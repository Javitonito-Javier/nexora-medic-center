from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments.models import Appointment
from app.modules.consultations.models import Consultation
from app.modules.inventory.models import InventoryLot, InventoryMovement, Product
from app.modules.licensing.service import get_license_status
from app.modules.pharmacy.models import PharmacySale, PharmacySaleItem
from app.modules.receipts.models import ClinicReceipt

router = APIRouter()


class DashboardMetric(BaseModel):
    title: str
    value: str
    icon: str


class DashboardAlert(BaseModel):
    title: str
    message: str
    severity: str = "info"


class DashboardChartPoint(BaseModel):
    label: str
    value: float
    secondary_value: float = 0


class DashboardChart(BaseModel):
    title: str
    chart_type: str
    primary_label: str = ""
    secondary_label: str = ""
    points: list[DashboardChartPoint]


class DashboardSummary(BaseModel):
    metrics: list[DashboardMetric]
    alerts: list[DashboardAlert]
    charts: list[DashboardChart] = []


@router.get("/")
def list_dashboard() -> dict[str, object]:
    return {"module": "dashboard", "items": ["summary"]}


@router.get("/summary", response_model=DashboardSummary)
def read_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    today = datetime.now(UTC).date()
    today_start = datetime.combine(today, time.min, tzinfo=UTC)
    today_end = datetime.combine(today, time.max, tzinfo=UTC)
    month_start = datetime(today.year, today.month, 1, tzinfo=UTC)
    week_start = today_start - timedelta(days=6)
    next_two_days = today_end + timedelta(days=2)

    today_appointments = list(
        db.scalars(
            select(Appointment).where(
                Appointment.scheduled_at >= today_start,
                Appointment.scheduled_at <= today_end,
            )
        )
    )
    pending_today = [
        appointment
        for appointment in today_appointments
        if appointment.status in {"scheduled", "pending"}
    ]
    upcoming_appointments = list(
        db.scalars(
            select(Appointment).where(
                Appointment.scheduled_at > today_end,
                Appointment.scheduled_at <= next_two_days,
                Appointment.status.in_(["scheduled", "pending"]),
            )
        )
    )

    today_consultations = list(
        db.scalars(
            select(Consultation).where(
                Consultation.date >= today_start,
                Consultation.date <= today_end,
            )
        )
    )

    pharmacy_today = _sales_between(db, today_start, today_end)
    pharmacy_month = _sales_between(db, month_start, today_end)
    pharmacy_week = _sales_between(db, week_start, today_end)
    month_items = _sale_items_for_sales(db, pharmacy_month)
    clinic_today = _clinic_receipts_between(db, today_start, today_end)
    clinic_month = _clinic_receipts_between(db, month_start, today_end)
    clinic_week = _clinic_receipts_between(db, week_start, today_end)

    products = list(db.scalars(select(Product).where(Product.active)))
    lots = list(db.scalars(select(InventoryLot)))
    product_by_id = {product.id: product for product in products}
    low_stock_count = _low_stock_count(products, lots)
    expiring_lots = _expiring_lots(product_by_id, lots, today, days=30)
    stagnant_alerts = _stagnant_alerts(db, products, lots, days=15)

    metrics = [
        DashboardMetric(title="Citas de hoy", value=str(len(today_appointments)), icon="event"),
        DashboardMetric(title="Pendientes hoy", value=str(len(pending_today)), icon="groups"),
        DashboardMetric(
            title="Consultas registradas hoy", value=str(len(today_consultations)), icon="medical"
        ),
        DashboardMetric(
            title="Consultas pagadas hoy",
            value=_money(sum(receipt.total for receipt in clinic_today)),
            icon="clinic_payment",
        ),
        DashboardMetric(
            title="Consultas pagadas mes",
            value=_money(sum(receipt.total for receipt in clinic_month)),
            icon="clinic_payment",
        ),
        DashboardMetric(
            title="Ventas farmacia hoy",
            value=_money(sum(sale.total for sale in pharmacy_today)),
            icon="pos",
        ),
        DashboardMetric(
            title="Ventas farmacia mes",
            value=_money(sum(sale.total for sale in pharmacy_month)),
            icon="pharmacy",
        ),
        DashboardMetric(
            title="Utilidad farmacia mes",
            value=_money(sum(item.profit_total for item in month_items)),
            icon="profit",
        ),
        DashboardMetric(title="Bajo stock", value=str(low_stock_count), icon="stock"),
        DashboardMetric(title="Lotes por vencer", value=str(len(expiring_lots)), icon="warning"),
    ]

    alerts: list[DashboardAlert] = []
    license_status = get_license_status(db, update_check=False)
    if license_status.enforcement_enabled and license_status.status != "active":
        alerts.append(
            DashboardAlert(
                title="Licencia del sistema",
                message=license_status.message,
                severity="warning" if license_status.can_write else "critical",
            )
        )
    elif (
        license_status.enforcement_enabled
        and license_status.days_remaining is not None
        and license_status.days_remaining <= 7
    ):
        alerts.append(
            DashboardAlert(
                title="Licencia por vencer",
                message=license_status.message,
                severity="warning",
            )
        )
    for appointment in upcoming_appointments[:5]:
        alerts.append(
            DashboardAlert(
                title="Cita proxima",
                message=f"{appointment.scheduled_at.strftime('%d/%m %H:%M')} - {appointment.reason or 'Consulta'}",
                severity="info",
            )
        )
    for product, lot in expiring_lots[:5]:
        expires = lot.expires_at.strftime("%d/%m/%Y") if lot.expires_at else "N/A"
        alerts.append(
            DashboardAlert(
                title="Lote por vencer",
                message=f"{product.name} lote {lot.lot_number} vence {expires}. Tienda: {lot.store_units}, bodega: {lot.warehouse_units}.",
                severity="warning",
            )
        )
    for product in products:
        total_store = sum(lot.store_units for lot in lots if lot.product_id == product.id)
        if total_store <= product.min_stock_units:
            alerts.append(
                DashboardAlert(
                    title="Bajo stock",
                    message=f"{product.name}: {total_store} unidades en tienda. Minimo: {product.min_stock_units}.",
                    severity="warning",
                )
            )
    alerts.extend(stagnant_alerts[:5])
    if not alerts:
        alerts.append(
            DashboardAlert(
                title="Todo tranquilo",
                message="No hay alertas criticas para mostrar.",
                severity="ok",
            )
        )

    charts = [
        DashboardChart(
            title="Ingresos ultimos 7 dias",
            chart_type="grouped_bar",
            primary_label="Farmacia",
            secondary_label="Clinica",
            points=_weekly_income_points(today, pharmacy_week, clinic_week),
        ),
        DashboardChart(
            title="Pagos del mes",
            chart_type="donut",
            points=_payment_method_points(pharmacy_month, clinic_month),
        ),
        DashboardChart(
            title="Productos mas vendidos del mes",
            chart_type="horizontal_bar",
            primary_label="Unidades",
            points=_top_product_points(month_items),
        ),
    ]

    return DashboardSummary(metrics=metrics, alerts=alerts[:12], charts=charts)


def _sales_between(db: Session, start: datetime, end: datetime) -> list[PharmacySale]:
    return list(
        db.scalars(
            select(PharmacySale).where(
                PharmacySale.created_at >= start,
                PharmacySale.created_at <= end,
                PharmacySale.status == "active",
            )
        )
    )


def _sale_items_for_sales(db: Session, sales: list[PharmacySale]) -> list[PharmacySaleItem]:
    sale_ids = [sale.id for sale in sales]
    if not sale_ids:
        return []
    return list(db.scalars(select(PharmacySaleItem).where(PharmacySaleItem.sale_id.in_(sale_ids))))


def _clinic_receipts_between(db: Session, start: datetime, end: datetime) -> list[ClinicReceipt]:
    return list(
        db.scalars(
            select(ClinicReceipt).where(
                ClinicReceipt.created_at >= start,
                ClinicReceipt.created_at <= end,
            )
        )
    )


def _weekly_income_points(
    today: date,
    pharmacy_sales: list[PharmacySale],
    clinic_receipts: list[ClinicReceipt],
) -> list[DashboardChartPoint]:
    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    points: list[DashboardChartPoint] = []
    for day in days:
        pharmacy_total = sum(sale.total for sale in pharmacy_sales if sale.created_at.date() == day)
        clinic_total = sum(
            receipt.total for receipt in clinic_receipts if receipt.created_at.date() == day
        )
        points.append(
            DashboardChartPoint(
                label=day.strftime("%d/%m"),
                value=round(pharmacy_total, 2),
                secondary_value=round(clinic_total, 2),
            )
        )
    return points


def _payment_method_points(
    pharmacy_sales: list[PharmacySale],
    clinic_receipts: list[ClinicReceipt],
) -> list[DashboardChartPoint]:
    labels = {"cash": "Efectivo", "card": "Tarjeta", "transfer": "Transferencia"}
    totals = dict.fromkeys(labels, 0.0)
    for sale in pharmacy_sales:
        totals[sale.payment_method] = totals.get(sale.payment_method, 0.0) + sale.total
    for receipt in clinic_receipts:
        totals[receipt.payment_method] = totals.get(receipt.payment_method, 0.0) + receipt.total
    return [
        DashboardChartPoint(label=labels[key], value=round(value, 2))
        for key, value in totals.items()
        if value > 0
    ]


def _top_product_points(items: list[PharmacySaleItem], limit: int = 5) -> list[DashboardChartPoint]:
    totals: dict[str, float] = {}
    for item in items:
        totals[item.product_name] = totals.get(item.product_name, 0) + item.units_deducted
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [
        DashboardChartPoint(label=name, value=round(units, 2)) for name, units in ranked[:limit]
    ]


def _low_stock_count(products: list[Product], lots: list[InventoryLot]) -> int:
    count = 0
    for product in products:
        total_store = sum(lot.store_units for lot in lots if lot.product_id == product.id)
        if total_store <= product.min_stock_units:
            count += 1
    return count


def _expiring_lots(
    product_by_id: dict[str, Product],
    lots: list[InventoryLot],
    today: date,
    days: int,
) -> list[tuple[Product, InventoryLot]]:
    limit = today + timedelta(days=days)
    result: list[tuple[Product, InventoryLot]] = []
    for lot in lots:
        if lot.expires_at is None or lot.expires_at < today or lot.expires_at > limit:
            continue
        if lot.store_units + lot.warehouse_units <= 0:
            continue
        product = product_by_id.get(lot.product_id)
        if product is not None:
            result.append((product, lot))
    return sorted(result, key=lambda item: (item[1].expires_at or date.max, item[1].created_at))


def _stagnant_alerts(
    db: Session,
    products: list[Product],
    lots: list[InventoryLot],
    days: int,
) -> list[DashboardAlert]:
    threshold = datetime.now(UTC) - timedelta(days=days)
    product_by_id = {product.id: product for product in products}
    alerts: list[DashboardAlert] = []
    for lot in lots:
        if lot.store_units <= 0:
            continue
        last_movement = db.scalar(
            select(InventoryMovement)
            .where(InventoryMovement.lot_id == lot.id, InventoryMovement.from_location == "store")
            .order_by(InventoryMovement.created_at.desc())
            .limit(1)
        )
        last_date = last_movement.created_at if last_movement is not None else lot.updated_at
        if last_date > threshold:
            continue
        product = product_by_id.get(lot.product_id)
        if product is None:
            continue
        alerts.append(
            DashboardAlert(
                title="Lote estancado",
                message=f"{product.name} lote {lot.lot_number} lleva {(datetime.now(UTC) - last_date).days} dias sin movimiento.",
                severity="warning",
            )
        )
    return alerts


def _money(value: float) -> str:
    return f"L {value:.2f}"
