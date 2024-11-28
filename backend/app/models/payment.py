from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    LATE = "late"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    OTHER = "other"

class Payment(BaseModel):
    __tablename__ = "payments"

    # Relaciones
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    
    # Detalles del pago
    amount = Column(Float)
    due_date = Column(Date)
    payment_date = Column(Date)
    
    # Estado y método
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod))
    
    # Cargos adicionales
    late_fee = Column(Float, default=0.0)
    
    # Referencia
    reference_number = Column(String)
    notes = Column(String)
    
    # Relaciones
    contract = relationship("Contract", back_populates="payments")
