"""
Test cases for the property API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict
from app.models.property import PropertyStatus, PropertyType
from app.core.auth import get_current_user
from app.main import app

pytestmark = pytest.mark.integration

# Override the get_current_user dependency for testing
async def mock_current_user():
    return {"id": "test-user-id"}

# Apply the mock to the app
app.dependency_overrides[get_current_user] = mock_current_user

@pytest.fixture
async def principal_property_data() -> Dict:
    return {
        "name": "Principal Property",
        "address": "123 Main St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.PRINCIPAL,
        "status": PropertyStatus.AVAILABLE,
        "size": 150.5,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "parking_spots": 2,
        "monthly_rent": 2500.00,
        "user_id": "test-user-id"
    }

@pytest.fixture
async def unit_property_data() -> Dict:
    return {
        "name": "Unit 1",
        "address": "123 Main St Unit 1",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.UNIT,
        "status": PropertyStatus.AVAILABLE,
        "size": 75.0,
        "bedrooms": 2,
        "bathrooms": 1.5,
        "parking_spots": 1,
        "monthly_rent": 1500.00,
        "user_id": "test-user-id"
    }

@pytest.fixture(autouse=True)
async def cleanup_db(db_session: AsyncSession) -> None:
    """Clean up the database after each test"""
    yield
    await db_session.execute(text("DELETE FROM properties"))
    await db_session.commit()

async def test_create_principal_property(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict
) -> None:
    """Test creating a principal property"""
    response = await client.post("/api/v1/properties", json=principal_property_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == principal_property_data["name"]
    assert data["property_type"] == PropertyType.PRINCIPAL
    assert data["parent_property_id"] is None

async def test_create_unit(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict,
    unit_property_data: Dict
) -> None:
    """Test creating a unit under a principal property"""
    # First create a principal property
    principal_response = await client.post("/api/v1/properties", json=principal_property_data)
    assert principal_response.status_code == 201
    principal_id = principal_response.json()["id"]

    # Create a unit
    response = await client.post(
        f"/api/v1/properties/{principal_id}/units",
        json=unit_property_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == unit_property_data["name"]
    assert data["property_type"] == PropertyType.UNIT
    assert data["parent_property_id"] == principal_id

async def test_get_property_with_units(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict,
    unit_property_data: Dict
) -> None:
    """Test getting a principal property with its units"""
    # Create principal property
    principal_response = await client.post("/api/v1/properties", json=principal_property_data)
    assert principal_response.status_code == 201
    principal_id = principal_response.json()["id"]

    # Create multiple units
    for i in range(3):
        unit_data = unit_property_data.copy()
        unit_data["name"] = f"Unit {i+1}"
        response = await client.post(
            f"/api/v1/properties/{principal_id}/units",
            json=unit_data
        )
        assert response.status_code == 201

    # Get property with units
    response = await client.get(f"/api/v1/properties/{principal_id}/with-units")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == principal_id
    assert data["property_type"] == PropertyType.PRINCIPAL
    assert len(data["units"]) == 3

async def test_get_units_by_principal(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict,
    unit_property_data: Dict
) -> None:
    """Test getting all units for a principal property"""
    # Create principal property
    principal_response = await client.post("/api/v1/properties", json=principal_property_data)
    assert principal_response.status_code == 201
    principal_id = principal_response.json()["id"]

    # Create multiple units
    created_units = []
    for i in range(3):
        unit_data = unit_property_data.copy()
        unit_data["name"] = f"Unit {i+1}"
        response = await client.post(
            f"/api/v1/properties/{principal_id}/units",
            json=unit_data
        )
        assert response.status_code == 201
        created_units.append(response.json())

    # Get all units
    response = await client.get(f"/api/v1/properties/{principal_id}/units")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(unit["parent_property_id"] == principal_id for unit in data)

async def test_bulk_update_with_units(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict,
    unit_property_data: Dict
) -> None:
    """Test bulk update of properties including units"""
    # Create principal property with units
    principal_response = await client.post("/api/v1/properties", json=principal_property_data)
    principal_id = principal_response.json()["id"]
    
    unit_ids = []
    for i in range(3):
        unit_data = unit_property_data.copy()
        unit_data["name"] = f"Unit {i+1}"
        response = await client.post(
            f"/api/v1/properties/{principal_id}/units",
            json=unit_data
        )
        unit_ids.append(response.json()["id"])

    # Bulk update all properties (principal and units)
    all_ids = [principal_id] + unit_ids
    bulk_update = {
        "ids": all_ids,
        "update": {
            "status": PropertyStatus.MAINTENANCE
        }
    }
    response = await client.put("/api/v1/properties/bulk", json=bulk_update)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(all_ids)
    assert all(p["status"] == PropertyStatus.MAINTENANCE for p in data)

async def test_unit_validation_errors(
    client: AsyncClient,
    db_session: AsyncSession,
    unit_property_data: Dict
) -> None:
    """Test validation errors when creating units"""
    # Try to create a unit without a principal property
    response = await client.post("/api/v1/properties", json=unit_property_data)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error

    # Try to create a unit with non-existent principal
    response = await client.post(
        "/api/v1/properties/99999/units",
        json=unit_property_data
    )
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error

async def test_create_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    response = await client.post("/api/v1/properties", json=test_property_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_property_data["name"]
    assert data["address"] == test_property_data["address"]
    assert data["user_id"] == test_property_data["user_id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

async def test_get_properties(
    client: AsyncClient,
    db_session: AsyncSession,
    principal_property_data: Dict
) -> None:
    # First create a property
    await client.post("/api/v1/properties", json=principal_property_data)

    # Then get all properties for this user
    response = await client.get(f"/api/v1/properties?user_id={principal_property_data['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == principal_property_data["name"]

async def test_update_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    # First create a property
    create_response = await client.post("/api/v1/properties", json=test_property_data)
    property_id = create_response.json()["id"]

    # Update the property
    update_data = {
        "name": "Updated Test Property",
        "monthly_rent": 1200.0
    }
    response = await client.put(f"/api/v1/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["monthly_rent"] == update_data["monthly_rent"]
    assert data["address"] == test_property_data["address"]  # Unchanged field

async def test_delete_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    # First create a property
    create_response = await client.post("/api/v1/properties", json=test_property_data)
    property_id = create_response.json()["id"]

    # Delete the property
    response = await client.delete(f"/api/v1/properties/{property_id}")
    assert response.status_code == 204

    # Verify the property is deleted (soft delete)
    get_response = await client.get(f"/api/v1/properties/{property_id}")
    assert get_response.status_code == 404

async def test_create_property_validation(
    client: AsyncClient,
    db_session: AsyncSession
) -> None:
    """Test validation errors when creating a property"""
    # Missing required fields
    invalid_data = {
        "name": "Test Property"  # Missing other required fields
    }
    response = await client.post("/api/v1/properties", json=invalid_data)
    print("Response:", response.json())  # Add this line to see the validation errors
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

async def test_get_property_by_id(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    """Test getting a specific property by ID"""
    # Create a property first
    create_response = await client.post("/api/v1/properties", json=test_property_data)
    property_id = create_response.json()["id"]

    # Get the property by ID
    response = await client.get(f"/api/v1/properties/{property_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == property_id
    assert data["name"] == test_property_data["name"]

async def test_filter_properties(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    """Test filtering properties by query parameters"""
    # Create multiple properties
    property1 = test_property_data.copy()
    property1["status"] = "available"
    await client.post("/api/v1/properties", json=property1)

    property2 = test_property_data.copy()
    property2["status"] = "rented"
    await client.post("/api/v1/properties", json=property2)

    # Test filtering by status
    response = await client.get("/api/v1/properties?status=available")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(p["status"] == "available" for p in data)

async def test_partial_update_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    """Test partial update of property fields"""
    # Create a property
    create_response = await client.post("/api/v1/properties", json=test_property_data)
    property_id = create_response.json()["id"]

    # Update only some fields
    update_data = {
        "name": "Updated Name Only"
    }
    response = await client.put(f"/api/v1/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["address"] == test_property_data["address"]  # Should remain unchanged

async def test_bulk_operations(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    """Test bulk operations on properties"""
    # Create multiple properties
    properties = []
    for i in range(3):
        prop = test_property_data.copy()
        prop["address"] = f"Address {i}"
        response = await client.post("/api/v1/properties", json=prop)
        assert response.status_code == 201  # Ensure creation succeeds
        properties.append(response.json())

    # Test bulk update with a valid status value
    property_ids = [p["id"] for p in properties]
    bulk_update = {
        "ids": property_ids,
        "update": {
            "status": "maintenance"  # Use lowercase to match enum
        }
    }
    response = await client.put("/api/v1/properties/bulk", json=bulk_update)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(property_ids)
    # Verify all properties were updated with the new status
    assert all(p["status"] == "maintenance" for p in data)
