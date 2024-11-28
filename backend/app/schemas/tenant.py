from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from .base import BaseSchema

class TenantBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str
    identification_type: str
    identification_number: str
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_active: bool = True

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    identification_type: Optional[str] = None
    identification_number: Optional[str] = None

class Tenant(TenantBase, BaseSchema):
    class Config:
        from_attributes = True

class TenantDetail(Tenant):
    contracts: List["ContractBase"] = []
    maintenance_tickets: List["MaintenanceTicketBase"] = []
