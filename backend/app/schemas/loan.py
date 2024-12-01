from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum
from .base import BaseSchema

class LoanType(str, Enum):
    MORTGAGE = "mortgage"
    RENOVATION = "renovation"
    EQUITY = "equity"
    PERSONAL = "personal"
    BUSINESS = "business"
    OTHER = "other"

class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    DEFAULT = "default"
    REFINANCED = "refinanced"
    PENDING = "pending"

class PaymentMethod(str, Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CHECK = "check"
    CARD = "card"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LoanBase(BaseModel):
    property_id: int
    loan_type: LoanType
    principal_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    term_months: int = Field(..., gt=0)
    payment_day: int = Field(..., ge=1, le=31)
    start_date: date
    lender_name: str
    lender_contact: Optional[str] = None
    loan_number: str
    notes: Optional[str] = None

class LoanCreate(LoanBase):
    @validator('payment_day')
    def validate_payment_day(cls, v):
        if not 1 <= v <= 31:
            raise ValueError('El día de pago debe estar entre 1 y 31')
        return v

class LoanUpdate(BaseModel):
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    payment_day: Optional[int] = Field(None, ge=1, le=31)
    status: Optional[LoanStatus] = None
    notes: Optional[str] = None

class Loan(LoanBase, BaseSchema):
    end_date: date
    status: LoanStatus
    remaining_balance: float
    monthly_payment: float
    last_payment_date: Optional[date] = None
    next_payment_date: Optional[date] = None

    class Config:
        from_attributes = True

class LoanDetail(Loan):
    property: "PropertyBase"
    documents: List["LoanDocument"] = []
    payments: List["LoanPayment"] = []

class LoanDocumentBase(BaseModel):
    document_type: str
    file_path: str
    description: Optional[str] = None

class LoanDocumentCreate(LoanDocumentBase):
    pass

class LoanDocument(LoanDocumentBase, BaseSchema):
    loan_id: int
    upload_date: date
    is_verified: bool = False
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoanPaymentBase(BaseModel):
    payment_date: date
    due_date: date
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    late_fee: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None

class LoanPaymentCreate(LoanPaymentBase):
    pass

class LoanPayment(LoanPaymentBase, BaseSchema):
    loan_id: int
    principal_amount: float
    interest_amount: float
    status: PaymentStatus
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoanSummary(BaseModel):
    loan_id: int
    total_amount: float
    remaining_balance: float
    total_paid: float
    total_principal_paid: float
    total_interest_paid: float
    total_late_fees: float
    monthly_payment: float
    next_payment_date: Optional[date]
    next_payment_amount: Optional[float]
    status: LoanStatus
    payments_made: int
    remaining_payments: int

class AmortizationEntry(BaseModel):
    payment_number: int
    payment_date: date
    payment_amount: float
    principal_payment: float
    interest_payment: float
    remaining_balance: float

from .property import PropertyBase  # Importación al final para evitar referencias circulares
