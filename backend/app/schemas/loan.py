from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum
from .base import BaseSchema

class LoanType(str, Enum):
    MORTGAGE = "mortgage"
    RENOVATION = "renovation"
    EQUITY = "equity"
    OTHER = "other"

class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    DEFAULT = "default"
    REFINANCED = "refinanced"

class LoanBase(BaseModel):
    property_id: int
    loan_type: LoanType
    principal_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    term_months: int = Field(..., gt=0)
    start_date: date
    end_date: date
    status: LoanStatus = Field(default=LoanStatus.ACTIVE)
    remaining_balance: float = Field(..., ge=0)
    monthly_payment: float = Field(..., gt=0)
    lender_name: str
    lender_contact: Optional[str] = None
    loan_number: str

class LoanCreate(LoanBase):
    pass

class LoanUpdate(LoanBase):
    property_id: Optional[int] = None
    loan_type: Optional[LoanType] = None
    principal_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    term_months: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[LoanStatus] = None
    remaining_balance: Optional[float] = None
    monthly_payment: Optional[float] = None
    lender_name: Optional[str] = None
    lender_contact: Optional[str] = None
    loan_number: Optional[str] = None

class Loan(LoanBase, BaseSchema):
    class Config:
        from_attributes = True

class LoanDetail(Loan):
    property: "PropertyBase"
