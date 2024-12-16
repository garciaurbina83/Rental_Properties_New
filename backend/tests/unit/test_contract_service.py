import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.contract_service import ContractService
from app.services.tenant_service import TenantService
from app.models.contract import Contract, ContractStatus, PaymentMethod, PaymentFrequency
from app.models.payment import Payment
from app.models.tenant import Tenant, TenantStatus, ContactMethod
from app.models.unit import Unit, UnitType
from app.models.property import Property, PropertyType, PropertyStatus
from app.schemas.tenant import TenantCreate
from app.schemas.contract import ContractCreate
from sqlalchemy import delete

@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession):
    """Limpiar la base de datos antes de cada prueba"""
    await db_session.execute(delete(Contract))
    await db_session.execute(delete(Unit))
    await db_session.execute(delete(Property))
    await db_session.execute(delete(Tenant))
    await db_session.commit()

@pytest.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Crear un inquilino de prueba"""
    tenant_data = TenantCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe.contract_service@test.com",
        phone="1234567890",
        occupation="Software Engineer",
        monthly_income=5000.0,
        previous_address="123 Old St",
        identification_type="DNI",
        identification_number="12345678",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        preferred_contact_method=ContactMethod.EMAIL,
        status=TenantStatus.ACTIVE
    )
    return await TenantService.create_tenant(db_session, tenant_data)

@pytest.fixture
async def test_property(db_session: AsyncSession) -> Property:
    """Crear una propiedad de prueba"""
    property = Property(
        name="Test Property",
        address="123 Test St",
        city="Test City",
        state="Test State",
        country="Test Country",
        postal_code="12345",
        property_type=PropertyType.APARTMENT_BUILDING,
        year_built=2000,
        total_units=10,
        status=PropertyStatus.ACTIVE
    )
    db_session.add(property)
    await db_session.commit()
    await db_session.refresh(property)
    return property

@pytest.fixture
async def test_unit(db_session: AsyncSession, test_property: Property) -> Unit:
    """Crear una unidad de prueba"""
    unit = Unit(
        property_id=test_property.id,
        unit_number="A1",
        floor=1,
        unit_type=UnitType.APARTMENT,
        bedrooms=2,
        bathrooms=1.0,
        total_area=100.0,
        furnished=True,
        is_available=True,
        is_active=True,
        base_rent=1000.0,
        description="Test unit",
        amenities="[]"
    )
    db_session.add(unit)
    await db_session.commit()
    await db_session.refresh(unit)
    return unit

@pytest.fixture
async def test_contract(db_session: AsyncSession, test_tenant: Tenant, test_unit: Unit) -> Contract:
    """Crear un contrato de prueba"""
    contract_data = ContractCreate(
        tenant_id=test_tenant.id,
        unit_id=test_unit.id,
        contract_number="CONT-001",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        rent_amount=1000.0,
        security_deposit=2000.0,
        payment_frequency=PaymentFrequency.MONTHLY,
        payment_due_day=5,
        payment_method=PaymentMethod.TRANSFER,
        terms_and_conditions="Standard terms",
        utilities_included={"water": True, "electricity": False},
        guarantor_info=None
    )
    return await ContractService.create_contract(db_session, contract_data)

@pytest.mark.asyncio
async def test_update_guarantor_info(db_session: AsyncSession, test_contract: Contract):
    """Probar actualización de información del garante"""
    guarantor_info = {
        "name": "Jane Smith",
        "phone": "1234567890",
        "email": "jane.smith@test.com",
        "relationship": "Family friend",
        "occupation": "Manager"
    }
    
    updated_contract = await ContractService.update_guarantor_info(
        db_session,
        test_contract.id,
        guarantor_info
    )
    
    assert updated_contract.guarantor_info == guarantor_info
    
    # Verificar que el cambio persiste en la base de datos
    contract = await ContractService.get_contract(db_session, test_contract.id)
    assert contract.guarantor_info == guarantor_info

@pytest.mark.asyncio
async def test_update_utilities(db_session: AsyncSession, test_contract: Contract):
    """Probar actualización de servicios incluidos"""
    utilities = {
        "water": True,
        "electricity": True,
        "gas": False,
        "internet": True,
        "cable": False
    }
    
    updated_contract = await ContractService.update_utilities(
        db_session,
        test_contract.id,
        utilities
    )
    
    assert updated_contract.utilities_included == utilities
    
    # Verificar que el cambio persiste en la base de datos
    contract = await ContractService.get_contract(db_session, test_contract.id)
    assert contract.utilities_included == utilities

@pytest.mark.asyncio
async def test_update_payment_method(db_session: AsyncSession, test_contract: Contract):
    """Probar actualización de método de pago"""
    # Cambiar a pago en efectivo
    updated_contract = await ContractService.update_payment_method(
        db_session,
        test_contract.id,
        PaymentMethod.CASH
    )
    
    assert updated_contract.payment_method == PaymentMethod.CASH
    
    # Verificar que el cambio persiste en la base de datos
    contract = await ContractService.get_contract(db_session, test_contract.id)
    assert contract.payment_method == PaymentMethod.CASH
    
    # Cambiar a pago con cheque
    updated_contract = await ContractService.update_payment_method(
        db_session,
        test_contract.id,
        PaymentMethod.CHECK
    )
    
    assert updated_contract.payment_method == PaymentMethod.CHECK
    contract = await ContractService.get_contract(db_session, test_contract.id)
    assert contract.payment_method == PaymentMethod.CHECK
