from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from ..models.tenant import Tenant, TenantStatus
from ..models.tenant_related import TenantReference, TenantDocument
from ..schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantReferenceCreate,
    TenantDocumentCreate
)

class TenantService:
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant: TenantCreate) -> Tenant:
        # Verificar si ya existe un inquilino con el mismo email
        stmt = select(Tenant).where(Tenant.email == tenant.email)
        result = await db.execute(stmt)
        existing_tenant = result.scalar_one_or_none()

        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear el nuevo inquilino
        new_tenant = Tenant(
            first_name=tenant.first_name,
            last_name=tenant.last_name,
            email=tenant.email,
            phone=tenant.phone,
            occupation=tenant.occupation,
            monthly_income=tenant.monthly_income,
            previous_address=tenant.previous_address,
            identification_type=tenant.identification_type,
            identification_number=tenant.identification_number,
            emergency_contact_name=tenant.emergency_contact_name,
            emergency_contact_phone=tenant.emergency_contact_phone,
            date_of_birth=tenant.date_of_birth,
            employer=tenant.employer,
            preferred_contact_method=tenant.preferred_contact_method,
            status=tenant.status
        )

        db.add(new_tenant)
        await db.commit()
        await db.refresh(new_tenant)

        # Crear referencias si existen
        if tenant.references:
            for ref in tenant.references:
                tenant_ref = TenantReference(
                    tenant_id=new_tenant.id,
                    name=ref.name,
                    ref_relationship=ref.ref_relationship,
                    phone=ref.phone,
                    email=ref.email,
                    notes=ref.notes
                )
                db.add(tenant_ref)

        # Crear documentos si existen
        if tenant.documents:
            for doc in tenant.documents:
                tenant_doc = TenantDocument(
                    tenant_id=new_tenant.id,
                    document_type=doc.document_type,
                    file_path=doc.file_path,
                    upload_date=doc.upload_date,
                    expiry_date=doc.expiry_date,
                    is_verified=doc.is_verified
                )
                db.add(tenant_doc)

        if tenant.references or tenant.documents:
            await db.commit()

        return new_tenant

    @staticmethod
    async def get_tenant(db: AsyncSession, tenant_id: int) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenants(db: AsyncSession) -> List[Tenant]:
        stmt = select(Tenant)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_tenant(db: AsyncSession, tenant_id: int, tenant: TenantUpdate) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        db_tenant = result.scalar_one_or_none()

        if not db_tenant:
            return None

        # Actualizar los campos del inquilino
        for field, value in tenant.dict(exclude_unset=True).items():
            setattr(db_tenant, field, value)

        await db.commit()
        await db.refresh(db_tenant)
        return db_tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: int) -> bool:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            return False

        await db.delete(tenant)
        await db.commit()
        return True

    @staticmethod
    async def search_tenants_by_employer(db: AsyncSession, employer: str) -> List[Tenant]:
        stmt = select(Tenant).where(Tenant.employer.ilike(f"%{employer}%"))
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def filter_tenants_by_income(db: AsyncSession, min_income: float, max_income: float) -> List[Tenant]:
        stmt = select(Tenant).where(
            Tenant.monthly_income >= min_income,
            Tenant.monthly_income <= max_income
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_tenant_status(db: AsyncSession, tenant_id: int, status: TenantStatus) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            return None

        tenant.status = status
        await db.commit()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def get_tenants(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Tenant]:
        query = select(Tenant)
        if is_active is not None:
            query = query.where(Tenant.is_active == is_active)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def search_tenants(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        stmt = select(Tenant).where(
            (Tenant.first_name.ilike(f"%{search_term}%")) |
            (Tenant.last_name.ilike(f"%{search_term}%")) |
            (Tenant.email.ilike(f"%{search_term}%"))
        )
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def add_tenant_reference(
        db: AsyncSession,
        tenant_id: int,
        reference: TenantReferenceCreate
    ) -> TenantReference:
        db_tenant = await TenantService.get_tenant(db, tenant_id)
        db_reference = TenantReference(**reference.dict(), tenant_id=tenant_id)
        db.add(db_reference)
        await db.commit()
        await db.refresh(db_reference)
        return db_reference

    @staticmethod
    async def add_tenant_document(
        db: AsyncSession,
        tenant_id: int,
        document: TenantDocumentCreate
    ) -> TenantDocument:
        db_tenant = await TenantService.get_tenant(db, tenant_id)
        db_document = TenantDocument(**document.dict(), tenant_id=tenant_id)
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)
        return db_document

    @staticmethod
    async def get_tenant_by_email(db: AsyncSession, email: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
