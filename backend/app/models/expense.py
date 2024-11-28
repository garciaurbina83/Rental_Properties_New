from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ExpenseCategory(enum.Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    TAXES = "taxes"
    INSURANCE = "insurance"
    MORTGAGE = "mortgage"
    OTHER = "other"

class ExpenseStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class Expense(BaseModel):
    __tablename__ = "expenses"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    maintenance_ticket_id = Column(Integer, ForeignKey("maintenance_tickets.id"), nullable=True)
    
    # Detalles del gasto
    amount = Column(Float)
    category = Column(Enum(ExpenseCategory))
    description = Column(String)
    
    # Estado
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    
    # Fechas
    due_date = Column(Date)
    payment_date = Column(Date)
    
    # Documentación
    invoice_number = Column(String)
    receipt_url = Column(String)
    
    # Relaciones
    property = relationship("Property", back_populates="expenses")
    maintenance_ticket = relationship("MaintenanceTicket", back_populates="expenses")
