"""
Configuración de pruebas para pytest.
Define fixtures y configuraciones comunes para todas las pruebas.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_test_token

# Configurar base de datos de prueba
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Crear un event loop para pruebas asíncronas"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Crear y configurar base de datos de prueba"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Proporcionar una sesión de base de datos para las pruebas"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session) -> Generator:
    """Crear un cliente de prueba para la API"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    """Proporcionar datos de usuario de prueba"""
    return {
        "id": "test_user_id",
        "email": "test@example.com",
        "name": "Test User",
        "roles": ["admin"]
    }

@pytest.fixture
def auth_headers(test_user):
    """Proporcionar headers de autenticación para las pruebas"""
    token = create_test_token(test_user)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_property():
    """Proporcionar datos de propiedad de prueba"""
    return {
        "title": "Test Property",
        "description": "A test property",
        "address": "123 Test St",
        "price": 1000.00,
        "bedrooms": 2,
        "bathrooms": 1,
        "square_meters": 100
    }

@pytest.fixture
def test_tenant():
    """Proporcionar datos de inquilino de prueba"""
    return {
        "name": "Test Tenant",
        "email": "tenant@example.com",
        "phone": "1234567890",
        "document_id": "ABC123"
    }

@pytest.fixture
def test_contract():
    """Proporcionar datos de contrato de prueba"""
    return {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "monthly_rent": 1000.00,
        "deposit": 2000.00
    }

@pytest.fixture
def test_payment():
    """Proporcionar datos de pago de prueba"""
    return {
        "amount": 1000.00,
        "payment_date": "2024-01-01",
        "payment_method": "credit_card",
        "status": "completed"
    }

@pytest.fixture
def test_maintenance():
    """Proporcionar datos de mantenimiento de prueba"""
    return {
        "title": "Test Maintenance",
        "description": "A test maintenance request",
        "priority": "high",
        "status": "pending"
    }
