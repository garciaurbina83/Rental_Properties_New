from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: int
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLogResponse(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
