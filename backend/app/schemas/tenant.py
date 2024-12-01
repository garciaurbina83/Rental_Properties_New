from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, constr
from ..models.tenant import ContactMethod, TenantStatus

class TenantReferenceBase(BaseModel):
    name: str
    relationship: str
    phone: constr(min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    notes: Optional[str] = None

class TenantReferenceCreate(TenantReferenceBase):
    pass

class TenantReference(TenantReferenceBase):
    id: int
    tenant_id: int
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

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
        orm_mode = True

class TenantBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: constr(min_length=8, max_length=20)
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    previous_address: Optional[str] = None
    identification_type: str
    identification_number: str
    is_active: bool = True
    preferred_contact_method: ContactMethod = ContactMethod.EMAIL
    notes: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_phone: constr(min_length=8, max_length=20)
    date_of_birth: Optional[date] = None
    employer: Optional[str] = None
    status: TenantStatus = TenantStatus.ACTIVE

class TenantCreate(TenantBase):
    references: Optional[List[TenantReferenceCreate]] = []
    documents: Optional[List[TenantDocumentCreate]] = []

class TenantUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(min_length=8, max_length=20)] = None
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    previous_address: Optional[str] = None
    identification_type: Optional[str] = None
    identification_number: Optional[str] = None
    is_active: Optional[bool] = None
    preferred_contact_method: Optional[ContactMethod] = None
    notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[constr(min_length=8, max_length=20)] = None
    date_of_birth: Optional[date] = None
    employer: Optional[str] = None
    status: Optional[TenantStatus] = None

class Tenant(TenantBase):
    id: int
    references: List[TenantReference] = []
    documents: List[TenantDocument] = []
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

class TenantInDB(Tenant):
    pass
