"""
Pytest configuration file
"""
import asyncio
from datetime import datetime, timezone
import pytest
from typing import AsyncGenerator, Generator, Dict
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from app.core.settings import Settings
from app.core.database import get_db
from app.main import app
from app.models.base import Base
from app.core.test_auth import create_test_token, get_test_user
from app.core.auth import get_current_user
from app.core.security import get_current_user

settings = Settings()

# Create async engine for testing
# Ensure we're using asyncpg driver
test_engine = create_async_engine(
    settings.database_test_url.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=NullPool,
    echo=settings.debug
)

# Create async session factory
test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    """Yield the SQLAlchemy engine"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield a SQLAlchemy session"""
    async with test_async_session() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, auth_headers: Dict[str, str]) -> AsyncGenerator[AsyncClient, None]:
    """Yield a test client with a clean database session"""
    async def _get_test_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    # Override database dependency
    app.dependency_overrides[get_db] = _get_test_db
    
    # Override auth dependency with test auth
    app.dependency_overrides[get_current_user] = get_test_user

    async with AsyncClient(
        app=app,
        base_url="http://localhost:8000",
        headers=auth_headers,
        follow_redirects=True
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Create authorization headers with a test token"""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_property_data() -> Dict[str, any]:
    """Get test property data"""
    return {
        "name": "Test Property",
        "address": "123 Test St",
        "city": "Test City",
        "state": "Test State",
        "zip_code": "12345",
        "country": "Test Country",
        "size": 1000.0,
        "bedrooms": 2,
        "bathrooms": 2.0,
        "parking_spots": 1,
        "purchase_price": 200000.0,
        "current_value": 250000.0,
        "monthly_rent": 1000.0,
        "status": "available",  # Use lowercase status to match the enum
        "is_active": True,
        "user_id": "test_user_id"
    }

@pytest.fixture
def selenium_driver(request):
    """Create a Selenium WebDriver instance for e2e tests"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def pytest_collection_modifyitems(config, items):
    """Modify test items in place to ensure test classes run in order."""
    MARKS = {
        "unit": pytest.mark.unit,
        "integration": pytest.mark.integration,
        "e2e": pytest.mark.e2e
    }

    for item in items:
        for name, mark in MARKS.items():
            if name in item.keywords:
                item.add_marker(mark)
