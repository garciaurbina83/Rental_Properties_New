import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import PropertyStatus

pytestmark = pytest.mark.integration

async def test_create_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    response = await client.post("/api/v1/properties/", json=test_property_data)
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == test_property_data["address"]
    assert data["status"] == PropertyStatus.AVAILABLE.value

async def test_get_properties(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    # First create a property
    await client.post("/api/v1/properties/", json=test_property_data)
    
    # Then get all properties
    response = await client.get("/api/v1/properties/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(p["address"] == test_property_data["address"] for p in data)

async def test_update_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    # First create a property
    create_response = await client.post("/api/v1/properties/", json=test_property_data)
    property_id = create_response.json()["id"]
    
    # Update the property
    update_data = {"monthly_rent": 1200}
    response = await client.put(f"/api/v1/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_rent"] == update_data["monthly_rent"]

async def test_delete_property(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    # First create a property
    create_response = await client.post("/api/v1/properties/", json=test_property_data)
    property_id = create_response.json()["id"]
    
    # Delete the property
    response = await client.delete(f"/api/v1/properties/{property_id}")
    assert response.status_code == 204
    
    # Verify property is deleted
    get_response = await client.get(f"/api/v1/properties/{property_id}")
    assert get_response.status_code == 404

async def test_create_property_validation(
    client: AsyncClient,
    db_session: AsyncSession
) -> None:
    """Test property creation with invalid data"""
    invalid_data = {
        "address": "",  # Empty address
        "type": "InvalidType",  # Invalid property type
        "rentAmount": -1000,  # Negative rent
        "status": "InvalidStatus"  # Invalid status
    }
    response = await client.post("/api/v1/properties/", json=invalid_data)
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
    create_response = await client.post("/api/v1/properties/", json=test_property_data)
    property_id = create_response.json()["id"]
    
    # Get the property
    response = await client.get(f"/api/v1/properties/{property_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == property_id
    assert data["address"] == test_property_data["address"]

async def test_filter_properties(
    client: AsyncClient,
    db_session: AsyncSession,
    test_property_data: dict
) -> None:
    """Test filtering properties by query parameters"""
    # Create multiple properties
    property1 = test_property_data.copy()
    property1["status"] = "available"
    await client.post("/api/v1/properties/", json=property1)
    
    property2 = test_property_data.copy()
    property2["status"] = "rented"
    await client.post("/api/v1/properties/", json=property2)
    
    # Test filtering by status
    response = await client.get("/api/v1/properties/?status=available")
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
    create_response = await client.post("/api/v1/properties/", json=test_property_data)
    property_id = create_response.json()["id"]
    
    # Test updating single field
    update_data = {"status": "rented"}
    response = await client.put(f"/api/v1/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == update_data["status"]

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
        response = await client.post("/api/v1/properties/", json=prop)
        properties.append(response.json())
    
    # Test bulk update
    property_ids = [p["id"] for p in properties]
    bulk_update = {
        "ids": property_ids,
        "update": {"status": PropertyStatus.MAINTENANCE.value}  # Using enum value
    }
    response = await client.put("/api/v1/properties/bulk", json=bulk_update)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(property_ids)
    assert all(p["status"] == PropertyStatus.MAINTENANCE.value for p in data)
