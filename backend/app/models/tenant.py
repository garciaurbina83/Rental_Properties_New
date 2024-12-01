from sqlalchemy import Column, String, Integer, Date, Boolean, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ContactMethod(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    WHATSAPP = "whatsapp"

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    BLACKLISTED = "blacklisted"

class Tenant(BaseModel):
    __tablename__ = "tenants"

    # Información personal
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    occupation = Column(String)
    monthly_income = Column(Float)
    previous_address = Column(String)
    
    # Documentos
    identification_type = Column(String)  # DNI, Pasaporte, etc.
    identification_number = Column(String)
    
    # Estado y preferencias
    is_active = Column(Boolean, default=True)
    preferred_contact_method = Column(Enum(ContactMethod), default=ContactMethod.EMAIL)
    notes = Column(String, nullable=True)
    
    # Información adicional
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    date_of_birth = Column(Date)
    employer = Column(String, nullable=True)
    status = Column(Enum(TenantStatus), default=TenantStatus.PENDING)
    
    # Relaciones
    contracts = relationship("Contract", back_populates="tenant")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="tenant")
    references = relationship("TenantReference", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("TenantDocument", back_populates="tenant", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")

    def __repr__(self):
        return f"<Tenant {self.first_name} {self.last_name}>"
