from sqlalchemy import Column, String, Integer, Float, ForeignKey, Date, Enum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ExpenseType(str, enum.Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    TAXES = "taxes"
    INSURANCE = "insurance"
    MORTGAGE = "mortgage"
    IMPROVEMENTS = "improvements"
    MANAGEMENT = "management"
    LEGAL = "legal"
    OTHER = "other"

class ExpenseStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class RecurrenceInterval(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class Expense(BaseModel):
    __tablename__ = "expenses"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    maintenance_ticket_id = Column(Integer, ForeignKey("maintenance_tickets.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("expensecategory.id"), nullable=True)
    
    # Información básica
    description = Column(String)
    amount = Column(Float)
    expense_type = Column(Enum(ExpenseType))
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.DRAFT)
    
    # Fechas
    date_incurred = Column(Date)
    due_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    
    # Detalles de pago
    payment_method = Column(String, nullable=True)
    reference_number = Column(String, nullable=True)
    
    # Sistema de aprobación
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Gastos recurrentes
    is_recurring = Column(Boolean, default=False)
    recurrence_interval = Column(Enum(RecurrenceInterval), nullable=True)
    recurrence_end_date = Column(Date, nullable=True)
    parent_expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    
    # Archivos y documentación
    attachments = Column(JSON, default=list)  # Lista de rutas a archivos adjuntos
    receipt_path = Column(String, nullable=True)
    
    # Notas y metadatos
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    
    # Relaciones
    property = relationship("Property", back_populates="expenses")
    unit = relationship("Unit", back_populates="expenses")
    maintenance_ticket = relationship("MaintenanceTicket", back_populates="expenses")
    vendor = relationship("Vendor", back_populates="expenses")
    approver = relationship("User", foreign_keys=[approved_by])
    category = relationship("ExpenseCategory", back_populates="expenses")
    child_expenses = relationship("Expense", backref=relationship("parent", remote_side="Expense.id"))

    def __repr__(self):
        return f"<Expense {self.description} - {self.amount}>"
