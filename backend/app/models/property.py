from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship, backref
from .base import BaseModel
import enum

class PropertyType(str, enum.Enum):
    PRINCIPAL = "principal"
    UNIT = "unit"

class PropertyStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Property(BaseModel):
    __tablename__ = "properties"

    name = Column(String, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)
    
    # Detalles físicos
    size = Column(Float)  # en metros cuadrados
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    parking_spots = Column(Integer)
    
    # Detalles financieros
    purchase_price = Column(Float)
    current_value = Column(Float)
    monthly_rent = Column(Float)
    
    # Estado
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    
    # Tipo de propiedad y relaciones jerárquicas
    property_type = Column(Enum(PropertyType), nullable=False)
    parent_property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
    units = relationship("Property", backref=backref("parent", remote_side="Property.id"))
    
    # Owner information
    user_id = Column(String, nullable=False, index=True)
    
    # Relaciones
    contracts = relationship("Contract", back_populates="property")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="property")
    expenses = relationship("Expense", back_populates="property")
    loans = relationship("Loan", back_populates="property")
