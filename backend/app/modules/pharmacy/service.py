from datetime import UTC, date, datetime, time

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.events import SaleCompletedEvent, publish_event
from app.core.exceptions import (
    ConflictError,
    InsufficientStockError,
    NotFoundError,
    ValidationError,
)
from app.core.transactions import transactional
from app.modules.business.service import (
    business_header_lines,
    ensure_invoice_allowed,
    fiscal_lines,
    footer_line,
)
from app.modules.inventory.models import (
    InventoryLot,
    InventoryLotPrice,
    InventoryMovement,
    Product,
    ProductPresentation,
)
from app.modules.patients.models import Patient
from app.modules.pharmacy.models import (
    PharmacySale,
    PharmacySaleItem,
    PharmacySaleLotAllocation,
)
from app.modules.pharmacy.schemas import (
    PharmacyCashSummary,
    PharmacyPaymentTotals,
    ReceiptText,
    SaleCreate,
    SaleRead,
)
from app.modules.points.service import earn_points, redeem_points


def list_sales(db: Session) -> list[SaleRead]:
    sales = list(db.scalars(select(PharmacySale).order_by(PharmacySale.created_at.desc())))
    if not sales:
        return []
    sale_ids = [sale.id for sale in sales]
    items = list(db.scalars(select(PharmacySaleItem).where(PharmacySaleItem.sale_id.in_(sale_ids))))
    allocations = list(
        db.scalars(
            select(PharmacySaleLotAllocation).where(PharmacySaleLotAllocation.sale_id.in_(sale_ids))
        )
    )
    items_by_sale: dict[str, list[PharmacySaleItem]] = {}
    for item in items:
        items_by_sale.setdefault(item.sale_id, []).append(item)
    allocations_by_sale: dict[str, list[PharmacySaleLotAllocation]] = {}
    for allocation in allocations:
        allocations_by_sale.setdefault(allocation.sale_id, []).append(allocation)
    return [
        _build_sale_read(sale, items_by_sale.get(sale.id, []), allocations_by_sale.get(sale.id, []))
        for sale in sales
    ]


def get_sale(db: Session, sale_id: str) -> SaleRead | None:
    sale = db.get(PharmacySale, sale_id)
    if sale is None:
        return None
    items = list(db.scalars(select(PharmacySaleItem).where(PharmacySaleItem.sale_id == sale.id)))
    allocations = list(
        db.scalars(
            select(PharmacySaleLotAllocation).where(PharmacySaleLotAllocation.sale_id == sale.id)
        )
    )
    return _build_sale_read(sale, items, allocations)


@transactional
def create_sale(db: Session, payload: SaleCreate) -> SaleRead:
    ensure_invoice_allowed(db, document_type=payload.document_type)
    _validate_payment_details(payload)
    patient = db.get(Patient, payload.patient_id) if payload.patient_id else None
    if payload.patient_id and patient is None:
        raise NotFoundError("Paciente/cliente", payload.patient_id)
    _validate_discount_prerequisites(payload, patient)

    sale = PharmacySale(
        patient_id=patient.id if patient is not None else None,
        customer_name=payload.customer_name or "Consumidor final",
        cashier_name=payload.cashier_name,
        document_type=payload.document_type,
        payment_method=payload.payment_method,
        payment_reference=payload.payment_reference,
        bank_name=payload.bank_name,
        discount=payload.discount,
        discount_type=payload.discount_type,
        discount_base_total=payload.discount_base_total,
        discount_evidence_note=payload.discount_evidence_note,
    )
    db.add(sale)
    db.flush()

    sale_items: list[PharmacySaleItem] = []
    sale_allocations: list[PharmacySaleLotAllocation] = []
    subtotal = 0.0
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if product is None or not product.active:
            raise NotFoundError("Producto", item.product_id)

        presentation = _resolve_presentation(db, product, item.presentation, item.presentation_id)
        if presentation is None:
            raise ValidationError("Presentacion no encontrada para el producto.", field="presentation")

        units = presentation.units_per_sale * item.quantity
        price, label_price = _presentation_prices_from_next_lot(
            db,
            product.id,
            presentation,
            lot_barcode=item.lot_barcode,
        )
        line_total = round(price * item.quantity, 2)
        label_line_total = round(label_price * item.quantity, 2)
        lot_deductions = _deduct_store_stock(db, product.id, units, lot_barcode=item.lot_barcode)

        sale_item = PharmacySaleItem(
            sale_id=sale.id,
            product_id=product.id,
            product_name=product.name,
            presentation=presentation.name,
            quantity=item.quantity,
            units_deducted=units,
            unit_price=price,
            line_total=line_total,
            label_unit_price=label_price,
            label_line_total=label_line_total,
        )
        db.add(sale_item)
        db.flush()

        sale_unit_value = price / presentation.units_per_sale
        item_cost_total = 0.0
        item_profit_total = 0.0
        for lot, deducted_units in lot_deductions:
            cost_total = round(lot.purchase_unit_cost * deducted_units, 2)
            revenue_total = round(sale_unit_value * deducted_units, 2)
            profit_total = round(revenue_total - cost_total, 2)
            allocation = PharmacySaleLotAllocation(
                sale_id=sale.id,
                sale_item_id=sale_item.id,
                product_id=product.id,
                lot_id=lot.id,
                lot_number=lot.lot_number,
                units=deducted_units,
                purchase_unit_cost=lot.purchase_unit_cost,
                sale_unit_value=round(sale_unit_value, 4),
                cost_total=cost_total,
                revenue_total=revenue_total,
                profit_total=profit_total,
            )
            db.add(allocation)
            sale_allocations.append(allocation)
            item_cost_total += cost_total
            item_profit_total += profit_total
        sale_item.cost_total = round(item_cost_total, 2)
        sale_item.profit_total = round(item_profit_total, 2)
        db.add(sale_item)
        sale_items.append(sale_item)
        subtotal += line_total

    sale.subtotal = round(subtotal, 2)
    label_subtotal = round(sum(item.label_line_total for item in sale_items), 2)
    _validate_discount_amount(payload, patient, sale.subtotal, label_subtotal)
    sale.discount = round(payload.discount, 2)
    if patient is not None and payload.discount_type == "points":
        redeemed = redeem_points(db, patient, sale.id, sale.discount)
        sale.discount = min(redeemed, sale.subtotal)
    sale.total = round(sale.subtotal - sale.discount, 2)
    if patient is not None and payload.discount_type != "points":
        earn_points(db, patient, sale.id, sale.total)
    db.add(sale)
    # El commit y rollback los maneja el decorador @transactional
    db.refresh(sale)
    for item in sale_items:
        db.refresh(item)
    for allocation in sale_allocations:
        db.refresh(allocation)
    
    # PUBLICAR EVENTO: Venta completada exitosamente
    # Esto dispara auditoría automática y futuras notificaciones
    publish_event(
        SaleCompletedEvent(
            aggregate_id=str(sale.id),
            sale_id=str(sale.id),
            total_amount=sale.total,
            patient_id=str(patient.id) if patient else None,
            items_count=len(sale_items)
        )
    )
    
    return _build_sale_read(sale, sale_items, sale_allocations)


def _validate_payment_details(payload: SaleCreate) -> None:
    if payload.payment_method in {"card", "transfer"} and not payload.payment_reference.strip():
        raise ValidationError("Agrega el codigo de comprobante del pago.", field="payment_reference")
    if payload.payment_method == "transfer" and not payload.bank_name.strip():
        raise ValidationError("Selecciona el banco de la transferencia.", field="bank_name")


def _validate_discount_prerequisites(payload: SaleCreate, patient: Patient | None) -> None:
    allowed_discount_types = {"none", "general", "third_age", "fourth_age", "points"}
    if payload.discount_type not in allowed_discount_types:
        raise ValidationError("Tipo de descuento no valido.", field="discount_type")
    if payload.discount <= 0:
        return
    if payload.discount_type == "none":
        raise ConflictError("Selecciona el tipo de descuento.")
    if payload.discount_type == "points" and patient is None:
        raise ValidationError("Selecciona un cliente para redimir puntos.", field="patient_id")
    if payload.discount_type in {"third_age", "fourth_age"} and patient is None:
        raise ValidationError("Selecciona un cliente para aplicar descuento por edad.", field="patient_id")
    if payload.discount_type == "third_age" and patient is not None and _patient_age(patient) < 60:
        raise ValidationError("El cliente no califica para descuento de tercera edad.", field="discount_type")
    if payload.discount_type == "fourth_age":
        if patient is not None and _patient_age(patient) < 80:
            raise ValidationError("El cliente no califica para descuento de cuarta edad.", field="discount_type")
        if not payload.discount_evidence_note.strip():
            raise ValidationError("Agrega evidencia de receta/DNI para cuarta edad.", field="discount_evidence_note")


def _validate_discount_amount(
    payload: SaleCreate,
    patient: Patient | None,
    subtotal: float,
    label_subtotal: float,
) -> None:
    discount = round(payload.discount, 2)
    if discount < 0:
        raise ValidationError("El descuento debe ser mayor o igual a cero.", field="discount")
    if discount > subtotal:
        raise ValidationError("El descuento no puede superar el subtotal.", field="discount")
    if discount <= 0:
        return

    if payload.discount_type == "points" and patient is not None:
        if patient.available_points < 50:
            raise ValidationError("El cliente necesita al menos L 50.00 en puntos para redimir.", field="discount")
        if discount > patient.available_points:
            raise ValidationError("El descuento por puntos supera el saldo disponible.", field="discount")

    if payload.discount_type in {"third_age", "fourth_age"}:
        rate = 0.25 if payload.discount_type == "third_age" else 0.35
        max_discount = _legal_discount_from_label(subtotal, label_subtotal, rate)
        if discount > max_discount:
            label = "tercera edad" if payload.discount_type == "third_age" else "cuarta edad"
            raise ValidationError(
                f"El descuento de {label} no puede superar L {max_discount:.2f}.",
                field="discount"
            )


def _patient_age(patient: Patient) -> int:
    today = date.today()
    years = today.year - patient.birth_date.year
    if (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day):
        years -= 1
    return years


def _legal_discount_from_label(subtotal: float, label_subtotal: float, rate: float) -> float:
    if subtotal <= 0 or label_subtotal <= 0:
        return 0
    legal_total = label_subtotal * (1 - rate)
    return round(min(max(subtotal - legal_total, 0), subtotal), 2)


def summarize_pharmacy_cash(
    db: Session,
    summary_date: date,
    cashier_name: str | None = None,
) -> PharmacyCashSummary:
    start = datetime.combine(summary_date, time.min, tzinfo=UTC)
    end = datetime.combine(summary_date, time.max, tzinfo=UTC)
    statement = select(PharmacySale).where(
        PharmacySale.created_at >= start,
        PharmacySale.created_at <= end,
        PharmacySale.status == "active",
    )
    if cashier_name:
        statement = statement.where(PharmacySale.cashier_name == cashier_name)

    sales = list(db.scalars(statement))
    payment_totals = {"cash": 0.0, "card": 0.0, "transfer": 0.0}
    for sale in sales:
        payment_totals[sale.payment_method] = (
            payment_totals.get(sale.payment_method, 0.0) + sale.total
        )
    sale_ids = [sale.id for sale in sales]
    items = (
        list(db.scalars(select(PharmacySaleItem).where(PharmacySaleItem.sale_id.in_(sale_ids))))
        if sale_ids
        else []
    )

    return PharmacyCashSummary(
        date=summary_date.isoformat(),
        cashier_name=cashier_name,
        sales_count=len(sales),
        subtotal=round(sum(sale.subtotal for sale in sales), 2),
        discount=round(sum(sale.discount for sale in sales), 2),
        total=round(sum(sale.total for sale in sales), 2),
        cost_total=round(sum(item.cost_total for item in items), 2),
        profit_total=round(sum(item.profit_total for item in items), 2),
        by_payment_method=PharmacyPaymentTotals(
            cash=round(payment_totals.get("cash", 0), 2),
            card=round(payment_totals.get("card", 0), 2),
            transfer=round(payment_totals.get("transfer", 0), 2),
        ),
    )


def build_receipt_text(db: Session, sale_id: str) -> ReceiptText | None:
    sale = db.get(PharmacySale, sale_id)
    if sale is None:
        return None
    items = list(db.scalars(select(PharmacySaleItem).where(PharmacySaleItem.sale_id == sale.id)))
    created = sale.created_at.strftime("%Y%m%d_%H%M")
    lines = [
        *business_header_lines(db),
        "Farmacia",
        f"{'FACTURA' if sale.document_type == 'invoice' else 'RECIBO'}: {sale.id[:8].upper()}",
        f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}",
        f"Cajero: {sale.cashier_name or 'N/A'}",
        f"Cliente: {sale.customer_name}",
        "-" * 32,
    ]
    sar_lines = fiscal_lines(db, document_type=sale.document_type)
    if sar_lines:
        lines.extend([*sar_lines, "-" * 32])
    for item in items:
        lines.extend(
            [
                item.product_name[:32],
                f"{item.quantity} x {item.presentation} @ L {item.unit_price:.2f}",
                f"Subtotal linea: L {item.line_total:.2f}",
            ]
        )
    lines.extend(
        [
            "-" * 32,
            f"Subtotal: L {sale.subtotal:.2f}",
            f"Base vineta: L {sale.discount_base_total:.2f}",
            f"Tipo descuento: {sale.discount_type}",
            f"Descuento: L {sale.discount:.2f}",
            f"Evidencia: {sale.discount_evidence_note or 'N/A'}",
            f"Total: L {sale.total:.2f}",
            f"Pago: {sale.payment_method}",
            f"Banco: {sale.bank_name or 'N/A'}",
            f"Comprobante: {sale.payment_reference or 'N/A'}",
            "",
            footer_line(db, document_type=sale.document_type),
        ]
    )
    safe_customer = "".join(
        char
        for char in sale.customer_name.lower().replace(" ", "_")
        if char.isalnum() or char == "_"
    )
    return ReceiptText(
        sale_id=sale.id,
        filename=f"recibo_{safe_customer or 'consumidor_final'}_{created}.txt",
        content="\n".join(lines),
    )


def _resolve_presentation(
    db: Session,
    product: Product,
    presentation_code: str,
    presentation_id: str | None,
) -> ProductPresentation | None:
    statement = select(ProductPresentation).where(
        ProductPresentation.product_id == product.id,
        ProductPresentation.active,
    )
    if presentation_id:
        presentation = db.scalar(statement.where(ProductPresentation.id == presentation_id))
        if presentation is not None:
            return presentation

    presentation = db.scalar(statement.where(ProductPresentation.code == presentation_code))
    if presentation is not None:
        return presentation

    fallback_units = 1
    fallback_price = product.unit_price
    fallback_name = product.base_unit_name
    if presentation_code == "box":
        fallback_units = product.units_per_blister * product.blisters_per_box
        fallback_price = product.box_price
        fallback_name = "Caja"
    elif presentation_code == "blister":
        fallback_units = product.units_per_blister
        fallback_price = product.blister_price
        fallback_name = "Blister"

    presentation = ProductPresentation(
        product_id=product.id,
        code=presentation_code,
        name=fallback_name,
        units_per_sale=fallback_units,
        default_price=fallback_price,
        label_price=fallback_price,
    )
    db.add(presentation)
    db.flush()
    return presentation


def _presentation_prices_from_next_lot(
    db: Session,
    product_id: str,
    presentation: ProductPresentation,
    lot_barcode: str | None = None,
) -> tuple[float, float]:
    statement = select(InventoryLot).where(
        InventoryLot.product_id == product_id,
        InventoryLot.store_units > 0,
        _lot_is_sellable(),
    )
    if lot_barcode:
        statement = statement.where(InventoryLot.lot_barcode == lot_barcode)
    lot = db.scalar(
        statement.order_by(
            InventoryLot.expires_at.asc().nulls_last(), InventoryLot.created_at.asc()
        ).limit(1)
    )
    if lot is None:
        label_price = presentation.label_price or presentation.default_price
        return presentation.default_price, label_price

    lot_price = db.scalar(
        select(InventoryLotPrice).where(
            InventoryLotPrice.lot_id == lot.id,
            InventoryLotPrice.presentation_id == presentation.id,
        )
    )
    if lot_price is None:
        label_price = presentation.label_price or presentation.default_price
        return presentation.default_price, label_price
    return lot_price.sale_price, lot_price.label_price or lot_price.sale_price


def _deduct_store_stock(
    db: Session,
    product_id: str,
    units: int,
    lot_barcode: str | None = None,
) -> list[tuple[InventoryLot, int]]:
    remaining = units
    statement = select(InventoryLot).where(
        InventoryLot.product_id == product_id,
        InventoryLot.store_units > 0,
        _lot_is_sellable(),
    )
    if lot_barcode:
        statement = statement.where(InventoryLot.lot_barcode == lot_barcode)
    lots = list(
        db.scalars(
            statement.order_by(
                InventoryLot.expires_at.asc().nulls_last(), InventoryLot.created_at.asc()
            )
        )
    )
    if sum(lot.store_units for lot in lots) < units:
        message = "No hay suficiente existencia vigente en tienda para completar la venta."
        if lot_barcode:
            message = "El lote escaneado no tiene existencia vigente suficiente en tienda."
        raise InsufficientStockError(
            product_name="Producto",
            requested=units,
            available=sum(lot.store_units for lot in lots)
        )

    deductions: list[tuple[InventoryLot, int]] = []
    for lot in lots:
        if remaining <= 0:
            break
        deducted = min(lot.store_units, remaining)
        lot.store_units -= deducted
        remaining -= deducted
        deductions.append((lot, deducted))
        db.add(
            InventoryMovement(
                lot_id=lot.id,
                product_id=product_id,
                movement_type="sale",
                from_location="store",
                to_location="customer",
                units=deducted,
                reason="Venta farmacia",
                note="Salida automatica por POS usando FEFO/FIFO sin lotes vencidos.",
            )
        )
        db.add(lot)
    return deductions


def _lot_is_sellable():
    today = date.today()
    return or_(InventoryLot.expires_at.is_(None), InventoryLot.expires_at >= today)


def _build_sale_read(
    sale: PharmacySale,
    items: list[PharmacySaleItem],
    allocations: list[PharmacySaleLotAllocation] | None = None,
) -> SaleRead:
    allocations = allocations or []
    allocations_by_item: dict[str, list[PharmacySaleLotAllocation]] = {}
    for allocation in allocations:
        allocations_by_item.setdefault(allocation.sale_item_id, []).append(allocation)
    return SaleRead(
        id=sale.id,
        patient_id=sale.patient_id or "",
        customer_name=sale.customer_name,
        cashier_name=sale.cashier_name,
        document_type=sale.document_type,
        payment_method=sale.payment_method,
        payment_reference=sale.payment_reference,
        bank_name=sale.bank_name,
        status=sale.status,
        subtotal=sale.subtotal,
        discount=sale.discount,
        discount_type=sale.discount_type,
        discount_base_total=sale.discount_base_total,
        discount_evidence_note=sale.discount_evidence_note,
        total=sale.total,
        cost_total=round(sum(item.cost_total for item in items), 2),
        profit_total=round(sum(item.profit_total for item in items), 2),
        created_at=sale.created_at,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "presentation": item.presentation,
                "quantity": item.quantity,
                "units_deducted": item.units_deducted,
                "unit_price": item.unit_price,
                "line_total": item.line_total,
                "label_unit_price": item.label_unit_price,
                "label_line_total": item.label_line_total,
                "cost_total": item.cost_total,
                "profit_total": item.profit_total,
                "allocations": allocations_by_item.get(item.id, []),
            }
            for item in items
        ],
    )
