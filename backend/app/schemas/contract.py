from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum
from .base import BaseSchema

class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class ContractBase(BaseModel):
    property_id: int
    tenant_id: int
    start_date: date
    end_date: date
    monthly_rent: float = Field(..., gt=0)
    security_deposit: float = Field(..., ge=0)
    payment_day: int = Field(..., ge=1, le=31)
    late_fee_percentage: float = Field(..., ge=0, le=100)
    status: ContractStatus = Field(default=ContractStatus.DRAFT)
    is_active: bool = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(ContractBase):
    property_id: Optional[int] = None
    tenant_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    monthly_rent: Optional[float] = None
    security_deposit: Optional[float] = None
    payment_day: Optional[int] = None
    late_fee_percentage: Optional[float] = None

class Contract(ContractBase, BaseSchema):
    class Config:
        from_attributes = True

class ContractDetail(Contract):
    property: "PropertyBase"
    tenant: "TenantBase"
    payments: List["PaymentBase"] = []
