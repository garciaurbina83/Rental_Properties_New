from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.property import (
    Property,
    PropertyCreate,
    PropertyUpdate,
    PropertyFilter,
    PropertyBulkUpdate
)
from ..models.property import PropertyStatus
from ..services import property_service
from ..dependencies.database import get_db
from ..dependencies.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/properties",
    tags=["properties"]
)

@router.post("/", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Property:
    """
    Crea una nueva propiedad
    """
    return await property_service.create_property(db, property, current_user)

@router.get("/", response_model=List[Property])
async def get_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    filters: Optional[PropertyFilter] = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> List[Property]:
    """
    Obtiene una lista de propiedades con filtros opcionales
    """
    filters_dict = filters.model_dump(exclude_unset=True) if filters else None
    return await property_service.get_properties(db, skip, limit, filters_dict)

@router.get("/{property_id}", response_model=Property)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> Property:
    """
    Obtiene una propiedad por su ID
    """
    return await property_service.get_property(db, property_id)

@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> Property:
    """
    Actualiza una propiedad existente
    """
    return await property_service.update_property(db, property_id, property_update)

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> None:
    """
    Elimina una propiedad (soft delete)
    """
    await property_service.delete_property(db, property_id)
    return None

@router.get("/metrics", response_model=Dict[str, Any])
async def get_property_metrics(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene métricas de las propiedades
    """
    return await property_service.get_property_metrics(db)

@router.get("/search/{search_term}", response_model=List[Property])
async def search_properties(
    search_term: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> List[Property]:
    """
    Búsqueda de propiedades por término
    """
    return await property_service.search_properties(db, search_term, skip, limit)

@router.get("/status/{status}", response_model=List[Property])
async def get_properties_by_status(
    status: PropertyStatus,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> List[Property]:
    """
    Obtiene propiedades por estado
    """
    return await property_service.get_properties_by_status(db, status, skip, limit)

@router.put("/bulk", response_model=List[Property])
async def bulk_update_properties(
    bulk_update: PropertyBulkUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)
) -> List[Property]:
    """
    Actualiza múltiples propiedades a la vez
    """
    updated_properties = []
    for property_id in bulk_update.ids:
        updated_property = await property_service.update_property(db, property_id, bulk_update.update)
        updated_properties.append(updated_property)
    return updated_properties
