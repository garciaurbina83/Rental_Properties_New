from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from fastapi import HTTPException, status
from ..models.tenant import Tenant
from ..models.property import Property, PropertyStatus
from ..schemas.tenant import TenantCreate, TenantUpdate

class TenantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_property(self, property_id: int) -> Property:
        """Get property and verify it exists"""
        stmt = select(Property).where(Property.id == property_id)
        result = await self.db.execute(stmt)
        property = result.scalar_one_or_none()
        
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with id {property_id} not found"
            )
        return property

    async def create_tenant(self, tenant: TenantCreate) -> Tenant:
        # Verificar que la propiedad existe y está disponible
        property = await self.get_property(tenant.property_id)
        
        # Verificar si la propiedad ya tiene inquilinos activos
        current_date = func.current_date()
        stmt = select(Tenant).where(
            Tenant.property_id == tenant.property_id,
            Tenant.lease_end >= current_date
        )
        result = await self.db.execute(stmt)
        active_tenants = result.scalars().all()
        
        if active_tenants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is already rented"
            )

        # Crear el inquilino
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

        # Actualizar el estado de la propiedad
        property.status = PropertyStatus.RENTED.value
        
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
        # Obtener el inquilino
        db_tenant = await self.get_tenant(tenant_id)
        if not db_tenant:
            return None

        # Si se está actualizando la propiedad
        if tenant_data.property_id and tenant_data.property_id != db_tenant.property_id:
            # Verificar que la nueva propiedad existe y está disponible
            new_property = await self.get_property(tenant_data.property_id)
            if new_property.status == PropertyStatus.RENTED.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New property is already rented"
                )
            
            # Actualizar estados de las propiedades
            old_property = await self.get_property(db_tenant.property_id)
            old_property.update_status_from_tenants()
            new_property.status = PropertyStatus.RENTED.value

        # Actualizar el inquilino
        tenant_data_dict = tenant_data.dict(exclude_unset=True)
        for field, value in tenant_data_dict.items():
            setattr(db_tenant, field, value)

        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def delete_tenant(self, tenant_id: int) -> bool:
        # Obtener el inquilino
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False

        # Obtener y actualizar la propiedad
        property = await self.get_property(tenant.property_id)
        
        # Eliminar el inquilino
        stmt = delete(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(stmt)
        
        if result.rowcount > 0:
            # Actualizar el estado de la propiedad
            property.update_status_from_tenants()
            await self.db.commit()
            return True
            
        return False
