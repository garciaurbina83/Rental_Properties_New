from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.notification import NotificationType, NotificationStatus, NotificationPriority

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: NotificationPriority = NotificationPriority.NORMAL

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatus
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class NotificationInDB(NotificationOut):
    pass

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Tipo de mensaje: notification, error, system")
    data: Dict[str, Any] = Field(..., description="Contenido del mensaje")

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True
    payment_reminders: bool = True
    system_notifications: bool = True
    maintenance_alerts: bool = True
    contract_updates: bool = True
