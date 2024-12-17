from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..models.base import BaseModel
from ..core.security import get_password_hash
from ..models.user import User

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE
    resource_type = Column(String, nullable=False)  # payment, contract, etc.
    resource_id = Column(Integer)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Registrar una acción en el log de auditoría
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log

    @staticmethod
    def get_resource_history(
        db: Session,
        resource_type: str,
        resource_id: int
    ) -> list[AuditLog]:
        """
        Obtener historial de cambios de un recurso
        """
        return db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.timestamp.desc()).all()

    @staticmethod
    def get_user_actions(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[AuditLog]:
        """
        Obtener acciones realizadas por un usuario
        """
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(AuditLog.timestamp.desc()).all()

    @staticmethod
    def get_sensitive_operations(
        db: Session,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[AuditLog]:
        """
        Obtener operaciones sensibles (DELETE, actualizaciones de estado, etc.)
        """
        sensitive_actions = ["DELETE", "UPDATE_STATUS", "REFUND"]
        
        query = db.query(AuditLog).filter(AuditLog.action.in_(sensitive_actions))
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(AuditLog.timestamp.desc()).all()
