from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.property import Property
from ..schemas.property import PropertyCreate, PropertyUpdate, Property as PropertySchema, PropertyDetail
from ..crud.property import (
    create_property,
    get_property,
    get_properties,
    update_property,
    delete_property
)
from ..core.auth import get_current_user

router = APIRouter(
    prefix="/properties",
    tags=["properties"]
)

@router.post("/", response_model=PropertySchema)
def create_new_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new property"""
    return create_property(db=db, property_data=property_data)

@router.get("/", response_model=List[PropertySchema])
def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of properties with pagination"""
    return get_properties(db=db, skip=skip, limit=limit)

@router.get("/{property_id}", response_model=PropertyDetail)
def get_property_by_id(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific property by ID"""
    db_property = get_property(db=db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property

@router.put("/{property_id}", response_model=PropertySchema)
def update_property_by_id(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a property"""
    db_property = update_property(
        db=db,
        property_id=property_id,
        property_data=property_data
    )
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property

@router.delete("/{property_id}")
def delete_property_by_id(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a property"""
    success = delete_property(db=db, property_id=property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"}
