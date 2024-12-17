from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class MaintenanceTicketBase(BaseModel):
    property_id: int
    tenant_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    due_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    assigned_to: Optional[str] = None

class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass

class MaintenanceTicketUpdate(MaintenanceTicketBase):
    property_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    due_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    assigned_to: Optional[str] = None

class MaintenanceTicket(MaintenanceTicketBase, BaseSchema):
    class Config:
        from_attributes = True

class MaintenanceTicketDetail(MaintenanceTicket):
    property: "PropertyBase"
    tenant: Optional["TenantBase"] = None
    expenses: List["ExpenseBase"] = []
