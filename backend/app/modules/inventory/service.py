from datetime import UTC, date, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.transactions import transactional

from app.modules.inventory.models import (
    InventoryLot,
    InventoryLotPrice,
    InventoryMovement,
    Product,
    ProductPresentation,
)
from app.modules.inventory.schemas import (
    ExpiredLotsRetirementRequest,
    ExpiredLotsRetirementResult,
    ExpiringLotAlert,
    InventoryMovementRead,
    LotPresentationPriceRead,
    PickListItem,
    ProductCreate,
    ProductRead,
    StagnantLotAlert,
    StockLossCreate,
    StockTransfer,
)


def list_products(
    db: Session, search: str | None = None, active: bool | None = True
) -> list[ProductRead]:
    statement = select(Product).order_by(Product.name.asc())
    if active is not None:
        statement = statement.where(Product.active == active)
    if search:
        pattern = f"%{search.lower()}%"
        statement = statement.where(
            Product.name.ilike(pattern)
            | Product.sku.ilike(pattern)
            | Product.barcode.ilike(pattern)
        )

    products = list(db.scalars(statement))
    if not products:
        return []

    product_ids = [product.id for product in products]
    presentations = list(
        db.scalars(
            select(ProductPresentation)
            .where(ProductPresentation.product_id.in_(product_ids), ProductPresentation.active)
            .order_by(ProductPresentation.created_at.asc())
        )
    )
    presentations_by_product: dict[str, list[ProductPresentation]] = {}
    for presentation in presentations:
        presentations_by_product.setdefault(presentation.product_id, []).append(presentation)

    lots = list(
        db.scalars(
            select(InventoryLot)
            .where(InventoryLot.product_id.in_(product_ids))
            .order_by(InventoryLot.expires_at.asc().nulls_last(), InventoryLot.created_at.asc())
        )
    )
    lots_by_product: dict[str, list[InventoryLot]] = {}
    for lot in lots:
        lots_by_product.setdefault(lot.product_id, []).append(lot)

    lot_ids = [lot.id for lot in lots]
    prices = _list_lot_prices(db, lot_ids, presentations)
    prices_by_lot: dict[str, list[LotPresentationPriceRead]] = {}
    for price in prices:
        prices_by_lot.setdefault(price.lot_id, []).append(price)

    return [
        _build_product_read(
            product,
            presentations_by_product.get(product.id, []),
            lots_by_product.get(product.id, []),
            prices_by_lot,
        )
        for product in products
    ]


@transactional
def create_product(db: Session, payload: ProductCreate) -> ProductRead:
    product = Product(
        name=payload.name,
        sku=payload.sku,
        barcode=payload.barcode,
        description=payload.description,
        base_unit_name=payload.base_unit_name,
        laboratory_name=payload.laboratory_name,
        supplier_name=payload.supplier_name,
        units_per_blister=payload.units_per_blister,
        blisters_per_box=payload.blisters_per_box,
        unit_price=payload.unit_price,
        blister_price=payload.blister_price,
        box_price=payload.box_price,
        min_stock_units=payload.min_stock_units,
    )
    db.add(product)
    db.flush()

    presentations = _build_presentations(product.id, payload)
    for presentation in presentations:
        db.add(presentation)
    db.flush()

    lots: list[InventoryLot] = []
    lot_prices_by_lot: dict[str, list[LotPresentationPriceRead]] = {}
    if payload.lot is not None:
        lot = InventoryLot(
            product_id=product.id,
            lot_number=payload.lot.lot_number,
            lot_barcode=payload.lot.lot_barcode,
            shelf_location=payload.lot.shelf_location,
            expires_at=payload.lot.expires_at,
            purchase_unit_cost=payload.lot.purchase_unit_cost,
            warehouse_units=payload.lot.warehouse_units,
            store_units=payload.lot.store_units,
        )
        db.add(lot)
        db.flush()
        presentation_by_code = {
            presentation.code.lower(): presentation for presentation in presentations
        }
        raw_prices = payload.lot.presentation_prices or [
            {
                "presentation_code": presentation.code,
                "sale_price": presentation.default_price,
                "label_price": presentation.label_price or presentation.default_price,
            }
            for presentation in presentations
        ]
        for raw_price in raw_prices:
            presentation_code = (
                raw_price["presentation_code"]
                if isinstance(raw_price, dict)
                else raw_price.presentation_code
            ).lower()
            presentation = presentation_by_code.get(presentation_code)
            if presentation is None:
                continue
            sale_price = (
                raw_price["sale_price"] if isinstance(raw_price, dict) else raw_price.sale_price
            )
            label_price = (
                raw_price.get("label_price", sale_price)
                if isinstance(raw_price, dict)
                else raw_price.label_price
            )
            db.add(
                InventoryLotPrice(
                    lot_id=lot.id,
                    presentation_id=presentation.id,
                    sale_price=sale_price,
                    label_price=label_price or sale_price,
                )
            )
        lots.append(lot)

    # El commit lo maneja el decorador @transactional
    db.refresh(product)
    for presentation in presentations:
        db.refresh(presentation)
    for lot in lots:
        db.refresh(lot)
    if lots:
        prices = _list_lot_prices(db, [lot.id for lot in lots], presentations)
        for price in prices:
            lot_prices_by_lot.setdefault(price.lot_id, []).append(price)
    return _build_product_read(product, presentations, lots, lot_prices_by_lot)


def get_product(db: Session, product_id: str) -> Product | None:
    return db.get(Product, product_id)


@transactional
def transfer_to_store(db: Session, lot_id: str, payload: StockTransfer) -> InventoryLot | None:
    lot = db.get(InventoryLot, lot_id)
    if lot is None:
        return None
    if lot.warehouse_units < payload.units:
        raise ValueError("No hay suficiente existencia en bodega.")
    lot.warehouse_units -= payload.units
    lot.store_units += payload.units
    db.add(lot)
    db.add(
        InventoryMovement(
            lot_id=lot.id,
            product_id=lot.product_id,
            movement_type="transfer",
            from_location="warehouse",
            to_location="store",
            units=payload.units,
            reason="Traslado interno",
            note="Movimiento de bodega a tienda; no descuenta como venta.",
        )
    )
    # El commit lo maneja el decorador @transactional
    db.refresh(lot)
    return lot


@transactional
def register_stock_loss(db: Session, lot_id: str, payload: StockLossCreate) -> InventoryLot | None:
    lot = db.get(InventoryLot, lot_id)
    if lot is None:
        return None

    if payload.location == "warehouse":
        if lot.warehouse_units < payload.units:
            raise ValueError("No hay suficiente existencia en bodega para registrar la merma.")
        lot.warehouse_units -= payload.units
    else:
        if lot.store_units < payload.units:
            raise ValueError("No hay suficiente existencia en tienda para registrar la merma.")
        lot.store_units -= payload.units

    db.add(lot)
    db.add(
        InventoryMovement(
            lot_id=lot.id,
            product_id=lot.product_id,
            movement_type="loss",
            from_location=payload.location,
            to_location="loss",
            units=payload.units,
            reason=payload.reason,
            note=payload.note,
        )
    )
    # El commit lo maneja el decorador @transactional
    db.refresh(lot)
    return lot


@transactional
def retire_expired_lots(
    db: Session,
    payload: ExpiredLotsRetirementRequest,
) -> ExpiredLotsRetirementResult:
    today = date.today()
    lots = list(
        db.scalars(
            select(InventoryLot)
            .where(
                InventoryLot.expires_at.is_not(None),
                InventoryLot.expires_at < today,
                (InventoryLot.store_units > 0) | (InventoryLot.warehouse_units > 0),
            )
            .order_by(InventoryLot.expires_at.asc(), InventoryLot.created_at.asc())
        )
    )

    retired_lots = 0
    store_units = 0
    warehouse_units = 0
    for lot in lots:
        lot_had_stock = False
        if lot.store_units > 0:
            store_units += lot.store_units
            db.add(
                InventoryMovement(
                    lot_id=lot.id,
                    product_id=lot.product_id,
                    movement_type="loss",
                    from_location="store",
                    to_location="loss",
                    units=lot.store_units,
                    reason=payload.reason,
                    note=payload.note,
                )
            )
            lot.store_units = 0
            lot_had_stock = True
        if lot.warehouse_units > 0:
            warehouse_units += lot.warehouse_units
            db.add(
                InventoryMovement(
                    lot_id=lot.id,
                    product_id=lot.product_id,
                    movement_type="loss",
                    from_location="warehouse",
                    to_location="loss",
                    units=lot.warehouse_units,
                    reason=payload.reason,
                    note=payload.note,
                )
            )
            lot.warehouse_units = 0
            lot_had_stock = True
        if lot_had_stock:
            retired_lots += 1
            db.add(lot)

    # El commit lo maneja el decorador @transactional
    return ExpiredLotsRetirementResult(
        retired_lots=retired_lots,
        store_units=store_units,
        warehouse_units=warehouse_units,
        total_units=store_units + warehouse_units,
    )


def list_movements(
    db: Session, product_id: str | None = None, lot_id: str | None = None
) -> list[InventoryMovementRead]:
    statement = select(InventoryMovement).order_by(InventoryMovement.created_at.desc())
    if product_id:
        statement = statement.where(InventoryMovement.product_id == product_id)
    if lot_id:
        statement = statement.where(InventoryMovement.lot_id == lot_id)
    return list(db.scalars(statement.limit(100)))


def build_store_pick_list(db: Session, product_id: str, units: int) -> list[PickListItem]:
    product = db.get(Product, product_id)
    if product is None:
        return []
    remaining = units
    lots = list(
        db.scalars(
            select(InventoryLot)
            .where(
                InventoryLot.product_id == product_id,
                InventoryLot.warehouse_units > 0,
                _lot_is_usable(),
            )
            .order_by(InventoryLot.expires_at.asc().nulls_last(), InventoryLot.created_at.asc())
        )
    )
    result: list[PickListItem] = []
    for lot in lots:
        if remaining <= 0:
            break
        recommended = min(lot.warehouse_units, remaining)
        remaining -= recommended
        result.append(
            PickListItem(
                lot_id=lot.id,
                product_id=product.id,
                product_name=product.name,
                lot_number=lot.lot_number,
                shelf_location=lot.shelf_location,
                expires_at=lot.expires_at,
                recommended_units=recommended,
                warehouse_units=lot.warehouse_units,
                store_units=lot.store_units,
            )
        )
    return result


def _lot_is_usable():
    today = date.today()
    return or_(InventoryLot.expires_at.is_(None), InventoryLot.expires_at >= today)


def list_stagnant_lot_alerts(db: Session, days: int = 15) -> list[StagnantLotAlert]:
    threshold = datetime.now(UTC) - timedelta(days=days)
    products = {product.id: product for product in db.scalars(select(Product))}
    lots = list(db.scalars(select(InventoryLot).where(InventoryLot.store_units > 0)))
    alerts: list[StagnantLotAlert] = []
    for lot in lots:
        last_movement = db.scalar(
            select(InventoryMovement)
            .where(InventoryMovement.lot_id == lot.id, InventoryMovement.from_location == "store")
            .order_by(InventoryMovement.created_at.desc())
            .limit(1)
        )
        last_date = last_movement.created_at if last_movement is not None else lot.updated_at
        if last_date.tzinfo is None:
            last_date = last_date.replace(tzinfo=UTC)
        if last_date > threshold:
            continue
        days_without_movement = max((datetime.now(UTC) - last_date).days, 0)
        product = products.get(lot.product_id)
        if product is None:
            continue
        alerts.append(
            StagnantLotAlert(
                lot_id=lot.id,
                product_id=lot.product_id,
                product_name=product.name,
                lot_number=lot.lot_number,
                store_units=lot.store_units,
                days_without_movement=days_without_movement,
                message=f"Lote {lot.lot_number} lleva {days_without_movement} dias sin movimiento en tienda.",
            )
        )
    return alerts


def list_expiring_lot_alerts(db: Session, days: int = 30) -> list[ExpiringLotAlert]:
    today = date.today()
    limit = today + timedelta(days=days)
    products = {product.id: product for product in db.scalars(select(Product))}
    lots = list(
        db.scalars(
            select(InventoryLot)
            .where(
                InventoryLot.expires_at.is_not(None),
                InventoryLot.expires_at >= today,
                InventoryLot.expires_at <= limit,
            )
            .order_by(InventoryLot.expires_at.asc(), InventoryLot.created_at.asc())
        )
    )
    alerts: list[ExpiringLotAlert] = []
    for lot in lots:
        total_units = lot.warehouse_units + lot.store_units
        if total_units <= 0 or lot.expires_at is None:
            continue
        product = products.get(lot.product_id)
        if product is None:
            continue
        days_to_expire = max((lot.expires_at - today).days, 0)
        alerts.append(
            ExpiringLotAlert(
                lot_id=lot.id,
                product_id=lot.product_id,
                product_name=product.name,
                lot_number=lot.lot_number,
                shelf_location=lot.shelf_location,
                expires_at=lot.expires_at,
                warehouse_units=lot.warehouse_units,
                store_units=lot.store_units,
                total_units=total_units,
                days_to_expire=days_to_expire,
                message=(
                    f"{product.name} lote {lot.lot_number} vence en "
                    f"{days_to_expire} dias. Total: {total_units} unidades."
                ),
            )
        )
    return alerts


def _build_presentations(product_id: str, payload: ProductCreate) -> list[ProductPresentation]:
    if payload.presentations:
        return [
            ProductPresentation(
                product_id=product_id,
                code=presentation.code.lower(),
                name=presentation.name,
                units_per_sale=presentation.units_per_sale,
                default_price=presentation.default_price,
                label_price=presentation.label_price or presentation.default_price,
            )
            for presentation in payload.presentations
        ]

    return [
        ProductPresentation(
            product_id=product_id,
            code="unit",
            name=payload.base_unit_name,
            units_per_sale=1,
            default_price=payload.unit_price,
            label_price=payload.unit_price,
        ),
        ProductPresentation(
            product_id=product_id,
            code="blister",
            name="Blister",
            units_per_sale=payload.units_per_blister,
            default_price=payload.blister_price,
            label_price=payload.blister_price,
        ),
        ProductPresentation(
            product_id=product_id,
            code="box",
            name="Caja",
            units_per_sale=payload.units_per_blister * payload.blisters_per_box,
            default_price=payload.box_price,
            label_price=payload.box_price,
        ),
    ]


def _list_lot_prices(
    db: Session,
    lot_ids: list[str],
    presentations: list[ProductPresentation],
) -> list[LotPresentationPriceRead]:
    if not lot_ids:
        return []
    presentation_by_id = {presentation.id: presentation for presentation in presentations}
    prices = list(
        db.scalars(select(InventoryLotPrice).where(InventoryLotPrice.lot_id.in_(lot_ids)))
    )
    result: list[LotPresentationPriceRead] = []
    for price in prices:
        presentation = presentation_by_id.get(price.presentation_id)
        if presentation is None:
            continue
        result.append(
            LotPresentationPriceRead(
                id=price.id,
                lot_id=price.lot_id,
                presentation_id=price.presentation_id,
                presentation_code=presentation.code,
                presentation_name=presentation.name,
                sale_price=price.sale_price,
                label_price=price.label_price or price.sale_price,
                created_at=price.created_at,
                updated_at=price.updated_at,
            )
        )
    return result


def _build_product_read(
    product: Product,
    presentations: list[ProductPresentation],
    lots: list[InventoryLot],
    prices_by_lot: dict[str, list[LotPresentationPriceRead]],
) -> ProductRead:
    return ProductRead(
        id=product.id,
        name=product.name,
        sku=product.sku,
        barcode=product.barcode,
        description=product.description,
        base_unit_name=product.base_unit_name,
        laboratory_name=product.laboratory_name,
        supplier_name=product.supplier_name,
        units_per_blister=product.units_per_blister,
        blisters_per_box=product.blisters_per_box,
        unit_price=product.unit_price,
        blister_price=product.blister_price,
        box_price=product.box_price,
        min_stock_units=product.min_stock_units,
        active=product.active,
        total_warehouse_units=sum(lot.warehouse_units for lot in lots),
        total_store_units=sum(lot.store_units for lot in lots),
        presentations=presentations,
        lots=[
            {
                "id": lot.id,
                "product_id": lot.product_id,
                "lot_number": lot.lot_number,
                "lot_barcode": lot.lot_barcode,
                "shelf_location": lot.shelf_location,
                "expires_at": lot.expires_at,
                "purchase_unit_cost": lot.purchase_unit_cost,
                "warehouse_units": lot.warehouse_units,
                "store_units": lot.store_units,
                "created_at": lot.created_at,
                "updated_at": lot.updated_at,
                "presentation_prices": prices_by_lot.get(lot.id, []),
            }
            for lot in lots
        ],
        created_at=product.created_at,
        updated_at=product.updated_at,
    )
