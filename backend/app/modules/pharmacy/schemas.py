from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentMethod = Literal["cash", "card", "transfer"]
DocumentType = Literal["receipt", "invoice"]


class SaleItemCreate(BaseModel):
    product_id: str
    presentation: str = Field(default="unit", min_length=1, max_length=60)
    presentation_id: str | None = None
    lot_barcode: str | None = None
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    patient_id: str | None = None
    customer_name: str = "Consumidor final"
    cashier_name: str = ""
    document_type: DocumentType = "receipt"
    payment_method: PaymentMethod = "cash"
    payment_reference: str = Field(default="", max_length=160)
    bank_name: str = Field(default="", max_length=120)
    discount: float = Field(default=0, ge=0)
    discount_type: str = Field(default="none", max_length=40)
    discount_base_total: float = Field(default=0, ge=0)
    discount_evidence_note: str = Field(default="", max_length=260)
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleLotAllocationRead(BaseModel):
    id: str
    lot_id: str
    lot_number: str
    units: int
    purchase_unit_cost: float
    sale_unit_value: float
    cost_total: float
    revenue_total: float
    profit_total: float

    model_config = ConfigDict(from_attributes=True)


class SaleItemRead(BaseModel):
    id: str
    product_id: str
    product_name: str
    presentation: str
    quantity: int
    units_deducted: int
    unit_price: float
    line_total: float
    label_unit_price: float = 0
    label_line_total: float = 0
    cost_total: float
    profit_total: float
    allocations: list[SaleLotAllocationRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SaleRead(BaseModel):
    id: str
    patient_id: str
    customer_name: str
    cashier_name: str
    document_type: str
    payment_method: str
    payment_reference: str = ""
    bank_name: str = ""
    status: str
    subtotal: float
    discount: float
    discount_type: str = "none"
    discount_base_total: float = 0
    discount_evidence_note: str = ""
    total: float
    cost_total: float = 0
    profit_total: float = 0
    created_at: datetime
    items: list[SaleItemRead]

    model_config = ConfigDict(from_attributes=True)


class PharmacyPaymentTotals(BaseModel):
    cash: float = 0
    card: float = 0
    transfer: float = 0


class PharmacyCashSummary(BaseModel):
    date: str
    cashier_name: str | None = None
    sales_count: int
    subtotal: float
    discount: float
    total: float
    cost_total: float
    profit_total: float
    by_payment_method: PharmacyPaymentTotals


class ReceiptText(BaseModel):
    sale_id: str
    filename: str
    content: str
