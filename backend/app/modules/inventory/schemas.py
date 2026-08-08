from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductPresentationCreate(BaseModel):
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=80)
    units_per_sale: int = Field(default=1, ge=1)
    default_price: float = Field(default=0, ge=0)
    label_price: float = Field(default=0, ge=0)


class ProductPresentationRead(ProductPresentationCreate):
    id: str
    product_id: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LotPresentationPriceCreate(BaseModel):
    presentation_code: str = Field(min_length=1, max_length=60)
    sale_price: float = Field(ge=0)
    label_price: float = Field(default=0, ge=0)


class LotPresentationPriceRead(BaseModel):
    id: str
    lot_id: str
    presentation_id: str
    presentation_code: str
    presentation_name: str
    sale_price: float
    label_price: float
    created_at: datetime
    updated_at: datetime


class InventoryLotCreate(BaseModel):
    lot_number: str = Field(min_length=1, max_length=120)
    lot_barcode: str = Field(default="", max_length=120)
    shelf_location: str = Field(default="", max_length=120)
    expires_at: date | None = None
    purchase_unit_cost: float = Field(default=0, ge=0)
    warehouse_units: int = Field(default=0, ge=0)
    store_units: int = Field(default=0, ge=0)
    presentation_prices: list[LotPresentationPriceCreate] = Field(default_factory=list)


class InventoryLotRead(InventoryLotCreate):
    id: str
    product_id: str
    created_at: datetime
    updated_at: datetime
    presentation_prices: list[LotPresentationPriceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InventoryMovementRead(BaseModel):
    id: str
    lot_id: str
    product_id: str
    movement_type: str
    from_location: str
    to_location: str
    units: int
    reason: str
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockLossCreate(BaseModel):
    location: str = Field(pattern="^(warehouse|store)$")
    units: int = Field(gt=0)
    reason: str = Field(default="Merma", max_length=220)
    note: str = ""


class ExpiredLotsRetirementRequest(BaseModel):
    reason: str = Field(default="Retiro por vencimiento", max_length=220)
    note: str = ""


class ExpiredLotsRetirementResult(BaseModel):
    retired_lots: int
    store_units: int
    warehouse_units: int
    total_units: int


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=220)
    sku: str = Field(default="", max_length=80)
    barcode: str = Field(default="", max_length=120)
    description: str = ""
    base_unit_name: str = Field(default="unidad", max_length=60)
    laboratory_name: str = Field(default="", max_length=160)
    supplier_name: str = Field(default="", max_length=160)
    units_per_blister: int = Field(default=1, ge=1)
    blisters_per_box: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0, ge=0)
    blister_price: float = Field(default=0, ge=0)
    box_price: float = Field(default=0, ge=0)
    min_stock_units: int = Field(default=0, ge=0)
    presentations: list[ProductPresentationCreate] = Field(default_factory=list)
    lot: InventoryLotCreate | None = None


class ProductRead(BaseModel):
    id: str
    name: str
    sku: str
    barcode: str
    description: str
    base_unit_name: str
    laboratory_name: str
    supplier_name: str
    units_per_blister: int
    blisters_per_box: int
    unit_price: float
    blister_price: float
    box_price: float
    min_stock_units: int
    active: bool
    total_warehouse_units: int
    total_store_units: int
    presentations: list[ProductPresentationRead]
    lots: list[InventoryLotRead]
    created_at: datetime
    updated_at: datetime


class StockTransfer(BaseModel):
    units: int = Field(gt=0)


class PickListItem(BaseModel):
    lot_id: str
    product_id: str
    product_name: str
    lot_number: str
    shelf_location: str
    expires_at: date | None
    recommended_units: int
    warehouse_units: int
    store_units: int


class StagnantLotAlert(BaseModel):
    lot_id: str
    product_id: str
    product_name: str
    lot_number: str
    store_units: int
    days_without_movement: int
    message: str


class ExpiringLotAlert(BaseModel):
    lot_id: str
    product_id: str
    product_name: str
    lot_number: str
    shelf_location: str
    expires_at: date
    warehouse_units: int
    store_units: int
    total_units: int
    days_to_expire: int
    message: str
