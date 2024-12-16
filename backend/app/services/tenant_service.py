from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from ..models.tenant import Tenant
from ..schemas.tenant import TenantCreate, TenantUpdate

class TenantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(self, tenant: TenantCreate) -> Tenant:
        new_tenant = Tenant(
            first_name=tenant.first_name,
            last_name=tenant.last_name,
            property_id=tenant.property_id,
            lease_start=tenant.lease_start,
            lease_end=tenant.lease_end,
            deposit=tenant.deposit,
            monthly_rent=tenant.monthly_rent,
            payment_day=tenant.payment_day
        )

        self.db.add(new_tenant)
        await self.db.commit()
        await self.db.refresh(new_tenant)
        return new_tenant

    async def get_tenant(self, tenant_id: int) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        stmt = select(Tenant).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_tenant(self, tenant_id: int, tenant_data: TenantUpdate) -> Optional[Tenant]:
        db_tenant = await self.get_tenant(tenant_id)
        if not db_tenant:
            return None

        tenant_data_dict = tenant_data.dict(exclude_unset=True)
        for field, value in tenant_data_dict.items():
            setattr(db_tenant, field, value)

        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def delete_tenant(self, tenant_id: int) -> bool:
        stmt = delete(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
