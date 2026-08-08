from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.inventory.models import InventoryLot
from app.modules.inventory.schemas import (
    ExpiredLotsRetirementRequest,
    ExpiredLotsRetirementResult,
    ExpiringLotAlert,
    InventoryLotRead,
    InventoryMovementRead,
    PickListItem,
    ProductCreate,
    ProductRead,
    StagnantLotAlert,
    StockLossCreate,
    StockTransfer,
)
from app.modules.inventory.service import (
    build_store_pick_list,
    create_product,
    list_expiring_lot_alerts,
    list_movements,
    list_products,
    list_stagnant_lot_alerts,
    register_stock_loss,
    retire_expired_lots,
    transfer_to_store,
)
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
def read_products(
    search: str | None = Query(default=None),
    active: bool | None = Query(default=True),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return list_products(db, search=search, active=active)


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> ProductRead:
    product = create_product(db, payload)
    record_audit_event(
        db,
        module="inventory",
        action="create_product",
        entity_type="product",
        entity_id=product.id,
        summary=f"Producto creado: {product.name}.",
        actor=current_user,
        after_data=payload.model_dump(),
    )
    return product


@router.get("/movements", response_model=list[InventoryMovementRead])
def read_movements(
    product_id: str | None = Query(default=None),
    lot_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[InventoryMovementRead]:
    return list_movements(db, product_id=product_id, lot_id=lot_id)


@router.get("/pick-list", response_model=list[PickListItem])
def read_pick_list(
    product_id: str = Query(),
    units: int = Query(gt=0),
    db: Session = Depends(get_db),
) -> list[PickListItem]:
    return build_store_pick_list(db, product_id=product_id, units=units)


@router.get("/alerts/stagnant-lots", response_model=list[StagnantLotAlert])
def read_stagnant_lot_alerts(
    days: int = Query(default=15, ge=1),
    db: Session = Depends(get_db),
) -> list[StagnantLotAlert]:
    return list_stagnant_lot_alerts(db, days=days)


@router.get("/alerts/expiring-lots", response_model=list[ExpiringLotAlert])
def read_expiring_lot_alerts(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> list[ExpiringLotAlert]:
    return list_expiring_lot_alerts(db, days=days)


@router.patch("/lots/{lot_id}/transfer-to-store", response_model=InventoryLotRead)
def transfer_to_store_endpoint(
    lot_id: str,
    payload: StockTransfer,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> InventoryLotRead:
    before_lot = db.get(InventoryLot, lot_id)
    before = (
        model_snapshot(before_lot, ["warehouse_units", "store_units", "lot_number"])
        if before_lot
        else None
    )
    try:
        lot = transfer_to_store(db, lot_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")
    after = model_snapshot(lot, ["warehouse_units", "store_units", "lot_number"])
    record_audit_event(
        db,
        module="inventory",
        action="transfer_to_store",
        entity_type="inventory_lot",
        entity_id=lot.id,
        summary=f"Traslado a tienda de {payload.units} unidades.",
        actor=current_user,
        before_data=before,
        after_data=after,
    )
    return lot


@router.patch("/lots/{lot_id}/loss", response_model=InventoryLotRead)
def register_stock_loss_endpoint(
    lot_id: str,
    payload: StockLossCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> InventoryLotRead:
    before_lot = db.get(InventoryLot, lot_id)
    before = (
        model_snapshot(before_lot, ["warehouse_units", "store_units", "lot_number"])
        if before_lot
        else None
    )
    try:
        lot = register_stock_loss(db, lot_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")
    after = model_snapshot(lot, ["warehouse_units", "store_units", "lot_number"])
    record_audit_event(
        db,
        module="inventory",
        action="stock_loss",
        entity_type="inventory_lot",
        entity_id=lot.id,
        summary=f"Merma/perdida registrada por {payload.units} unidades.",
        actor=current_user,
        before_data=before,
        after_data=after,
        reason=payload.reason,
    )
    return lot


@router.patch("/lots/expired/retire", response_model=ExpiredLotsRetirementResult)
def retire_expired_lots_endpoint(
    payload: ExpiredLotsRetirementRequest,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> ExpiredLotsRetirementResult:
    result = retire_expired_lots(db, payload)
    record_audit_event(
        db,
        module="inventory",
        action="retire_expired_lots",
        entity_type="inventory_lot",
        entity_id="expired",
        summary=(
            f"Retiro masivo de {result.retired_lots} lotes vencidos "
            f"por {result.total_units} unidades."
        ),
        actor=current_user,
        after_data=result.model_dump(),
        reason=payload.reason,
    )
    return result
