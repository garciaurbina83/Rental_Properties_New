from sqlalchemy import Column, String, ForeignKey, Boolean, Float, Date, Integer, Enum, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class PaymentFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CHECK = "check"

class Contract(BaseModel):
    __tablename__ = "contracts"

    # Relaciones principales
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    
    # Información del contrato
    contract_number = Column(String, unique=True)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Información financiera
    rent_amount = Column(Float)
    security_deposit = Column(Float)
    payment_frequency = Column(Enum(PaymentFrequency), default=PaymentFrequency.MONTHLY)
    payment_due_day = Column(Integer)  # Día del mes en que vence el pago
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.TRANSFER)
    
    # Servicios y garantías
    utilities_included = Column(JSON)  # Lista de servicios incluidos
    guarantor_info = Column(JSON, nullable=True)  # Información del garante
    
    # Términos y condiciones
    terms_and_conditions = Column(String)
    special_conditions = Column(String, nullable=True)
    
    # Depósitos y pagos
    last_payment_date = Column(Date, nullable=True)
    deposit_returned = Column(Boolean, default=False)
    deposit_return_date = Column(Date, nullable=True)
    deposit_deductions = Column(Float, default=0.0)
    deposit_notes = Column(String, nullable=True)
    
    # Renovación
    is_renewable = Column(Boolean, default=True)
    renewal_price_increase = Column(Float, nullable=True)  # Porcentaje de incremento en renovación
    auto_renewal = Column(Boolean, default=False)
    
    # Relaciones
    tenant = relationship("Tenant", back_populates="contracts")
    unit = relationship("Unit", back_populates="contracts")
    payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")

class ContractDocument(BaseModel):
    __tablename__ = "contract_documents"
    
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    document_type = Column(String)  # Contrato firmado, adenda, etc.
    file_path = Column(String)
    upload_date = Column(Date)
    is_signed = Column(Boolean, default=False)
    signed_date = Column(Date, nullable=True)
    
    # Relación
    contract = relationship("Contract", back_populates="documents")
