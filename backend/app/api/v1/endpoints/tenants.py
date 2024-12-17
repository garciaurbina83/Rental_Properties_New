"""
API endpoints for tenant management
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse
)

router = APIRouter()  

@router.get("/tenants", response_model=List[TenantResponse])
async def get_tenants(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[TenantResponse]:
    """Get all tenants"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    return await tenant_service.get_tenants(skip=skip, limit=limit)

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """Get a specific tenant by ID"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    return tenant

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """Create a new tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    return await tenant_service.create_tenant(tenant_data)

@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """Update a tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    tenant = await tenant_service.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    return tenant

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Delete a tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    success = await tenant_service.delete_tenant(tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    return {"status": "success", "message": f"Tenant with id {tenant_id} deleted"}
