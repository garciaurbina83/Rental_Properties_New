from sqlalchemy import Column, String, Integer, Float, ForeignKey, Date, Enum, DateTime, Boolean
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

class MaintenanceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MaintenancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class MaintenanceRequest(BaseModel):
    __tablename__ = "maintenance_requests"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Información básica
    title = Column(String)
    description = Column(String)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM)
    
    # Fechas
    request_date = Column(Date)
    scheduled_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    
    # Costos
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Detalles del trabajo
    work_performed = Column(String, nullable=True)
    contractor_info = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    
    # Notas adicionales
    notes = Column(String, nullable=True)
    photos_path = Column(String, nullable=True)  # Ruta a las fotos del mantenimiento
    
    # Relaciones
    property = relationship("Property", back_populates="maintenance_requests")
    unit = relationship("Unit", back_populates="maintenance_requests")
    tenant = relationship("Tenant", back_populates="maintenance_requests")

    def __repr__(self):
        return f"<MaintenanceRequest {self.title} - {self.status}>"
