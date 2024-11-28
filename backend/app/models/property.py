from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class PropertyStatus(enum.Enum):
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
    
    # Owner information
    user_id = Column(String, nullable=False, index=True)
    
    # Relaciones
    contracts = relationship("Contract", back_populates="property")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="property")
    expenses = relationship("Expense", back_populates="property")
    loans = relationship("Loan", back_populates="property")
