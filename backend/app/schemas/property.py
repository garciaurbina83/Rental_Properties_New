from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from ..models.property import PropertyStatus, PropertyType

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
    property_type: PropertyType = Field(..., description="Tipo de propiedad (Principal o Unit)")
    parent_property_id: Optional[int] = Field(None, description="ID de la propiedad principal (solo para Units)")

    model_config = ConfigDict(
        from_attributes=True,
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
                "is_active": True,
                "property_type": "principal",
                "parent_property_id": None
            }
        }
    )

class PropertyCreate(PropertyBase):
    """Schema for creating a new property"""
    model_config = ConfigDict(from_attributes=True)

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
    property_type: Optional[PropertyType] = Field(None, description="Tipo de propiedad (Principal o Unit)")
    parent_property_id: Optional[int] = Field(None, description="ID de la propiedad principal (solo para Units)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Casa Moderna Centro Actualizada",
                "monthly_rent": 2600.00,
                "status": "rented",
                "property_type": "unit",
                "parent_property_id": 1
            }
        }
    )

class Property(PropertyBase):
    """Schema for property responses"""
    id: int = Field(..., description="ID único de la propiedad")
    user_id: str = Field(..., description="ID del propietario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = ConfigDict(from_attributes=True)

class PropertyWithUnits(Property):
    """Schema for property response including its units"""
    units: List[Property] = Field(default_factory=list, description="Lista de unidades de la propiedad")
    
    @field_validator('property_type')
    @classmethod
    def validate_property_type(cls, v):
        if v != PropertyType.PRINCIPAL:
            raise ValueError("Solo las propiedades principales pueden tener unidades")
        return v
    
    @field_validator('units')
    @classmethod
    def validate_units(cls, v):
        for unit in v:
            if unit.property_type != PropertyType.UNIT:
                raise ValueError("Las unidades deben ser de tipo UNIT")
            if unit.parent_property_id is None:
                raise ValueError("Las unidades deben tener un parent_property_id")
        return v

    model_config = ConfigDict(from_attributes=True)

class PropertyFilter(BaseModel):
    """Schema for filtering properties"""
    city: Optional[str] = Field(None, description="Filtrar por ciudad")
    state: Optional[str] = Field(None, description="Filtrar por estado")
    min_price: Optional[float] = Field(None, ge=0, description="Precio mínimo de renta")
    max_price: Optional[float] = Field(None, ge=0, description="Precio máximo de renta")
    bedrooms: Optional[int] = Field(None, ge=0, description="Número mínimo de habitaciones")
    bathrooms: Optional[float] = Field(None, ge=0, description="Número mínimo de baños")
    status: Optional[PropertyStatus] = Field(None, description="Estado de la propiedad")
    property_type: Optional[PropertyType] = Field(None, description="Tipo de propiedad")
    parent_property_id: Optional[int] = Field(None, description="Filtrar por propiedad principal")

class PropertyBulkUpdate(BaseModel):
    """Schema for bulk updating properties"""
    ids: List[int] = Field(..., description="Lista de IDs de propiedades a actualizar")
    update: PropertyUpdate = Field(..., description="Datos a actualizar")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3],
                "update": {
                    "status": "maintenance",
                    "is_active": False
                }
            }
        }
    )
