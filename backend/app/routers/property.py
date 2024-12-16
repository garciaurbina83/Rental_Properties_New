from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db
from ..services.property_service import PropertyService
from ..schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    Property,
    PropertyFilter,
    PropertyBulkUpdate,
    PropertyWithUnits
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
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"])),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    filters: PropertyFilter = Depends()
):
    """
    Obtiene una lista de propiedades con filtros opcionales.
    """
    property_service = PropertyService(db)
    return await property_service.get_properties(
        user_id=user_id,
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
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Crea una nueva propiedad.
    """
    property_service = PropertyService(db)
    try:
        property = await property_service.create_property(property_data, current_user["sub"])
        return property
    except Exception as e:
        print(f"Error creating property: {str(e)}")
        raise

@router.put(
    "/properties/bulk",
    response_model=List[Property],
    summary="Actualización masiva de propiedades",
    description="""
    Actualiza múltiples propiedades al mismo tiempo.
    Requiere el permiso 'property:write'.
    """,
)
async def bulk_update_properties(
    update_data: PropertyBulkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Actualiza múltiples propiedades en masa.
    """
    property_service = PropertyService(db)
    return await property_service.bulk_update_properties(
        update_data.ids, update_data.update
    )

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
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene una propiedad por su ID.
    """
    property_service = PropertyService(db)
    property = await property_service.get_property(property_id)
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
    property_data: PropertyUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Actualiza una propiedad existente.
    """
    property_service = PropertyService(db)
    updated_property = await property_service.update_property(property_id, property_data)
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
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:delete"]))
):
    """
    Elimina una propiedad (soft delete).
    """
    property_service = PropertyService(db)
    if not await property_service.delete_property(property_id):
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
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene métricas de las propiedades.
    """
    property_service = PropertyService(db)
    return await property_service.get_property_metrics()

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
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"])),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Busca propiedades por término.
    """
    property_service = PropertyService(db)
    return await property_service.search_properties(q, skip=skip, limit=limit)

@router.post(
    "/properties/{principal_id}/units",
    response_model=Property,
    status_code=201,
    summary="Crear nueva unidad",
    description="""
    Crea una nueva unidad asociada a una propiedad principal.
    La unidad se creará automáticamente con tipo UNIT y asociada a la propiedad principal especificada.
    Requiere el permiso 'property:write'.
    """,
    responses={
        201: {
            "description": "Unidad creada exitosamente",
            "model": Property
        },
        404: {
            "description": "Propiedad principal no encontrada"
        },
        422: {
            "description": "Error de validación - La propiedad principal no es válida"
        }
    }
)
async def create_unit(
    principal_id: int = Path(..., gt=0, description="ID de la propiedad principal"),
    unit_data: PropertyCreate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:write"]))
):
    """
    Crea una nueva unidad asociada a una propiedad principal.
    """
    property_service = PropertyService(db)
    try:
        unit = await property_service.create_unit(principal_id, unit_data, current_user["sub"])
        return unit
    except Exception as e:
        print(f"Error creating unit: {str(e)}")
        raise

@router.get(
    "/properties/{principal_id}/units",
    response_model=List[Property],
    summary="Obtener unidades de una propiedad",
    description="""
    Obtiene todas las unidades asociadas a una propiedad principal.
    Requiere el permiso 'property:read'.
    """,
    responses={
        404: {
            "description": "Propiedad principal no encontrada"
        },
        422: {
            "description": "Error de validación - La propiedad especificada no es principal"
        }
    }
)
async def get_property_units(
    principal_id: int = Path(..., gt=0, description="ID de la propiedad principal"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene todas las unidades de una propiedad principal.
    """
    property_service = PropertyService(db)
    return await property_service.get_units_by_principal(principal_id)

@router.get(
    "/properties/{property_id}/with-units",
    response_model=PropertyWithUnits,
    summary="Obtener propiedad con sus unidades",
    description="""
    Obtiene los detalles de una propiedad principal junto con todas sus unidades.
    Si la propiedad no es de tipo principal, se retornará un error.
    Requiere el permiso 'property:read'.
    """,
    responses={
        404: {
            "description": "Propiedad no encontrada"
        },
        422: {
            "description": "Error de validación - La propiedad no es de tipo principal"
        }
    }
)
async def get_property_with_units(
    property_id: int = Path(..., gt=0, description="ID de la propiedad"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["property:read"]))
):
    """
    Obtiene una propiedad principal con todas sus unidades.
    """
    property_service = PropertyService(db)
    return await property_service.get_property_with_units(property_id)
