from typing import Dict, Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime

from app.models.audit_log import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)

class AuditService:
    async def log_action(
        self,
        db: Session,
        entity_type: str,
        entity_id: int,
        action: str,
        user: User,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log an action in the audit log."""
        try:
            # Get IP address and user agent if request is provided
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host
                user_agent = request.headers.get("user-agent")

            # Create audit log entry
            audit_log = AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                changes=changes,
                performed_by=user.id,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.info(
                f"Audit log created: {action} on {entity_type} {entity_id} by user {user.id}"
            )
            return audit_log

        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            raise

    async def get_entity_history(
        self,
        db: Session,
        entity_type: str,
        entity_id: int
    ) -> list[AuditLog]:
        """Get the complete history of an entity."""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(AuditLog.performed_at.desc()).all()

    async def get_user_actions(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[AuditLog]:
        """Get all actions performed by a user."""
        query = db.query(AuditLog).filter(AuditLog.performed_by == user_id)
        
        if start_date:
            query = query.filter(AuditLog.performed_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.performed_at <= end_date)
            
        return query.order_by(AuditLog.performed_at.desc()).all()

    async def audit_change(
        self,
        db: Session,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: int,
        changes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Helper function to audit changes."""
        user = User(id=user_id)  # Mock user for testing
        return await self.log_action(
            db=db,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user=user,
            changes=changes
        )

    def compare_objects(self, old_obj: Dict[str, Any], new_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two objects and return the differences."""
        changes = {}
        for key in new_obj:
            if key in old_obj and old_obj[key] != new_obj[key]:
                changes[key] = {
                    "old": old_obj[key],
                    "new": new_obj[key]
                }
        return changes

audit_service = AuditService()
