from pydantic import BaseModel, Field
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
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1)
    city: str
    state: str
    zip_code: str
    country: str
    size: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    parking_spots: int = Field(..., ge=0)
    purchase_price: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)
    monthly_rent: Optional[float] = Field(None, ge=0)
    status: PropertyStatus = Field(default=PropertyStatus.AVAILABLE)
    is_active: bool = True

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(PropertyBase):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    size: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    parking_spots: Optional[int] = None

class Property(PropertyBase, BaseSchema):
    user_id: str = Field(..., description="ID of the property owner")
    
    class Config:
        from_attributes = True

class PropertyFilter(BaseModel):
    """Schema for property filtering parameters"""
    city: Optional[str] = None
    state: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_size: Optional[float] = Field(None, ge=0)
    max_size: Optional[float] = Field(None, ge=0)
    min_bedrooms: Optional[int] = Field(None, ge=0)
    max_bedrooms: Optional[int] = Field(None, ge=0)
    min_bathrooms: Optional[float] = Field(None, ge=0)
    max_bathrooms: Optional[float] = Field(None, ge=0)
    status: Optional[PropertyStatus] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class PropertyDetail(Property):
    contracts: List["ContractBase"] = []
    maintenance_tickets: List["MaintenanceTicketBase"] = []
    expenses: List["ExpenseBase"] = []
    loans: List["LoanBase"] = []
