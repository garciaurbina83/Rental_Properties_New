from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship, backref, validates
from ..core.database import Base
from enum import Enum

class PropertyType(str, Enum):
    PRINCIPAL = 'PRINCIPAL'
    UNIT = 'UNIT'

class PropertyStatus(str, Enum):
    AVAILABLE = 'available'
    RENTED = 'rented'

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Información básica
    name = Column(String(255))
    address = Column(String(255), nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
        
    # Detalles físicos
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    
    # Estado y tipo
    status = Column(String(50), server_default=PropertyStatus.AVAILABLE.value, nullable=False)
    is_active = Column(Boolean, server_default='true', nullable=False)
    property_type = Column(String(50), nullable=False)
    parent_property_id = Column(Integer, ForeignKey('properties.id'))
    
    # Owner information
    user_id = Column(String, nullable=False, index=True)
    
    # Relaciones
    units = relationship(
        "Property",
        backref=backref("parent", remote_side="Property.id"),
        cascade="all, delete-orphan"
    )
    
    tenants = relationship(
        "Tenant", 
        back_populates="property", 
        cascade="all, delete-orphan",
        uselist=True
    )
    
    @validates('property_type')
    def validate_property_type(self, key, value):
        if not isinstance(value, PropertyType):
            value = PropertyType(value)
        return value.value

    @validates('status')
    def validate_status(self, key, value):
        if value:
            if not isinstance(value, PropertyStatus):
                value = PropertyStatus(value)
            return value.value
        return PropertyStatus.AVAILABLE.value

    @validates('parent_property_id')
    def validate_parent(self, key, value):
        if value is not None and self.property_type != PropertyType.UNIT.value:
            raise ValueError("Only units can have a parent property")
        return value

    def update_status_from_tenants(self):
        """Update property status based on active tenants"""
        has_active_tenants = any(
            tenant.lease_end >= func.current_date() 
            for tenant in self.tenants
        )
        self.status = PropertyStatus.RENTED.value if has_active_tenants else PropertyStatus.AVAILABLE.value

    def __repr__(self):
        return f"<Property {self.name}>"
