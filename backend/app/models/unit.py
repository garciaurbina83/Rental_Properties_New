from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UnitType(str, enum.Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    ROOM = "room"
    OFFICE = "office"
    RETAIL = "retail"
    WAREHOUSE = "warehouse"
    OTHER = "other"

class Unit(BaseModel):
    __tablename__ = "units"

    # Relación con la propiedad
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    # Información básica
    unit_number = Column(String)  # Número o identificador de la unidad
    floor = Column(Integer, nullable=True)  # Piso (si aplica)
    unit_type = Column(Enum(UnitType))
    
    # Características
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Float, default=0)  # Float para permitir medios baños (0.5)
    total_area = Column(Float)  # En metros cuadrados
    furnished = Column(Boolean, default=False)
    
    # Estado
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)  # Para unidades que ya no se rentan
    
    # Información financiera
    base_rent = Column(Float)  # Renta base sugerida
    
    # Notas y descripción
    description = Column(String, nullable=True)
    amenities = Column(String, nullable=True)  # Lista de amenidades separadas por comas
    
    # Relaciones
    property = relationship("Property", back_populates="units_new")
    contracts = relationship("Contract", back_populates="unit")
    expenses = relationship("Expense", back_populates="unit")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="unit")

    def __repr__(self):
        return f"<Unit {self.unit_number} at Property {self.property_id}>"
