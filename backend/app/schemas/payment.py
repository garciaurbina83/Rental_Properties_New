from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum
from .base import BaseSchema

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    LATE = "late"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    OTHER = "other"

class PaymentBase(BaseModel):
    contract_id: int
    amount: float = Field(..., gt=0)
    due_date: date
    payment_date: Optional[date] = None
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: Optional[PaymentMethod] = None
    late_fee: float = Field(default=0.0, ge=0)
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    contract_id: Optional[int] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    late_fee: Optional[float] = None

class Payment(PaymentBase, BaseSchema):
    class Config:
        from_attributes = True

class PaymentDetail(Payment):
    contract: "ContractBase"
