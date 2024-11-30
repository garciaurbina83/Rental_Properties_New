"""
API endpoints for property management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_session
from app.core.auth import get_current_user
from app.models.property import Property, PropertyStatus
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyBulkUpdate
)

router = APIRouter()

@router.post("", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Property:
    """Create a new property"""
    from app.services.property_service import PropertyService
    property_service = PropertyService(db)
    return await property_service.create_property(property_data, current_user["id"])

@router.get("", response_model=List[PropertyResponse])
async def get_properties(
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[Property]:
    """Get all properties for the current user"""
    from app.services.property_service import PropertyService
    property_service = PropertyService(db)
    return await property_service.get_properties(skip=skip, limit=limit, filters={"user_id": current_user["id"]})

@router.put("/actions/bulk-update", response_model=List[PropertyResponse])
async def bulk_update_properties(
    bulk_update: PropertyBulkUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Property]:
    """Bulk update properties"""
    # First verify all properties exist and belong to user
    query = select(Property).filter(
        Property.id.in_(bulk_update.ids),
        Property.user_id == current_user["id"]
    )
    result = await db.execute(query)
    properties = result.scalars().all()
    
    if len(properties) != len(bulk_update.ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more properties not found"
        )
    
    # Get validated update data
    update_data = bulk_update.update.dict(exclude_unset=True)
    
    # If status is being updated, validate it's a valid enum value
    if "status" in update_data:
        status_value = update_data["status"]
        if isinstance(status_value, str):
            try:
                update_data["status"] = PropertyStatus(status_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
    
    # Perform bulk update
    stmt = update(Property).where(
        Property.id.in_(bulk_update.ids),
        Property.user_id == current_user["id"]
    ).values(**update_data)
    
    await db.execute(stmt)
    await db.commit()
    
    # Return updated properties
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Property:
    """Get a specific property by ID"""
    query = select(Property).filter(
        Property.id == property_id,
        Property.user_id == current_user["id"]
    )
    
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property_obj

@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Property:
    """Update a property"""
    query = select(Property).filter(
        Property.id == property_id,
        Property.user_id == current_user["id"]
    )
    
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    for field, value in property_data.dict(exclude_unset=True).items():
        setattr(property_obj, field, value)
    
    await db.commit()
    await db.refresh(property_obj)
    return property_obj

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
    """Delete a property"""
    query = select(Property).filter(
        Property.id == property_id,
        Property.user_id == current_user["id"]
    )
    
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    await db.delete(property_obj)
    await db.commit()
