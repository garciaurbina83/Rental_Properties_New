from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

class PropertyType(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    UNIT = "UNIT"

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"

class PropertyBase(BaseModel):
    """Base schema for property data"""
    name: Optional[str] = Field(None, max_length=255)
    address: str = Field(..., max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = Field("available", max_length=50)
    is_active: Optional[bool] = True
    property_type: str = Field(..., max_length=50)
    parent_property_id: Optional[int] = None

    @validator("property_type")
    def validate_property_type(cls, v):
        if v not in ["PRINCIPAL", "UNIT"]:
            raise ValueError("property_type must be either 'PRINCIPAL' or 'UNIT'")
        return v

    @validator("status")
    def validate_status(cls, v):
        if v and v not in ["available", "rented"]:
            raise ValueError("status must be either 'available' or 'rented'")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Casa en venta",
                "address": "Calle Principal 123",
                "city": "Ciudad",
                "state": "Estado",
                "zip_code": "12345",
                "bedrooms": 3,
                "bathrooms": 2,
                "status": "available",
                "property_type": "PRINCIPAL"
            }
        }
    )

class PropertyCreate(PropertyBase):
    """Schema for creating a new property"""
    pass

class PropertyUpdate(BaseModel):
    """Schema for updating an existing property"""
    name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    property_type: Optional[str] = Field(None, max_length=50)
    parent_property_id: Optional[int] = None

    @validator("property_type")
    def validate_property_type(cls, v):
        if v and v not in ["PRINCIPAL", "UNIT"]:
            raise ValueError("property_type must be either 'PRINCIPAL' or 'UNIT'")
        return v

    @validator("status")
    def validate_status(cls, v):
        if v and v not in ["available", "rented"]:
            raise ValueError("status must be either 'available' or 'rented'")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "status": "rented"
            }
        }
    )

class PropertyResponse(PropertyBase):
    """Schema for property responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PropertyFilter(BaseModel):
    """Schema for filtering properties"""
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None
    property_type: Optional[str] = None
    parent_property_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
