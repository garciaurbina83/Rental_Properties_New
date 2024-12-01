"""
Este módulo define las relaciones entre los modelos para evitar importaciones circulares.
"""
from sqlalchemy.orm import relationship

def setup_relationships(Tenant, Contract, TenantReference, TenantDocument, Property, MaintenanceTicket, Payment, ContractDocument):
    # Tenant relationships
    Tenant.contracts = relationship("Contract", back_populates="tenant")
    Tenant.maintenance_tickets = relationship("MaintenanceTicket", back_populates="tenant")
    Tenant.references = relationship("TenantReference", back_populates="tenant")
    Tenant.documents = relationship("TenantDocument", back_populates="tenant")

    # Contract relationships
    Contract.tenant = relationship("Tenant", back_populates="contracts")
    Contract.property = relationship("Property", back_populates="contracts")
    Contract.payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")
    Contract.documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")

    # TenantReference relationships
    TenantReference.tenant = relationship("Tenant", back_populates="references")

    # TenantDocument relationships
    TenantDocument.tenant = relationship("Tenant", back_populates="documents")

    # Property relationships
    Property.contracts = relationship("Contract", back_populates="property")
    Property.maintenance_tickets = relationship("MaintenanceTicket", back_populates="property")

    # Payment relationships
    Payment.contract = relationship("Contract", back_populates="payments")

    # ContractDocument relationships
    ContractDocument.contract = relationship("Contract", back_populates="documents")
