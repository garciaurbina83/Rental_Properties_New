from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime

class LoanType(enum.Enum):
    MORTGAGE = "mortgage"
    RENOVATION = "renovation"
    EQUITY = "equity"
    PERSONAL = "personal"
    BUSINESS = "business"
    OTHER = "other"

class LoanStatus(enum.Enum):
    ACTIVE = "active"
    PAID = "paid"
    DEFAULT = "default"
    REFINANCED = "refinanced"
    PENDING = "pending"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CHECK = "check"
    CARD = "card"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Loan(BaseModel):
    __tablename__ = "loans"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    # Detalles del préstamo
    loan_type = Column(Enum(LoanType))
    principal_amount = Column(Float)
    interest_rate = Column(Float)
    term_months = Column(Integer)
    payment_day = Column(Integer)  # Día del mes para el pago
    
    # Fechas
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Estado
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    remaining_balance = Column(Float)
    monthly_payment = Column(Float)
    last_payment_date = Column(Date, nullable=True)
    next_payment_date = Column(Date, nullable=True)
    
    # Información del prestamista
    lender_name = Column(String)
    lender_contact = Column(String)
    loan_number = Column(String, unique=True)
    notes = Column(String, nullable=True)
    
    # Relaciones
    property = relationship("Property", back_populates="loans")
    documents = relationship("LoanDocument", back_populates="loan", cascade="all, delete-orphan")
    payments = relationship("LoanPayment", back_populates="loan", cascade="all, delete-orphan")

class LoanDocument(BaseModel):
    __tablename__ = "loan_documents"
    
    loan_id = Column(Integer, ForeignKey("loans.id"))
    document_type = Column(String)  # Contrato, Pagaré, etc.
    file_path = Column(String)
    upload_date = Column(Date)
    description = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Relaciones
    loan = relationship("Loan", back_populates="documents")
    verified_by_user = relationship("User")

class LoanPayment(BaseModel):
    __tablename__ = "loan_payments"
    
    loan_id = Column(Integer, ForeignKey("loans.id"))
    payment_date = Column(Date)
    due_date = Column(Date)
    amount = Column(Float)
    principal_amount = Column(Float)
    interest_amount = Column(Float)
    late_fee = Column(Float, default=0.0)
    payment_method = Column(Enum(PaymentMethod))
    reference_number = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    notes = Column(String, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relaciones
    loan = relationship("Loan", back_populates="payments")
    processor = relationship("User")
