from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CashModule = Literal["clinic", "pharmacy"]
CashStatus = Literal["open", "closed"]


class CashRegisterOpen(BaseModel):
    module: CashModule
    cashier_name: str = Field(min_length=2, max_length=180)
    opening_amount: float = Field(default=0, ge=0)


class CashRegisterClose(BaseModel):
    counted_cash: float = Field(default=0, ge=0)
    counted_card: float = Field(default=0, ge=0)
    counted_transfer: float = Field(default=0, ge=0)
    notes: str = ""

    @model_validator(mode="after")
    def require_note_for_difference_hint(self) -> "CashRegisterClose":
        return self


class CashRegisterSessionRead(BaseModel):
    id: str
    module: str
    cashier_name: str
    status: str
    opening_amount: float
    opened_at: datetime
    closed_at: datetime | None
    expected_cash: float
    expected_card: float
    expected_transfer: float
    expected_total: float
    counted_cash: float
    counted_card: float
    counted_transfer: float
    counted_total: float
    difference: float
    notes: str
    opened_by_user_id: str | None
    closed_by_user_id: str | None

    model_config = ConfigDict(from_attributes=True)
