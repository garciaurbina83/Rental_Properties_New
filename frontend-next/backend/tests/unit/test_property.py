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

@pytest.mark.asyncio
async def test_create_unit_success():
    """Test successful creation of a unit under a principal property"""
    # Mock database session
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Create service instance
    service = PropertyService(mock_db)
    
    # Mock get_property to return a principal property
    principal_property = Property(**{
        "id": 1,
        "property_type": PropertyType.PRINCIPAL,
        "name": "Principal Property",
        "address": "123 Main St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "size": 200.0,
        "bedrooms": 4,
        "bathrooms": 3.0,
        "parking_spots": 2,
        "user_id": "test_user",
        "is_active": True
    })
    
    with patch.object(service, 'get_property', return_value=principal_property):
        # Create unit data
        unit_data = PropertyCreate(
            name="Test Unit",
            address="123 Main St Unit 1",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="Test Country",
            size=75.0,
            bedrooms=2,
            bathrooms=1.0,
            parking_spots=1,
            property_type=PropertyType.UNIT,
            parent_property_id=1
        )
        
        # Create the unit
        unit = await service.create_unit(1, unit_data, "test_user")
        
        # Verify the unit was created correctly
        assert unit.property_type == PropertyType.UNIT
        assert unit.parent_property_id == 1
        assert unit.name == "Test Unit"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_property_with_units():
    """Test getting a principal property with its units"""
    # Mock database session
    mock_db = AsyncMock()
    
    # Create service instance
    service = PropertyService(mock_db)
    
    # Create mock principal property
    principal = Property(**{
        "id": 1,
        "property_type": PropertyType.PRINCIPAL,
        "name": "Principal Property",
        "address": "123 Main St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "size": 200.0,
        "bedrooms": 4,
        "bathrooms": 3.0,
        "parking_spots": 2,
        "user_id": "test_user",
        "is_active": True
    })
    
    # Create mock units
    units = [
        Property(**{
            "id": i,
            "property_type": PropertyType.UNIT,
            "parent_property_id": 1,
            "name": f"Unit {i}",
            "address": f"123 Main St Unit {i}",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "Test Country",
            "size": 75.0,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "parking_spots": 1,
            "user_id": "test_user",
            "is_active": True
        }) for i in range(2, 4)
    ]
    
    # Mock the database queries
    mock_db.execute.return_value.scalar_one_or_none.return_value = principal
    mock_db.execute.return_value.scalars.return_value.all.return_value = units
    
    # Get the property with units
    result = await service.get_property_with_units(1)
    
    # Verify the result
    assert result.id == 1
    assert result.property_type == PropertyType.PRINCIPAL
    assert len(result.units) == 2
    assert all(unit.property_type == PropertyType.UNIT for unit in result.units)
    assert all(unit.parent_property_id == 1 for unit in result.units)

@pytest.mark.asyncio
async def test_unit_cannot_have_units():
    """Test that a unit cannot have sub-units"""
    # Mock database session
    mock_db = AsyncMock()
    
    # Create service instance
    service = PropertyService(mock_db)
    
    # Create mock unit property
    unit = Property(**{
        "id": 2,
        "property_type": PropertyType.UNIT,
        "parent_property_id": 1,
        "name": "Unit 1",
        "address": "123 Main St Unit 1",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "size": 75.0,
        "bedrooms": 2,
        "bathrooms": 1.0,
        "parking_spots": 1,
        "user_id": "test_user",
        "is_active": True
    })
    
    # Mock get_property to return a unit
    with patch.object(service, 'get_property', return_value=unit):
        # Try to create a sub-unit
        sub_unit_data = PropertyCreate(
            name="Sub Unit",
            address="123 Main St Unit 1-A",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="Test Country",
            size=50.0,
            bedrooms=1,
            bathrooms=1.0,
            parking_spots=1,
            property_type=PropertyType.UNIT,
            parent_property_id=2
        )
        
        # Verify that creating a sub-unit raises an error
        with pytest.raises(HTTPException) as exc_info:
            await service.create_unit(2, sub_unit_data, "test_user")
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Units can only be created under principal properties" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_bulk_update_with_units():
    """Test bulk updating properties while respecting the hierarchy"""
    # Mock database session
    mock_db = AsyncMock()
    
    # Create service instance
    service = PropertyService(mock_db)
    
    # Create mock properties (1 principal with 2 units)
    properties = [
        Property(**{
            "id": 1,
            "property_type": PropertyType.PRINCIPAL,
            "name": "Principal Property",
            "address": "123 Main St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "Test Country",
            "size": 200.0,
            "bedrooms": 4,
            "bathrooms": 3.0,
            "parking_spots": 2,
            "user_id": "test_user",
            "is_active": True
        }),
        Property(**{
            "id": 2,
            "property_type": PropertyType.UNIT,
            "parent_property_id": 1,
            "name": "Unit 1",
            "address": "123 Main St Unit 1",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "Test Country",
            "size": 75.0,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "parking_spots": 1,
            "user_id": "test_user",
            "is_active": True
        }),
        Property(**{
            "id": 3,
            "property_type": PropertyType.UNIT,
            "parent_property_id": 1,
            "name": "Unit 2",
            "address": "123 Main St Unit 2",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "Test Country",
            "size": 75.0,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "parking_spots": 1,
            "user_id": "test_user",
            "is_active": True
        })
    ]
    
    # Mock the database queries
    mock_db.execute.return_value.scalars.return_value.all.return_value = properties
    
    # Create update data
    update_data = PropertyUpdate(status=PropertyStatus.MAINTENANCE)
    
    # Perform bulk update
    updated = await service.bulk_update_properties([1, 2, 3], update_data, "test_user")
    
    # Verify the updates
    assert len(updated) == 3
    assert all(p.status == PropertyStatus.MAINTENANCE for p in updated)
    mock_db.commit.assert_called_once()
