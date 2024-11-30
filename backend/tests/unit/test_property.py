"""
Unit tests for property models, schemas and services
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.models.property import Property, PropertyType
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyWithUnits
from app.services.property_service import PropertyService
from app.core.exceptions import BadRequestException, NotFoundException

@pytest.fixture
def mock_property_dict():
    return {
        "id": 1,
        "name": "Test Property",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.PRINCIPAL,
        "parent_property_id": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@pytest.fixture
def mock_unit_dict():
    return {
        "id": 2,
        "name": "Test Unit",
        "address": "123 Test St Unit 1",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.UNIT,
        "parent_property_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

def test_property_model_creation(mock_property_dict):
    """Test Property model instantiation"""
    property = Property(**mock_property_dict)
    assert property.id == mock_property_dict["id"]
    assert property.name == mock_property_dict["name"]
    assert property.property_type == PropertyType.PRINCIPAL
    assert property.parent_property_id is None

def test_property_create_schema():
    """Test PropertyCreate schema validation"""
    data = {
        "name": "Test Property",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.PRINCIPAL
    }
    schema = PropertyCreate(**data)
    assert schema.name == data["name"]
    assert schema.property_type == PropertyType.PRINCIPAL

def test_property_with_units_schema(mock_property_dict, mock_unit_dict):
    """Test PropertyWithUnits schema"""
    data = {
        **mock_property_dict,
        "units": [mock_unit_dict]
    }
    schema = PropertyWithUnits(**data)
    assert schema.id == mock_property_dict["id"]
    assert len(schema.units) == 1
    assert schema.units[0].id == mock_unit_dict["id"]

@pytest.mark.asyncio
async def test_create_principal_property():
    """Test creating a principal property through service"""
    mock_db = AsyncMock()
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = PropertyService(mock_db)
    property_data = PropertyCreate(
        name="Test Property",
        address="123 Test St",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="Test Country",
        property_type=PropertyType.PRINCIPAL
    )

    created_property = await service.create_property(property_data)
    assert created_property.name == property_data.name
    assert created_property.property_type == PropertyType.PRINCIPAL
    mock_db.add.assert_called_once()
    await mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_unit_invalid_parent():
    """Test creating a unit with non-existent parent property"""
    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=None)

    service = PropertyService(mock_db)
    unit_data = PropertyCreate(
        name="Test Unit",
        address="123 Test St Unit 1",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="Test Country",
        property_type=PropertyType.UNIT,
        parent_property_id=999
    )

    with pytest.raises(NotFoundException):
        await service.create_property(unit_data)

@pytest.mark.asyncio
async def test_create_unit_with_unit_parent(mock_property_dict, mock_unit_dict):
    """Test creating a unit with another unit as parent"""
    mock_db = AsyncMock()
    parent_unit = Property(**mock_unit_dict)
    mock_db.get = AsyncMock(return_value=parent_unit)

    service = PropertyService(mock_db)
    unit_data = PropertyCreate(
        name="Test Unit 2",
        address="123 Test St Unit 2",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="Test Country",
        property_type=PropertyType.UNIT,
        parent_property_id=parent_unit.id
    )

    with pytest.raises(BadRequestException):
        await service.create_property(unit_data)
