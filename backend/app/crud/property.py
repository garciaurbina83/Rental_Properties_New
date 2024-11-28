from sqlalchemy.orm import Session
from ..models.property import Property
from ..schemas.property import PropertyCreate, PropertyUpdate
from fastapi import HTTPException

def create_property(db: Session, property_data: PropertyCreate, user_id: str) -> Property:
    """Create a new property"""
    db_property = Property(**property_data.model_dump(), user_id=user_id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def get_property(db: Session, property_id: int, user_id: str) -> Property:
    """Get a specific property by ID and verify ownership"""
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.user_id == user_id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

def get_properties(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 10
) -> list[Property]:
    """Get a list of properties with pagination for a specific user"""
    return db.query(Property).filter(
        Property.user_id == user_id
    ).offset(skip).limit(limit).all()

def update_property(
    db: Session,
    property_id: int,
    property_data: PropertyUpdate,
    user_id: str
) -> Property:
    """Update a property with ownership verification"""
    db_property = get_property(db=db, property_id=property_id, user_id=user_id)
    
    # Update only the fields that are not None
    property_data_dict = property_data.model_dump(exclude_unset=True)
    for field, value in property_data_dict.items():
        setattr(db_property, field, value)
    
    db.commit()
    db.refresh(db_property)
    return db_property

def delete_property(db: Session, property_id: int, user_id: str) -> bool:
    """Delete a property with ownership verification"""
    db_property = get_property(db=db, property_id=property_id, user_id=user_id)
    
    db.delete(db_property)
    db.commit()
    return True
