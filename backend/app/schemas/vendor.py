from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from .base import BaseSchema
from datetime import date
from typing import ForwardRef

ExpenseBase = ForwardRef('ExpenseBase')

class VendorBase(BaseModel):
    name: str = Field(..., min_length=1)
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

class Vendor(VendorBase, BaseSchema):
    expenses: List[ExpenseBase] = []

    class Config:
        from_attributes = True

class VendorRating(BaseSchema):
    id: int
    vendor_id: int
    rating: float = Field(..., ge=0, le=5)
    rated_by: int
    rated_at: date
    comment: Optional[str] = None

class VendorWithStats(Vendor):
    total_expenses: int
    total_amount: float
    average_expense: float
    last_expense_date: Optional[date] = None
    rating_count: int
    average_rating: Optional[float] = None
