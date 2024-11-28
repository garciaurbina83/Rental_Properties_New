from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ContractStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class Contract(BaseModel):
    __tablename__ = "contracts"

    # Relaciones
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    # Fechas
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Detalles financieros
    monthly_rent = Column(Float)
    security_deposit = Column(Float)
    
    # Términos
    payment_day = Column(Integer)  # Día del mes para el pago
    late_fee_percentage = Column(Float)
    
    # Estado
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    property = relationship("Property", back_populates="contracts")
    tenant = relationship("Tenant", back_populates="contracts")
    payments = relationship("Payment", back_populates="contract")
