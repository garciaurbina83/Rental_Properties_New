from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship as orm_relationship
from .base import BaseModel

class TenantReference(BaseModel):
    __tablename__ = "tenant_references"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String)
    ref_relationship = Column(String)  # Cambiado de relationship a ref_relationship
    phone = Column(String)
    email = Column(String)
    notes = Column(String, nullable=True)
    
    # Relación con el inquilino
    tenant = orm_relationship("Tenant", back_populates="references")

class TenantDocument(BaseModel):
    __tablename__ = "tenant_documents"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    document_type = Column(String)  # ID, Comprobante de ingresos, etc.
    file_path = Column(String)
    upload_date = Column(Date)
    expiry_date = Column(Date, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relación con el inquilino
    tenant = orm_relationship("Tenant", back_populates="documents")
