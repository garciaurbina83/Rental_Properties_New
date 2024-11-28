from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..services import property_service
from ..schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    Property,
    PropertyFilter
)
from ..core.security import get_current_user, check_permissions

router = APIRouter()

@router.get(
    "/properties",
    response_model=List[Property],
    summary="Obtener lista de propiedades",
    description="""
    Obtiene una lista paginada de propiedades.
    Se pueden aplicar filtros por estado, ciudad, precio, etc.
    Requiere el permiso 'property:read'.
    """,
)
async def get_properties(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"])),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    filters: PropertyFilter = Depends()
):
    """
    Obtiene una lista de propiedades con filtros opcionales.
    """
    return property_service.get_properties(
        db,
        skip=skip,
        limit=limit,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post(
    "/properties",
    response_model=Property,
    status_code=201,
    summary="Crear nueva propiedad",
    description="""
    Crea una nueva propiedad en el sistema.
    Requiere el permiso 'property:write'.
    """,
    responses={
        201: {
            "description": "Propiedad creada exitosamente",
            "model": Property
        },
        422: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "name"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Crea una nueva propiedad.
    """
    return property_service.create_property(db, property_data, current_user["id"])

@router.get(
    "/properties/{property_id}",
    response_model=Property,
    summary="Obtener propiedad por ID",
    description="""
    Obtiene los detalles de una propiedad específica por su ID.
    Requiere el permiso 'property:read'.
    """,
)
async def get_property(
    property_id: int = Path(..., gt=0, description="ID de la propiedad"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene una propiedad por su ID.
    """
    property = property_service.get_property(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return property

@router.put(
    "/properties/{property_id}",
    response_model=Property,
    summary="Actualizar propiedad",
    description="""
    Actualiza los datos de una propiedad existente.
    Requiere el permiso 'property:write'.
    """,
)
async def update_property(
    property_id: int = Path(..., gt=0, description="ID de la propiedad"),
    property_data: PropertyUpdate = Depends(),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Actualiza una propiedad existente.
    """
    updated_property = property_service.update_property(db, property_id, property_data)
    if not updated_property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return updated_property

@router.delete(
    "/properties/{property_id}",
    status_code=204,
    summary="Eliminar propiedad",
    description="""
    Elimina una propiedad del sistema (soft delete).
    Requiere el permiso 'property:delete'.
    """,
)
async def delete_property(
    property_id: int = Path(..., gt=0, description="ID de la propiedad"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:delete"]))
):
    """
    Elimina una propiedad (soft delete).
    """
    if not property_service.delete_property(db, property_id):
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

@router.get(
    "/properties/metrics",
    summary="Obtener métricas de propiedades",
    description="""
    Obtiene métricas generales sobre las propiedades.
    Requiere el permiso 'property:read'.
    """,
)
async def get_property_metrics(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene métricas de las propiedades.
    """
    return property_service.get_property_metrics(db)

@router.get(
    "/properties/search",
    response_model=List[Property],
    summary="Buscar propiedades",
    description="""
    Busca propiedades por término en nombre, dirección, ciudad o estado.
    Requiere el permiso 'property:read'.
    """,
)
async def search_properties(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"])),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Busca propiedades por término.
    """
    return property_service.search_properties(db, q, skip=skip, limit=limit)

@router.patch(
    "/properties/{property_id}/status",
    response_model=Property,
    summary="Actualizar estado de propiedad",
    description="""
    Actualiza el estado de una propiedad.
    Requiere el permiso 'property:write'.
    """,
)
async def update_property_status(
    property_id: int = Path(..., gt=0, description="ID de la propiedad"),
    status: str = Query(..., description="Nuevo estado de la propiedad"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Actualiza el estado de una propiedad.
    """
    updated_property = property_service.update_property_status(db, property_id, status)
    if not updated_property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return updated_property
