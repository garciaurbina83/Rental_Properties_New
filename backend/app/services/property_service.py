from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ..models.property import Property, PropertyStatus
from ..schemas.property import PropertyCreate, PropertyUpdate
from fastapi import HTTPException, status

def get_properties(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Property]:
    """
    Obtiene una lista de propiedades con filtros opcionales
    """
    query = db.query(Property)
    
    if filters:
        if 'status' in filters:
            query = query.filter(Property.status == filters['status'])
        if 'city' in filters:
            query = query.filter(Property.city.ilike(f"%{filters['city']}%"))
        if 'min_price' in filters:
            query = query.filter(Property.monthly_rent >= filters['min_price'])
        if 'max_price' in filters:
            query = query.filter(Property.monthly_rent <= filters['max_price'])
        if 'bedrooms' in filters:
            query = query.filter(Property.bedrooms >= filters['bedrooms'])
        if 'bathrooms' in filters:
            query = query.filter(Property.bathrooms >= filters['bathrooms'])
        if 'is_active' in filters:
            query = query.filter(Property.is_active == filters['is_active'])
    
    return query.offset(skip).limit(limit).all()

def get_property(db: Session, property_id: int) -> Optional[Property]:
    """
    Obtiene una propiedad por su ID
    """
    return db.query(Property).filter(Property.id == property_id).first()

def create_property(db: Session, property: PropertyCreate) -> Property:
    """
    Crea una nueva propiedad
    """
    db_property = Property(**property.model_dump())
    db.add(db_property)
    try:
        db.commit()
        db.refresh(db_property)
        return db_property
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating property: {str(e)}"
        )

def update_property(
    db: Session,
    property_id: int,
    property_update: PropertyUpdate
) -> Optional[Property]:
    """
    Actualiza una propiedad existente
    """
    db_property = get_property(db, property_id)
    if db_property:
        update_data = property_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_property, field, value)
        try:
            db.commit()
            db.refresh(db_property)
            return db_property
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating property: {str(e)}"
            )
    return None

def delete_property(db: Session, property_id: int) -> bool:
    """
    Elimina una propiedad (soft delete)
    """
    db_property = get_property(db, property_id)
    if db_property:
        try:
            db_property.is_active = False
            db_property.status = PropertyStatus.INACTIVE
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting property: {str(e)}"
            )
    return False

def get_property_metrics(db: Session) -> Dict[str, Any]:
    """
    Obtiene métricas de las propiedades
    """
    total_properties = db.query(func.count(Property.id)).scalar()
    available_properties = db.query(func.count(Property.id))\
        .filter(Property.status == PropertyStatus.AVAILABLE).scalar()
    rented_properties = db.query(func.count(Property.id))\
        .filter(Property.status == PropertyStatus.RENTED).scalar()
    avg_rent = db.query(func.avg(Property.monthly_rent))\
        .filter(Property.monthly_rent > 0).scalar()
    
    return {
        "total_properties": total_properties,
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "average_monthly_rent": round(avg_rent if avg_rent else 0, 2),
        "occupancy_rate": round((rented_properties / total_properties * 100), 2) if total_properties > 0 else 0
    }

def search_properties(
    db: Session,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Property]:
    """
    Búsqueda de propiedades por término
    """
    return db.query(Property).filter(
        and_(
            Property.is_active == True,
            or_(
                Property.name.ilike(f"%{search_term}%"),
                Property.address.ilike(f"%{search_term}%"),
                Property.city.ilike(f"%{search_term}%"),
                Property.state.ilike(f"%{search_term}%")
            )
        )
    ).offset(skip).limit(limit).all()

def get_properties_by_status(
    db: Session,
    status: PropertyStatus,
    skip: int = 0,
    limit: int = 100
) -> List[Property]:
    """
    Obtiene propiedades por estado
    """
    return db.query(Property)\
        .filter(Property.status == status)\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_property_status(
    db: Session,
    property_id: int,
    new_status: PropertyStatus
) -> Optional[Property]:
    """
    Actualiza el estado de una propiedad
    """
    db_property = get_property(db, property_id)
    if db_property:
        try:
            db_property.status = new_status
            db.commit()
            db.refresh(db_property)
            return db_property
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating property status: {str(e)}"
            )
    return None
