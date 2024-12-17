from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class TenantReferenceBase(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    notes: Optional[str] = None

class TenantReferenceCreate(TenantReferenceBase):
    pass

class TenantReference(TenantReferenceBase):
    id: int
    tenant_id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class TenantDocumentBase(BaseModel):
    document_type: str
    file_path: str
    upload_date: date
    expiry_date: Optional[date] = None
    is_verified: bool = False

class TenantDocumentCreate(TenantDocumentBase):
    pass

class TenantDocument(TenantDocumentBase):
    id: int
    tenant_id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class TenantBase(BaseModel):
    first_name: str = Field(..., min_length=1, description="First name of the tenant")
    last_name: str = Field(..., min_length=1, description="Last name of the tenant")
    property_id: int = Field(..., description="ID of the property being rented")
    lease_start: date = Field(..., description="Start date of the lease")
    lease_end: date = Field(..., description="End date of the lease")
    deposit: Decimal = Field(..., ge=0, description="Security deposit amount")
    monthly_rent: Decimal = Field(..., ge=0, description="Monthly rent amount")
    payment_day: int = Field(..., ge=1, le=31, description="Day of the month when rent is due")

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    property_id: Optional[int] = None
    lease_start: Optional[date] = None
    lease_end: Optional[date] = None
    deposit: Optional[Decimal] = Field(None, ge=0)
    monthly_rent: Optional[Decimal] = Field(None, ge=0)
    payment_day: Optional[int] = Field(None, ge=1, le=31)

class TenantResponse(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
