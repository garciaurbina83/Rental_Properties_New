import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.services.tenant_service import TenantService
from app.models.tenant import Tenant, TenantStatus, ContactMethod
from app.models.tenant_related import TenantReference, TenantDocument
from app.schemas.tenant import TenantCreate

@pytest.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Crear un inquilino de prueba"""
    tenant_data = TenantCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe.tenant_service@test.com",
        phone="1234567890",
        occupation="Software Engineer",
        monthly_income=5000.0,
        previous_address="123 Old St",
        identification_type="DNI",
        identification_number="12345678",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        date_of_birth=date(1990, 1, 1),
        employer="Tech Corp",
        preferred_contact_method=ContactMethod.EMAIL,
        status=TenantStatus.ACTIVE
    )
    tenant = await TenantService.create_tenant(db_session, tenant_data)
    return tenant

@pytest.fixture
async def test_tenant_search_employer(db_session: AsyncSession) -> Tenant:
    """Crear un inquilino de prueba para búsqueda por empleador"""
    tenant_data = TenantCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe.search_employer@test.com",
        phone="1234567890",
        occupation="Software Engineer",
        monthly_income=5000.0,
        previous_address="123 Old St",
        identification_type="DNI",
        identification_number="12345678",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        date_of_birth=date(1990, 1, 1),
        employer="Tech Corp",
        preferred_contact_method=ContactMethod.EMAIL,
        status=TenantStatus.ACTIVE
    )
    return await TenantService.create_tenant(db_session, tenant_data)

@pytest.fixture
async def test_tenant_filter_income(db_session: AsyncSession) -> Tenant:
    """Crear un inquilino de prueba para filtrado por ingresos"""
    tenant_data = TenantCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe.filter_income@test.com",
        phone="1234567890",
        occupation="Software Engineer",
        monthly_income=5000.0,
        previous_address="123 Old St",
        identification_type="DNI",
        identification_number="12345678",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        date_of_birth=date(1990, 1, 1),
        employer="Tech Corp",
        preferred_contact_method=ContactMethod.EMAIL,
        status=TenantStatus.ACTIVE
    )
    return await TenantService.create_tenant(db_session, tenant_data)

@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession):
    """Limpiar la base de datos antes de cada prueba"""
    await db_session.execute(delete(Tenant))
    await db_session.commit()

@pytest.mark.asyncio
async def test_update_tenant_status(db_session: AsyncSession, test_tenant: Tenant):
    """Probar actualización de estado del inquilino"""
    # Actualizar estado a INACTIVE
    updated_tenant = await TenantService.update_tenant_status(
        db_session,
        test_tenant.id,
        TenantStatus.INACTIVE
    )
    
    assert updated_tenant.status == TenantStatus.INACTIVE
    
    # Verificar que el cambio persiste en la base de datos
    tenant = await TenantService.get_tenant(db_session, test_tenant.id)
    assert tenant.status == TenantStatus.INACTIVE

@pytest.mark.asyncio
async def test_search_tenants_by_employer(db_session: AsyncSession, test_tenant_search_employer: Tenant):
    """Probar la búsqueda de inquilinos por empleador"""
    # Buscar por empleador exacto
    tenants = await TenantService.search_tenants_by_employer(
        db_session,
        "Tech Corp"
    )
    assert len(tenants) == 1
    assert tenants[0].id == test_tenant_search_employer.id
    
    # Buscar por parte del nombre del empleador
    tenants = await TenantService.search_tenants_by_employer(
        db_session,
        "Tech"
    )
    assert len(tenants) == 1
    
    # Buscar empleador que no existe
    tenants = await TenantService.search_tenants_by_employer(
        db_session,
        "Nonexistent Corp"
    )
    assert len(tenants) == 0

@pytest.mark.asyncio
async def test_filter_tenants_by_income(db_session: AsyncSession, test_tenant_filter_income: Tenant):
    """Probar el filtrado de inquilinos por ingresos"""
    # Crear otro inquilino con ingresos diferentes
    other_tenant_data = TenantCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith.tenant_service@test.com",
        phone="9876543210",
        occupation="Manager",
        monthly_income=8000.0,
        previous_address="456 New St",
        identification_type="DNI",
        identification_number="87654321",
        emergency_contact_name="John Smith",
        emergency_contact_phone="1234567890",
        date_of_birth=date(1992, 2, 2),
        employer="Other Corp",
        preferred_contact_method=ContactMethod.PHONE,
        status=TenantStatus.ACTIVE
    )
    await TenantService.create_tenant(db_session, other_tenant_data)
    
    # Filtrar por rango que incluye ambos inquilinos
    tenants = await TenantService.filter_tenants_by_income(
        db_session,
        min_income=4000.0,
        max_income=9000.0
    )
    assert len(tenants) == 2
    
    # Filtrar por rango que incluye solo el primer inquilino
    tenants = await TenantService.filter_tenants_by_income(
        db_session,
        max_income=6000.0
    )
    assert len(tenants) == 1
    assert tenants[0].id == test_tenant_filter_income.id
    
    # Filtrar por rango que incluye solo el segundo inquilino
    tenants = await TenantService.filter_tenants_by_income(
        db_session,
        min_income=7000.0
    )
    assert len(tenants) == 1
    assert tenants[0].monthly_income == 8000.0
    
    # Filtrar por rango que no incluye ningún inquilino
    tenants = await TenantService.filter_tenants_by_income(
        db_session,
        min_income=10000.0
    )
    assert len(tenants) == 0
