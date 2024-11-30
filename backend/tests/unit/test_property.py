"""
Unit tests for property models, schemas and services
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.models.property import Property, PropertyType, PropertyStatus
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyWithUnits
from app.services.property_service import PropertyService
from app.core.exceptions import BadRequestException, NotFoundException
from fastapi import status
from fastapi.exceptions import HTTPException

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
        "size": 150.5,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "parking_spots": 2,
        "property_type": PropertyType.PRINCIPAL,
        "parent_property_id": None,
        "user_id": "test_user",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": PropertyStatus.AVAILABLE,
        "is_active": True
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
        "size": 75.5,
        "bedrooms": 2,
        "bathrooms": 1.5,
        "parking_spots": 1,
        "property_type": PropertyType.UNIT,
        "parent_property_id": 1,
        "user_id": "test_user",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": PropertyStatus.AVAILABLE,
        "is_active": True
    }

def test_property_model_creation(mock_property_dict):
    """Test Property model instantiation"""
    property = Property(**mock_property_dict)
    assert property.id == mock_property_dict["id"]
    assert property.name == mock_property_dict["name"]
    assert property.property_type == PropertyType.PRINCIPAL
    assert property.parent_property_id is None
    assert property.size == mock_property_dict["size"]
    assert property.bedrooms == mock_property_dict["bedrooms"]
    assert property.bathrooms == mock_property_dict["bathrooms"]
    assert property.parking_spots == mock_property_dict["parking_spots"]

def test_property_create_schema():
    """Test PropertyCreate schema validation"""
    data = {
        "name": "Test Property",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "size": 150.5,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "parking_spots": 2,
        "property_type": PropertyType.PRINCIPAL
    }
    schema = PropertyCreate(**data)
    assert schema.name == data["name"]
    assert schema.property_type == PropertyType.PRINCIPAL
    assert schema.size == data["size"]
    assert schema.bedrooms == data["bedrooms"]
    assert schema.bathrooms == data["bathrooms"]
    assert schema.parking_spots == data["parking_spots"]

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
        size=150.5,
        bedrooms=3,
        bathrooms=2.5,
        parking_spots=2,
        property_type=PropertyType.PRINCIPAL
    )

    # Mock the created property
    created_property = Property(
        id=1,
        user_id="test_user",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **property_data.model_dump()
    )
    mock_db.refresh.side_effect = lambda x: setattr(x, 'id', created_property.id)

    result = await service.create_property(property_data, user_id="test_user")
    assert result.name == property_data.name
    assert result.property_type == PropertyType.PRINCIPAL
    assert result.size == property_data.size
    assert result.bedrooms == property_data.bedrooms
    assert result.bathrooms == property_data.bathrooms
    assert result.parking_spots == property_data.parking_spots
    assert result.user_id == "test_user"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_unit_invalid_parent():
    """Test creating a unit with non-existent parent property"""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = PropertyService(mock_db)
    # Mock get_property to raise HTTPException
    service.get_property = AsyncMock(side_effect=HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Parent property with id 999 not found"
    ))

    unit_data = PropertyCreate(
        name="Test Unit",
        address="123 Test St Unit 1",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="Test Country",
        size=75.5,
        bedrooms=2,
        bathrooms=1.5,
        parking_spots=1,
        property_type=PropertyType.UNIT,
        parent_property_id=999
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_property(unit_data, user_id="test_user")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Parent property with id 999 not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_create_unit_with_unit_parent(mock_property_dict, mock_unit_dict):
    """Test creating a unit with another unit as parent"""
    mock_db = AsyncMock()
    parent_unit = Property(**mock_unit_dict)
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = parent_unit
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = PropertyService(mock_db)
    # Mock get_property to return a unit property
    service.get_property = AsyncMock(return_value=parent_unit)

    unit_data = PropertyCreate(
        name="Test Unit 2",
        address="123 Test St Unit 2",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="Test Country",
        size=75.5,
        bedrooms=2,
        bathrooms=1.5,
        parking_spots=1,
        property_type=PropertyType.UNIT,
        parent_property_id=parent_unit.id
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_property(unit_data, user_id="test_user")
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Units can only be created under principal properties" in str(exc_info.value.detail)
