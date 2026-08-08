from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentMethod = Literal["cash", "card", "transfer"]
DocumentType = Literal["receipt", "invoice"]


class ClinicReceiptCreate(BaseModel):
    patient_id: str
    consultation_id: str | None = None
    cashier_name: str = ""
    doctor_name: str = ""
    document_type: DocumentType = "receipt"
    payment_method: PaymentMethod = "cash"
    payment_reference: str = Field(default="", max_length=160)
    bank_name: str = Field(default="", max_length=120)
    description: str = Field(default="Consulta medica", min_length=2)
    subtotal: float = Field(ge=0)
    discount: float = Field(default=0, ge=0)


class ClinicReceiptRead(BaseModel):
    id: str
    patient_id: str
    consultation_id: str | None
    patient_name: str
    cashier_name: str
    doctor_name: str
    document_type: str
    payment_method: str
    payment_reference: str
    bank_name: str
    description: str
    subtotal: float
    discount: float
    total: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceiptText(BaseModel):
    receipt_id: str
    filename: str
    content: str


class ClinicPaymentTotals(BaseModel):
    cash: float = 0
    card: float = 0
    transfer: float = 0


class ClinicCashSummary(BaseModel):
    date: str
    cashier_name: str | None = None
    receipts_count: int
    subtotal: float
    discount: float
    total: float
    by_payment_method: ClinicPaymentTotals
