from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from ....core.deps import get_db
from ....services.tenant_service import TenantService
from ....schemas.tenant import (
    Tenant,
    TenantCreate,
    TenantUpdate,
    TenantReference,
    TenantReferenceCreate,
    TenantDocument,
    TenantDocumentCreate,
    TenantStatus
)

router = APIRouter()

@router.post("/", response_model=Tenant, status_code=201)
async def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Crear un nuevo inquilino.
    """
    return await TenantService.create_tenant(db=db, tenant=tenant)

@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Obtener un inquilino por su ID.
    """
    return await TenantService.get_tenant(db=db, tenant_id=tenant_id)

@router.get("/", response_model=List[Tenant])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
) -> List[Tenant]:
    """
    Listar inquilinos con paginación y filtros opcionales.
    """
    return await TenantService.get_tenants(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )

@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_update: TenantUpdate,
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Actualizar información de un inquilino.
    """
    return await TenantService.update_tenant(
        db=db,
        tenant_id=tenant_id,
        tenant_update=tenant_update
    )

@router.put("/{tenant_id}/status", response_model=Tenant)
async def update_tenant_status(
    status: TenantStatus,
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Actualizar el estado de un inquilino.
    """
    return await TenantService.update_tenant_status(
        db=db,
        tenant_id=tenant_id,
        status=status
    )

@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> dict:
    """
    Eliminar un inquilino.
    """
    await TenantService.delete_tenant(db=db, tenant_id=tenant_id)
    return {"message": "Tenant deleted successfully"}

@router.post("/{tenant_id}/references", response_model=TenantReference)
async def add_tenant_reference(
    reference: TenantReferenceCreate,
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> TenantReference:
    """
    Agregar una referencia a un inquilino.
    """
    return await TenantService.add_tenant_reference(
        db=db,
        tenant_id=tenant_id,
        reference=reference
    )

@router.post("/{tenant_id}/documents", response_model=TenantDocument)
async def add_tenant_document(
    document: TenantDocumentCreate,
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    db: Session = Depends(get_db)
) -> TenantDocument:
    """
    Agregar un documento a un inquilino.
    """
    return await TenantService.add_tenant_document(
        db=db,
        tenant_id=tenant_id,
        document=document
    )

@router.get("/search/", response_model=List[Tenant])
async def search_tenants(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Tenant]:
    """
    Buscar inquilinos por nombre o email.
    """
    return await TenantService.search_tenants(
        db=db,
        search_term=q,
        skip=skip,
        limit=limit
    )

@router.get("/search/employer", response_model=List[Tenant])
async def search_tenants_by_employer(
    employer: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Tenant]:
    """
    Buscar inquilinos por empleador.
    """
    return await TenantService.search_tenants_by_employer(
        db=db,
        employer=employer,
        skip=skip,
        limit=limit
    )

@router.get("/search/income", response_model=List[Tenant])
async def filter_tenants_by_income(
    min_income: Optional[float] = Query(None, ge=0),
    max_income: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Tenant]:
    """
    Filtrar inquilinos por rango de ingresos mensuales.
    """
    return await TenantService.filter_tenants_by_income(
        db=db,
        min_income=min_income,
        max_income=max_income,
        skip=skip,
        limit=limit
    )
