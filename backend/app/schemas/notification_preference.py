from typing import Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.notification import NotificationType, NotificationChannel

class NotificationPreferenceBase(BaseModel):
    user_id: int
    preferences: Dict[str, Dict[str, bool]] = Field(
        default_factory=dict,
        description="Nested dictionary of notification preferences. "
                   "First level key is notification type, second level is channel type."
    )
    quiet_hours_start: Optional[int] = Field(
        None,
        ge=0,
        le=23,
        description="Start hour for quiet time (24-hour format)"
    )
    quiet_hours_end: Optional[int] = Field(
        None,
        ge=0,
        le=23,
        description="End hour for quiet time (24-hour format)"
    )
    time_zone: Optional[str] = Field(
        None,
        description="User's timezone for notification timing"
    )

class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass

class NotificationPreferenceUpdate(BaseModel):
    preferences: Optional[Dict[str, Dict[str, bool]]] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    time_zone: Optional[str] = None

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int

    class Config:
        orm_mode = True

def create_default_preferences() -> Dict[str, Dict[str, bool]]:
    """
    Create default notification preferences for a new user.
    By default, all notifications are enabled for all channels.
    """
    preferences = {}
    for notification_type in NotificationType:
        preferences[notification_type.value] = {
            channel.value: True for channel in NotificationChannel
        }
    return preferences
