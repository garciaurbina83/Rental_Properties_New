"""
Test cases for the property API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from app.models.property import PropertyStatus
from app.core.auth import get_current_user
from app.main import app

pytestmark = pytest.mark.integration

# Override the get_current_user dependency for testing
async def mock_current_user():
    return {"id": "test-user-id"}

# Apply the mock to the app
app.dependency_overrides[get_current_user] = mock_current_user

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
    test_property_data: dict
) -> None:
    # First create a property
    await client.post("/api/v1/properties", json=test_property_data)

    # Then get all properties
    response = await client.get("/api/v1/properties")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_property_data["name"]

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
