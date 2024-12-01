from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Enum, Date
from sqlalchemy.orm import relationship, backref
from .base import BaseModel
import enum

class PropertyType(str, enum.Enum):
    PRINCIPAL = "principal"
    UNIT = "unit"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"
    OTHER = "other"

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
    postal_code = Column(String)
    
    # Detalles físicos
    size = Column(Float)  # en metros cuadrados
    total_area = Column(Float)  # En metros cuadrados
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    parking_spots = Column(Integer)
    floors = Column(Integer, default=1)
    
    # Detalles financieros
    purchase_price = Column(Float)
    current_value = Column(Float)
    monthly_rent = Column(Float)
    monthly_expenses = Column(Float, default=0.0)
    
    # Estado
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    purchase_date = Column(Date, nullable=True)
    
    # Tipo de propiedad y relaciones jerárquicas
    property_type = Column(Enum(PropertyType), nullable=False)
    parent_property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
    units = relationship("Property", backref=backref("parent", remote_side="Property.id"))
    units_new = relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    
    # Owner information
    user_id = Column(String, nullable=False, index=True)
    
    # Relaciones
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="property")
    expenses = relationship("Expense", back_populates="property")
    loans = relationship("Loan", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Property {self.name}>"
