from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum
from .base import BaseSchema

class ExpenseCategory(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    TAXES = "taxes"
    INSURANCE = "insurance"
    MORTGAGE = "mortgage"
    OTHER = "other"

class ExpenseStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class ExpenseBase(BaseModel):
    property_id: int
    maintenance_ticket_id: Optional[int] = None
    amount: float = Field(..., gt=0)
    category: ExpenseCategory
    description: str = Field(..., min_length=1)
    status: ExpenseStatus = Field(default=ExpenseStatus.PENDING)
    due_date: date
    payment_date: Optional[date] = None
    invoice_number: Optional[str] = None
    receipt_url: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    property_id: Optional[int] = None
    amount: Optional[float] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    status: Optional[ExpenseStatus] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    invoice_number: Optional[str] = None
    receipt_url: Optional[str] = None

class Expense(ExpenseBase, BaseSchema):
    class Config:
        from_attributes = True

class ExpenseDetail(Expense):
    property: "PropertyBase"
    maintenance_ticket: Optional["MaintenanceTicketBase"] = None
