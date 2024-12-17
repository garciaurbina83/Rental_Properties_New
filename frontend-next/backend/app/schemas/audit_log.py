from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AuditLogBase(BaseModel):
    entity_type: str
    entity_id: int
    action: str
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    performed_by: int

class AuditLogInDBBase(AuditLogBase):
    id: int
    performed_by: int
    performed_at: datetime

    class Config:
        from_attributes = True

class AuditLog(AuditLogInDBBase):
    pass

class AuditLogDetail(AuditLog):
    user: "UserBase"

from app.schemas.user import UserBase
AuditLogDetail.update_forward_refs()
