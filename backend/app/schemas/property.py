from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema
from enum import Enum

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class PropertyBase(BaseModel):
    """Base schema for property data"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la propiedad")
    address: str = Field(..., min_length=1, description="Dirección completa")
    city: str = Field(..., description="Ciudad")
    state: str = Field(..., description="Estado o provincia")
    zip_code: str = Field(..., description="Código postal")
    country: str = Field(..., description="País")
    size: float = Field(..., gt=0, description="Tamaño en metros cuadrados")
    bedrooms: int = Field(..., ge=0, description="Número de habitaciones")
    bathrooms: float = Field(..., ge=0, description="Número de baños")
    parking_spots: int = Field(..., ge=0, description="Espacios de estacionamiento")
    purchase_price: Optional[float] = Field(None, ge=0, description="Precio de compra")
    current_value: Optional[float] = Field(None, ge=0, description="Valor actual estimado")
    monthly_rent: Optional[float] = Field(None, ge=0, description="Renta mensual")
    status: PropertyStatus = Field(
        default=PropertyStatus.AVAILABLE,
        description="Estado actual de la propiedad"
    )
    is_active: bool = Field(True, description="Indica si la propiedad está activa")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Casa Moderna Centro",
                "address": "Calle Principal 123",
                "city": "Ciudad de México",
                "state": "CDMX",
                "zip_code": "01234",
                "country": "México",
                "size": 150.5,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "parking_spots": 2,
                "purchase_price": 500000.00,
                "current_value": 550000.00,
                "monthly_rent": 2500.00,
                "status": "available",
                "is_active": True
            }
        }
    )

class PropertyCreate(PropertyBase):
    """Schema for creating a new property"""
    pass

class PropertyUpdate(BaseModel):
    """Schema for updating an existing property"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la propiedad")
    address: Optional[str] = Field(None, min_length=1, description="Dirección completa")
    city: Optional[str] = Field(None, description="Ciudad")
    state: Optional[str] = Field(None, description="Estado o provincia")
    zip_code: Optional[str] = Field(None, description="Código postal")
    country: Optional[str] = Field(None, description="País")
    size: Optional[float] = Field(None, gt=0, description="Tamaño en metros cuadrados")
    bedrooms: Optional[int] = Field(None, ge=0, description="Número de habitaciones")
    bathrooms: Optional[float] = Field(None, ge=0, description="Número de baños")
    parking_spots: Optional[int] = Field(None, ge=0, description="Espacios de estacionamiento")
    purchase_price: Optional[float] = Field(None, ge=0, description="Precio de compra")
    current_value: Optional[float] = Field(None, ge=0, description="Valor actual estimado")
    monthly_rent: Optional[float] = Field(None, ge=0, description="Renta mensual")
    status: Optional[PropertyStatus] = Field(None, description="Estado actual de la propiedad")
    is_active: Optional[bool] = Field(None, description="Indica si la propiedad está activa")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Casa Moderna Centro Actualizada",
            "monthly_rent": 2600.00,
            "status": "rented"
        }
    })

class Property(PropertyBase, BaseSchema):
    """Schema for property responses"""
    id: int = Field(..., description="ID único de la propiedad")
    user_id: str = Field(..., description="ID del propietario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = ConfigDict(from_attributes=True)

class PropertyFilter(BaseModel):
    """Schema for filtering properties"""
    city: Optional[str] = Field(None, description="Filtrar por ciudad")
    state: Optional[str] = Field(None, description="Filtrar por estado")
    min_price: Optional[float] = Field(None, ge=0, description="Precio mínimo")
    max_price: Optional[float] = Field(None, ge=0, description="Precio máximo")
    min_size: Optional[float] = Field(None, ge=0, description="Tamaño mínimo")
    max_size: Optional[float] = Field(None, ge=0, description="Tamaño máximo")
    bedrooms: Optional[int] = Field(None, ge=0, description="Número de habitaciones")
    bathrooms: Optional[float] = Field(None, ge=0, description="Número de baños")
    status: Optional[PropertyStatus] = Field(None, description="Estado de la propiedad")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "city": "Ciudad de México",
            "min_price": 2000.00,
            "max_price": 3000.00,
            "bedrooms": 2,
            "status": "available"
        }
    })

class PropertyDetail(Property):
    contracts: List["ContractBase"] = []
    maintenance_tickets: List["MaintenanceTicketBase"] = []
    expenses: List["ExpenseBase"] = []
    loans: List["LoanBase"] = []
