from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum
from .base import BaseSchema
from .user import UserBase
from .contract import ContractBase

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

class PaymentConcept(str, Enum):
    RENT = "rent"
    DEPOSIT = "deposit"
    LATE_FEE = "late_fee"
    MAINTENANCE = "maintenance"
    OTHER = "other"

class PaymentBase(BaseModel):
    contract_id: int
    amount: float = Field(..., gt=0)
    due_date: date
    payment_date: Optional[date] = None
    concept: PaymentConcept = Field(default=PaymentConcept.RENT)
    payment_period_start: Optional[date] = None
    payment_period_end: Optional[date] = None
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: Optional[PaymentMethod] = None
    late_fee: float = Field(default=0.0, ge=0)
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    processed_by_id: Optional[int] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    contract_id: Optional[int] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    concept: Optional[PaymentConcept] = None
    payment_period_start: Optional[date] = None
    payment_period_end: Optional[date] = None
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    late_fee: Optional[float] = None
    processed_by_id: Optional[int] = None

class Payment(PaymentBase, BaseSchema):
    class Config:
        from_attributes = True

class PaymentDetail(Payment):
    contract: "ContractBase"
    processed_by: Optional["UserBase"] = None
