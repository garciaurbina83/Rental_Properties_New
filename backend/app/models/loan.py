from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class LoanType(enum.Enum):
    MORTGAGE = "mortgage"
    RENOVATION = "renovation"
    EQUITY = "equity"
    OTHER = "other"

class LoanStatus(enum.Enum):
    ACTIVE = "active"
    PAID = "paid"
    DEFAULT = "default"
    REFINANCED = "refinanced"

class Loan(BaseModel):
    __tablename__ = "loans"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    # Detalles del préstamo
    loan_type = Column(Enum(LoanType))
    principal_amount = Column(Float)
    interest_rate = Column(Float)
    term_months = Column(Integer)
    
    # Fechas
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Estado
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    remaining_balance = Column(Float)
    monthly_payment = Column(Float)
    
    # Información del prestamista
    lender_name = Column(String)
    lender_contact = Column(String)
    loan_number = Column(String)
    
    # Relaciones
    property = relationship("Property", back_populates="loans")
