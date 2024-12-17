"""
API endpoints for property management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.property import Property, PropertyType, PropertyStatus
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse
)
from app.services.property_service import PropertyService

router = APIRouter()

@router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    bedrooms: Optional[int] = Query(None),
    bathrooms: Optional[int] = Query(None),
    status: Optional[PropertyStatus] = Query(None),
    property_type: Optional[PropertyType] = Query(None),
    parent_property_id: Optional[int] = Query(None)
) -> List[PropertyResponse]:
    """Get all properties with optional filtering"""
    property_service = PropertyService(db)
    
    # Construir filtros
    filters = {}
    if city:
        filters["city"] = city
    if state:
        filters["state"] = state
    if bedrooms:
        filters["bedrooms"] = bedrooms
    if bathrooms:
        filters["bathrooms"] = bathrooms
    if status:
        filters["status"] = status.value
    if property_type:
        filters["property_type"] = property_type.value
    if parent_property_id:
        filters["parent_property_id"] = parent_property_id
    
    return await property_service.get_properties(skip=skip, limit=limit, filters=filters)

@router.post("/properties", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db)
) -> PropertyResponse:
    """Create a new property"""
    property_service = PropertyService(db)
    # Por ahora usaremos un user_id fijo para pruebas
    return await property_service.create_property(property_data, user_id="1")

@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
) -> PropertyResponse:
    """Get a specific property by ID"""
    property_service = PropertyService(db)
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with id {property_id} not found"
        )
    return property

@router.put("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: AsyncSession = Depends(get_db)
) -> PropertyResponse:
    """Update a property"""
    property_service = PropertyService(db)
    property = await property_service.update_property(property_id, property_data)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with id {property_id} not found"
        )
    return property

@router.delete("/properties/{property_id}")
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a property"""
    property_service = PropertyService(db)
    success = await property_service.delete_property(property_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with id {property_id} not found"
        )
    return {"status": "success", "message": f"Property with id {property_id} deleted"}
