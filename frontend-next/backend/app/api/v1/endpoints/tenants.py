"""
API endpoints for tenant management
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_session
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse
)

router = APIRouter(
    prefix="/tenants",
    tags=["tenants"]
)

@router.post("", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Create a new tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    return await tenant_service.create_tenant(tenant_data)

@router.get("", response_model=List[TenantResponse])
async def get_tenants(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
) -> List[TenantResponse]:
    """Get all tenants"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    return await tenant_service.get_tenants(skip=skip, limit=limit)

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Get a specific tenant by ID"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant

@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Update a tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    tenant = await tenant_service.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    """Delete a tenant"""
    from app.services.tenant_service import TenantService
    tenant_service = TenantService(db)
    deleted = await tenant_service.delete_tenant(tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
