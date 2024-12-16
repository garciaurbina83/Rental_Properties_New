from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.notification import Notification, NotificationPreference
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.schemas.notification_preference import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate
)
from datetime import datetime

class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    async def create_with_user(
        self,
        db: Session,
        *,
        obj_in: NotificationCreate
    ) -> Notification:
        notification = await super().create(db, obj_in=obj_in)
        return notification

    async def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_unread_count(
        self,
        db: Session,
        user_id: int
    ) -> int:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.read_at.is_(None)
            )
            .count()
        )

    async def mark_as_read(
        self,
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        notification = (
            db.query(self.model)
            .filter(
                self.model.id == notification_id,
                self.model.user_id == user_id
            )
            .first()
        )
        if notification:
            notification.read_at = datetime.utcnow()
            db.commit()
        return notification

    async def mark_all_as_read(
        self,
        db: Session,
        user_id: int
    ) -> int:
        result = (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.read_at.is_(None)
            )
            .update(
                {"read_at": datetime.utcnow()},
                synchronize_session=False
            )
        )
        db.commit()
        return result

    async def get_pending_reminders(
        self,
        db: Session,
        current_time: datetime
    ) -> List[Notification]:
        return (
            db.query(self.model)
            .filter(
                self.model.send_at <= current_time,
                self.model.sent_at.is_(None)
            )
            .all()
        )

class CRUDNotificationPreference(CRUDBase[NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate]):
    async def get_user_preferences(
        self,
        db: Session,
        user_id: int
    ) -> Optional[NotificationPreference]:
        return (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

    async def create_user_preferences(
        self,
        db: Session,
        obj_in: NotificationPreferenceCreate
    ) -> NotificationPreference:
        preferences = NotificationPreference(
            user_id=obj_in.user_id,
            preferences=obj_in.preferences,
            quiet_hours_start=obj_in.quiet_hours_start,
            quiet_hours_end=obj_in.quiet_hours_end,
            time_zone=obj_in.time_zone
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
        return preferences

    async def update_user_preferences(
        self,
        db: Session,
        db_obj: NotificationPreference,
        obj_in: Union[NotificationPreferenceUpdate, Dict]
    ) -> NotificationPreference:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

notification = CRUDNotification(Notification)
notification_preference = CRUDNotificationPreference(NotificationPreference)
