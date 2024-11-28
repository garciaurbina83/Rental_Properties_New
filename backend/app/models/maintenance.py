from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class MaintenanceTicket(BaseModel):
    __tablename__ = "maintenance_tickets"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    # Detalles del ticket
    title = Column(String)
    description = Column(String)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    
    # Fechas
    due_date = Column(DateTime)
    resolved_date = Column(DateTime)
    
    # Costos
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    # Asignación
    assigned_to = Column(String)
    
    # Relaciones
    property = relationship("Property", back_populates="maintenance_tickets")
    tenant = relationship("Tenant", back_populates="maintenance_tickets")
    expenses = relationship("Expense", back_populates="maintenance_ticket")
