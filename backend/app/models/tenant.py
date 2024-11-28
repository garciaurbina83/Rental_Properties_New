from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class Tenant(BaseModel):
    __tablename__ = "tenants"

    # Información personal
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    # Documentos
    identification_type = Column(String)  # DNI, Pasaporte, etc.
    identification_number = Column(String)
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Información adicional
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    
    # Relaciones
    contracts = relationship("Contract", back_populates="tenant")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="tenant")
