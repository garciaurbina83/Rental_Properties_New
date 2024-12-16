from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum
from .base import BaseSchema
from .expense_category import ExpenseCategory as ExpenseCategorySchema

class ExpenseType(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    TAXES = "taxes"
    INSURANCE = "insurance"
    MORTGAGE = "mortgage"
    IMPROVEMENTS = "improvements"
    MANAGEMENT = "management"
    LEGAL = "legal"
    OTHER = "other"

class ExpenseStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class RecurrenceInterval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ExpenseBase(BaseModel):
    property_id: int
    unit_id: Optional[int] = None
    maintenance_ticket_id: Optional[int] = None
    vendor_id: Optional[int] = None
    description: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    expense_type: ExpenseType
    status: ExpenseStatus = Field(default=ExpenseStatus.DRAFT)
    date_incurred: date
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    requires_approval: bool = True
    is_recurring: bool = False
    recurrence_interval: Optional[RecurrenceInterval] = None
    recurrence_end_date: Optional[date] = None
    parent_expense_id: Optional[int] = None
    attachments: List[str] = []
    receipt_path: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    category_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    property_id: Optional[int] = None
    unit_id: Optional[int] = None
    maintenance_ticket_id: Optional[int] = None
    vendor_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1)
    amount: Optional[float] = Field(None, gt=0)
    expense_type: Optional[ExpenseType] = None
    status: Optional[ExpenseStatus] = None
    date_incurred: Optional[date] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    requires_approval: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_interval: Optional[RecurrenceInterval] = None
    recurrence_end_date: Optional[date] = None
    attachments: Optional[List[str]] = None
    receipt_path: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    category_id: Optional[int] = None

class ExpenseInDBBase(ExpenseBase):
    approved_by: Optional[int] = None
    approved_at: Optional[date] = None
    rejection_reason: Optional[str] = None
    child_expenses: List["Expense"] = []
    category: Optional[ExpenseCategorySchema] = None

    class Config:
        from_attributes = True

class Expense(ExpenseInDBBase, BaseSchema):
    pass

class ExpenseDetail(Expense):
    property: "PropertyBase"
    unit: Optional["UnitBase"] = None
    maintenance_ticket: Optional["MaintenanceTicketBase"] = None
    vendor: Optional["VendorBase"] = None
    approver: Optional["UserBase"] = None

class ExpenseAttachment(BaseSchema):
    id: int
    expense_id: int
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_by: int
    uploaded_at: date
    description: Optional[str] = None

class ExpenseSummary(BaseModel):
    total_amount: float
    paid_amount: float
    pending_amount: float
    overdue_amount: float
    total_count: int
    paid_count: int
    pending_count: int
    overdue_count: int
    average_processing_time: Optional[float] = None  # in days

class ExpenseCategorySummary(BaseModel):
    category: ExpenseType
    total_amount: float
    count: int
    percentage_of_total: float

class PropertyExpenseSummary(BaseModel):
    property_id: int
    property_name: str
    total_amount: float
    count: int
    categories: List[ExpenseCategorySummary]

class VendorExpenseSummary(BaseModel):
    vendor_id: int
    vendor_name: str
    total_amount: float
    count: int
    average_amount: float
    categories: List[ExpenseCategorySummary]

class RecurringExpenseSummary(BaseModel):
    expense_id: int
    description: str
    amount: float
    expense_type: ExpenseType
    recurrence_interval: RecurrenceInterval
    next_due_date: date
    property_id: Optional[int] = None
    unit_id: Optional[int] = None
    vendor_id: Optional[int] = None

from .property import PropertyBase
from .unit import UnitBase
from .maintenance import MaintenanceTicketBase
from .vendor import VendorBase
from .auth import UserBase
