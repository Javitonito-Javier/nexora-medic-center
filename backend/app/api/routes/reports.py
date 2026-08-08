from datetime import UTC, date, datetime, time

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.dashboard import DashboardSummary, read_dashboard_summary
from app.db.session import get_db
from app.modules.inventory.models import InventoryLot, Product
from app.modules.inventory.service import list_stagnant_lot_alerts
from app.modules.patients.models import Patient
from app.modules.pharmacy.models import (
    PharmacySale,
    PharmacySaleItem,
    PharmacySaleLotAllocation,
)
from app.modules.points.models import PointMovement
from app.modules.receipts.models import ClinicReceipt

router = APIRouter()


class SalesReportRow(BaseModel):
    period: str
    module: str
    cashier_name: str
    payment_method: str
    document_type: str
    documents_count: int
    subtotal: float
    discount: float
    total: float


class ClinicReceiptReportRow(BaseModel):
    period: str
    doctor_name: str
    service_description: str
    cashier_name: str
    payment_method: str
    document_type: str
    receipts_count: int
    subtotal: float
    discount: float
    total: float


class LotProfitReportRow(BaseModel):
    product_id: str
    product_name: str
    lot_id: str
    lot_number: str
    units: int
    revenue_total: float
    cost_total: float
    profit_total: float


class LowStockReportRow(BaseModel):
    product_id: str
    product_name: str
    sku: str
    min_stock_units: int
    store_units: int
    warehouse_units: int
    shortage_units: int


class ExpiringStockReportRow(BaseModel):
    product_id: str
    product_name: str
    lot_id: str
    lot_number: str
    expires_at: date
    days_to_expire: int
    store_units: int
    warehouse_units: int
    total_units: int
    shelf_location: str


class PointMovementReportRow(BaseModel):
    patient_id: str
    patient_name: str
    identity_number: str
    sale_id: str
    movement_type: str
    points: float
    balance_after: float
    note: str
    created_at: datetime


class TopProductReportRow(BaseModel):
    product_id: str
    product_name: str
    units_deducted: int
    quantity_sold: int
    revenue_total: float
    profit_total: float


class StagnantLotReportRow(BaseModel):
    product_id: str
    product_name: str
    lot_id: str
    lot_number: str
    store_units: int
    days_without_movement: int
    message: str


@router.get("/")
def list_reports() -> dict[str, object]:
    return {
        "module": "reports",
        "items": [
            "summary",
            "sales",
            "clinic-receipts",
            "profit-by-lot",
            "low-stock",
            "expiring-stock",
            "point-movements",
            "top-products",
            "stagnant-lots",
        ],
    }


@router.get("/summary", response_model=DashboardSummary)
def read_reports_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return read_dashboard_summary(db)


@router.get("/sales", response_model=list[SalesReportRow])
def read_sales_report(
    date_from: date | None = None,
    date_to: date | None = None,
    group_by: str = Query(default="day", pattern="^(day|month)$"),
    db: Session = Depends(get_db),
) -> list[SalesReportRow]:
    start, end = _date_range(date_from, date_to)
    rows: dict[tuple[str, str, str, str, str], SalesReportRow] = {}

    clinic_receipts = db.scalars(
        select(ClinicReceipt)
        .where(ClinicReceipt.created_at >= start)
        .where(ClinicReceipt.created_at <= end)
    )
    for receipt in clinic_receipts:
        key = _sales_key(
            created_at=receipt.created_at,
            group_by=group_by,
            module="clinic",
            cashier_name=receipt.cashier_name,
            payment_method=receipt.payment_method,
            document_type=receipt.document_type,
        )
        row = rows.setdefault(
            key,
            SalesReportRow(
                period=key[0],
                module=key[1],
                cashier_name=key[2],
                payment_method=key[3],
                document_type=key[4],
                documents_count=0,
                subtotal=0,
                discount=0,
                total=0,
            ),
        )
        _accumulate_sales_row(row, receipt.subtotal, receipt.discount, receipt.total)

    pharmacy_sales = db.scalars(
        select(PharmacySale)
        .where(PharmacySale.created_at >= start)
        .where(PharmacySale.created_at <= end)
        .where(PharmacySale.status == "active")
    )
    for sale in pharmacy_sales:
        key = _sales_key(
            created_at=sale.created_at,
            group_by=group_by,
            module="pharmacy",
            cashier_name=sale.cashier_name,
            payment_method=sale.payment_method,
            document_type=sale.document_type,
        )
        row = rows.setdefault(
            key,
            SalesReportRow(
                period=key[0],
                module=key[1],
                cashier_name=key[2],
                payment_method=key[3],
                document_type=key[4],
                documents_count=0,
                subtotal=0,
                discount=0,
                total=0,
            ),
        )
        _accumulate_sales_row(row, sale.subtotal, sale.discount, sale.total)

    return sorted(rows.values(), key=lambda item: (item.period, item.module, item.cashier_name))


@router.get("/clinic-receipts", response_model=list[ClinicReceiptReportRow])
def read_clinic_receipts_report(
    date_from: date | None = None,
    date_to: date | None = None,
    group_by: str = Query(default="day", pattern="^(day|month)$"),
    db: Session = Depends(get_db),
) -> list[ClinicReceiptReportRow]:
    start, end = _date_range(date_from, date_to)
    rows: dict[tuple[str, str, str, str, str, str], ClinicReceiptReportRow] = {}

    receipts = db.scalars(
        select(ClinicReceipt)
        .where(ClinicReceipt.created_at >= start)
        .where(ClinicReceipt.created_at <= end)
    )
    for receipt in receipts:
        key = (
            _period(receipt.created_at, group_by),
            receipt.doctor_name.strip() or "Sin doctor",
            receipt.description.strip() or "Servicio clinico",
            receipt.cashier_name.strip() or "Sin cajero",
            receipt.payment_method or "cash",
            receipt.document_type or "receipt",
        )
        row = rows.setdefault(
            key,
            ClinicReceiptReportRow(
                period=key[0],
                doctor_name=key[1],
                service_description=key[2],
                cashier_name=key[3],
                payment_method=key[4],
                document_type=key[5],
                receipts_count=0,
                subtotal=0,
                discount=0,
                total=0,
            ),
        )
        row.receipts_count += 1
        row.subtotal = round(row.subtotal + receipt.subtotal, 2)
        row.discount = round(row.discount + receipt.discount, 2)
        row.total = round(row.total + receipt.total, 2)

    return sorted(
        rows.values(),
        key=lambda item: (item.period, item.doctor_name, item.service_description),
    )


@router.get("/profit-by-lot", response_model=list[LotProfitReportRow])
def read_profit_by_lot_report(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> list[LotProfitReportRow]:
    start, end = _date_range(date_from, date_to)
    statement = (
        select(PharmacySaleLotAllocation, PharmacySaleItem, PharmacySale)
        .join(PharmacySaleItem, PharmacySaleLotAllocation.sale_item_id == PharmacySaleItem.id)
        .join(PharmacySale, PharmacySaleLotAllocation.sale_id == PharmacySale.id)
        .where(PharmacySale.created_at >= start)
        .where(PharmacySale.created_at <= end)
        .where(PharmacySale.status == "active")
    )
    rows: dict[tuple[str, str], LotProfitReportRow] = {}
    for allocation, item, _sale in db.execute(statement).all():
        key = (allocation.product_id, allocation.lot_id)
        row = rows.setdefault(
            key,
            LotProfitReportRow(
                product_id=allocation.product_id,
                product_name=item.product_name,
                lot_id=allocation.lot_id,
                lot_number=allocation.lot_number,
                units=0,
                revenue_total=0,
                cost_total=0,
                profit_total=0,
            ),
        )
        row.units += allocation.units
        row.revenue_total = round(row.revenue_total + allocation.revenue_total, 2)
        row.cost_total = round(row.cost_total + allocation.cost_total, 2)
        row.profit_total = round(row.profit_total + allocation.profit_total, 2)

    return sorted(rows.values(), key=lambda item: (item.product_name, item.lot_number))


@router.get("/inventory/low-stock", response_model=list[LowStockReportRow])
def read_low_stock_report(db: Session = Depends(get_db)) -> list[LowStockReportRow]:
    products = list(db.scalars(select(Product).where(Product.active.is_(True))))
    lots = list(db.scalars(select(InventoryLot)))
    lots_by_product: dict[str, list[InventoryLot]] = {}
    for lot in lots:
        lots_by_product.setdefault(lot.product_id, []).append(lot)

    rows: list[LowStockReportRow] = []
    for product in products:
        product_lots = lots_by_product.get(product.id, [])
        store_units = sum(lot.store_units for lot in product_lots)
        warehouse_units = sum(lot.warehouse_units for lot in product_lots)
        if store_units <= product.min_stock_units:
            rows.append(
                LowStockReportRow(
                    product_id=product.id,
                    product_name=product.name,
                    sku=product.sku,
                    min_stock_units=product.min_stock_units,
                    store_units=store_units,
                    warehouse_units=warehouse_units,
                    shortage_units=max(product.min_stock_units - store_units, 0),
                )
            )
    return sorted(rows, key=lambda item: (item.shortage_units * -1, item.product_name))


@router.get("/inventory/expiring-stock", response_model=list[ExpiringStockReportRow])
def read_expiring_stock_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> list[ExpiringStockReportRow]:
    today = date.today()
    limit = date.fromordinal(today.toordinal() + days)
    product_by_id = {product.id: product for product in db.scalars(select(Product))}
    lots = db.scalars(
        select(InventoryLot)
        .where(InventoryLot.expires_at.is_not(None))
        .where(InventoryLot.expires_at >= today)
        .where(InventoryLot.expires_at <= limit)
        .order_by(InventoryLot.expires_at.asc(), InventoryLot.created_at.asc())
    )

    rows: list[ExpiringStockReportRow] = []
    for lot in lots:
        total_units = lot.store_units + lot.warehouse_units
        if total_units <= 0 or lot.expires_at is None:
            continue
        product = product_by_id.get(lot.product_id)
        if product is None:
            continue
        rows.append(
            ExpiringStockReportRow(
                product_id=product.id,
                product_name=product.name,
                lot_id=lot.id,
                lot_number=lot.lot_number,
                expires_at=lot.expires_at,
                days_to_expire=max((lot.expires_at - today).days, 0),
                store_units=lot.store_units,
                warehouse_units=lot.warehouse_units,
                total_units=total_units,
                shelf_location=lot.shelf_location,
            )
        )
    return rows


@router.get("/points/movements", response_model=list[PointMovementReportRow])
def read_point_movements_report(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> list[PointMovementReportRow]:
    start, end = _date_range(date_from, date_to)
    statement = (
        select(PointMovement, Patient)
        .join(Patient, PointMovement.patient_id == Patient.id)
        .where(PointMovement.created_at >= start)
        .where(PointMovement.created_at <= end)
        .order_by(PointMovement.created_at.desc())
    )
    return [
        PointMovementReportRow(
            patient_id=patient.id,
            patient_name=patient.full_name,
            identity_number=patient.identity_number,
            sale_id=movement.sale_id,
            movement_type=movement.movement_type,
            points=movement.points,
            balance_after=movement.balance_after,
            note=movement.note,
            created_at=movement.created_at,
        )
        for movement, patient in db.execute(statement).all()
    ]


@router.get("/pharmacy/top-products", response_model=list[TopProductReportRow])
def read_top_products_report(
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[TopProductReportRow]:
    start, end = _date_range(date_from, date_to)
    statement = (
        select(PharmacySaleItem, PharmacySale)
        .join(PharmacySale, PharmacySaleItem.sale_id == PharmacySale.id)
        .where(PharmacySale.created_at >= start)
        .where(PharmacySale.created_at <= end)
        .where(PharmacySale.status == "active")
    )
    rows: dict[str, TopProductReportRow] = {}
    for item, _sale in db.execute(statement).all():
        row = rows.setdefault(
            item.product_id,
            TopProductReportRow(
                product_id=item.product_id,
                product_name=item.product_name,
                units_deducted=0,
                quantity_sold=0,
                revenue_total=0,
                profit_total=0,
            ),
        )
        row.units_deducted += item.units_deducted
        row.quantity_sold += item.quantity
        row.revenue_total = round(row.revenue_total + item.line_total, 2)
        row.profit_total = round(row.profit_total + item.profit_total, 2)

    return sorted(
        rows.values(),
        key=lambda item: (item.units_deducted * -1, item.revenue_total * -1, item.product_name),
    )[:limit]


@router.get("/inventory/stagnant-lots", response_model=list[StagnantLotReportRow])
def read_stagnant_lots_report(
    days: int = Query(default=15, ge=1, le=365),
    db: Session = Depends(get_db),
) -> list[StagnantLotReportRow]:
    alerts = list_stagnant_lot_alerts(db, days=days)
    return [
        StagnantLotReportRow(
            product_id=alert.product_id,
            product_name=alert.product_name,
            lot_id=alert.lot_id,
            lot_number=alert.lot_number,
            store_units=alert.store_units,
            days_without_movement=alert.days_without_movement,
            message=alert.message,
        )
        for alert in alerts
    ]


def _date_range(date_from: date | None, date_to: date | None) -> tuple[datetime, datetime]:
    today = datetime.now(UTC).date()
    start_date = date_from or date(today.year, today.month, 1)
    end_date = date_to or today
    return datetime.combine(start_date, time.min), datetime.combine(end_date, time.max)


def _period(created_at: datetime, group_by: str) -> str:
    if group_by == "month":
        return created_at.strftime("%Y-%m")
    return created_at.date().isoformat()


def _sales_key(
    *,
    created_at: datetime,
    group_by: str,
    module: str,
    cashier_name: str,
    payment_method: str,
    document_type: str,
) -> tuple[str, str, str, str, str]:
    return (
        _period(created_at, group_by),
        module,
        cashier_name.strip() or "Sin cajero",
        payment_method or "cash",
        document_type or "receipt",
    )


def _accumulate_sales_row(
    row: SalesReportRow,
    subtotal: float,
    discount: float,
    total: float,
) -> None:
    row.documents_count += 1
    row.subtotal = round(row.subtotal + subtotal, 2)
    row.discount = round(row.discount + discount, 2)
    row.total = round(row.total + total, 2)
