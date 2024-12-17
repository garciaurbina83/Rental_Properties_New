from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class AuditLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # e.g., 'expense', 'property', etc.
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # e.g., 'create', 'update', 'delete'
    changes = Column(JSON, nullable=True)  # Store changes in JSON format
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[performed_by])
