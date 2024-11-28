from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ..models.property import Property, PropertyStatus
from ..schemas.property import PropertyCreate, PropertyUpdate
from fastapi import HTTPException, status

async def get_properties(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Property]:
    """
    Obtiene una lista de propiedades con filtros opcionales
    """
    query = select(Property).where(Property.is_active == True)
    
    if filters:
        conditions = []
        if 'status' in filters:
            try:
                status_enum = PropertyStatus(filters['status'].lower())
                conditions.append(Property.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
        if 'city' in filters:
            conditions.append(Property.city.ilike(f"%{filters['city']}%"))
        if 'min_price' in filters:
            conditions.append(Property.monthly_rent >= filters['min_price'])
        if 'max_price' in filters:
            conditions.append(Property.monthly_rent <= filters['max_price'])
        if 'bedrooms' in filters:
            conditions.append(Property.bedrooms >= filters['bedrooms'])
        if 'bathrooms' in filters:
            conditions.append(Property.bathrooms >= filters['bathrooms'])
        if conditions:
            query = query.where(and_(*conditions))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_property(db: AsyncSession, property_id: int) -> Optional[Property]:
    """
    Obtiene una propiedad por su ID
    """
    query = select(Property).where(
        and_(
            Property.id == property_id,
            Property.is_active == True
        )
    )
    result = await db.execute(query)
    property = result.scalar_one_or_none()
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    return property

async def create_property(db: AsyncSession, property: PropertyCreate, user_id: str) -> Property:
    """
    Crea una nueva propiedad
    """
    try:
        property_dict = property.model_dump()
        
        # Ensure status is properly set as enum
        if isinstance(property_dict.get('status'), str):
            try:
                property_dict['status'] = PropertyStatus(property_dict['status'].lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
        
        db_property = Property(**property_dict, user_id=user_id)
        db.add(db_property)
        await db.commit()
        await db.refresh(db_property)
        return db_property
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def update_property(
    db: AsyncSession,
    property_id: int,
    property_update: PropertyUpdate
) -> Optional[Property]:
    """
    Actualiza una propiedad existente
    """
    db_property = await get_property(db, property_id)
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    try:
        update_data = property_update.model_dump(exclude_unset=True)
        
        # Handle status update
        if 'status' in update_data and isinstance(update_data['status'], str):
            try:
                update_data['status'] = PropertyStatus(update_data['status'].lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
        
        for field, value in update_data.items():
            setattr(db_property, field, value)
            
        await db.commit()
        await db.refresh(db_property)
        return db_property
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def delete_property(db: AsyncSession, property_id: int) -> bool:
    """
    Elimina una propiedad (soft delete)
    """
    query = select(Property).where(
        and_(
            Property.id == property_id,
            Property.is_active == True
        )
    )
    result = await db.execute(query)
    db_property = result.scalar_one_or_none()
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    try:
        db_property.is_active = False
        db_property.status = PropertyStatus.INACTIVE
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting property: {str(e)}"
        )

async def get_property_metrics(db: AsyncSession) -> Dict[str, Any]:
    """
    Obtiene métricas de las propiedades
    """
    total_properties = await db.scalar(
        select(func.count(Property.id))\
        .where(Property.is_active == True)
    )
    available_properties = await db.scalar(
        select(func.count(Property.id))\
        .where(
            and_(
                Property.is_active == True,
                Property.status == PropertyStatus.AVAILABLE
            )
        )
    )
    rented_properties = await db.scalar(
        select(func.count(Property.id))\
        .where(
            and_(
                Property.is_active == True,
                Property.status == PropertyStatus.RENTED
            )
        )
    )
    avg_rent = await db.scalar(
        select(func.avg(Property.monthly_rent))\
        .where(
            and_(
                Property.is_active == True,
                Property.monthly_rent > 0
            )
        )
    )
    
    return {
        "total_properties": total_properties,
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "average_monthly_rent": round(avg_rent if avg_rent else 0, 2),
        "occupancy_rate": round((rented_properties / total_properties * 100), 2) if total_properties > 0 else 0
    }

async def search_properties(
    db: AsyncSession,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Property]:
    """
    Búsqueda de propiedades por término
    """
    query = select(Property).where(
        and_(
            Property.is_active == True,
            or_(
                Property.name.ilike(f"%{search_term}%"),
                Property.address.ilike(f"%{search_term}%"),
                Property.city.ilike(f"%{search_term}%"),
                Property.state.ilike(f"%{search_term}%")
            )
        )
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_properties_by_status(
    db: AsyncSession,
    status: PropertyStatus,
    skip: int = 0,
    limit: int = 100
) -> List[Property]:
    """
    Obtiene propiedades por estado
    """
    query = select(Property).where(
        and_(
            Property.is_active == True,
            Property.status == status
        )
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_property_status(
    db: AsyncSession,
    property_id: int,
    new_status: PropertyStatus
) -> Optional[Property]:
    """
    Actualiza el estado de una propiedad
    """
    db_property = await get_property(db, property_id)
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    try:
        db_property.status = new_status
        await db.commit()
        await db.refresh(db_property)
        return db_property
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating property status: {str(e)}"
        )
