"""
Test cases for the property API endpoints
"""
import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_create_property(client: AsyncClient, test_property_data: Dict):
    """Test creating a new property"""
    response = await client.post("/api/properties", json=test_property_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_property_data["name"]
    assert data["address"] == test_property_data["address"]
    assert data["user_id"] == test_property_data["user_id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_get_properties(client: AsyncClient, test_property_data: Dict):
    """Test getting a list of properties"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201

    # Then get the list of properties
    response = await client.get("/api/properties")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_property_data["name"]

@pytest.mark.asyncio
async def test_get_property(client: AsyncClient, test_property_data: Dict):
    """Test getting a specific property"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201
    property_id = create_response.json()["id"]

    # Then get the specific property
    response = await client.get(f"/api/properties/{property_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == property_id
    assert data["name"] == test_property_data["name"]

@pytest.mark.asyncio
async def test_update_property(client: AsyncClient, test_property_data: Dict):
    """Test updating a property"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201
    property_id = create_response.json()["id"]

    # Update the property
    update_data = {
        "name": "Updated Test Property",
        "monthly_rent": 1200.0
    }
    response = await client.patch(f"/api/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["monthly_rent"] == update_data["monthly_rent"]
    assert data["address"] == test_property_data["address"]  # Unchanged field

@pytest.mark.asyncio
async def test_delete_property(client: AsyncClient, test_property_data: Dict):
    """Test deleting a property"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201
    property_id = create_response.json()["id"]

    # Delete the property
    response = await client.delete(f"/api/properties/{property_id}")
    assert response.status_code == 204

    # Verify the property is deleted (soft delete)
    get_response = await client.get(f"/api/properties/{property_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_search_properties(client: AsyncClient, test_property_data: Dict):
    """Test searching properties"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201

    # Search for the property
    response = await client.get("/api/properties/search", params={"q": test_property_data["name"]})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_property_data["name"]

@pytest.mark.asyncio
async def test_property_metrics(client: AsyncClient, test_property_data: Dict):
    """Test getting property metrics"""
    # First create a property
    create_response = await client.post("/api/properties", json=test_property_data)
    assert create_response.status_code == 201

    # Get metrics
    response = await client.get("/api/properties/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_properties" in data
    assert "total_value" in data
    assert "total_rent" in data
    assert data["total_properties"] > 0
