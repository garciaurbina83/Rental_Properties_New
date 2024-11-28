import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

def test_create_property(
    auth_client: TestClient,
    db: Session,
    test_data: dict
) -> None:
    response = auth_client.post("/api/v1/properties/", json=test_data["property"])
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == test_data["property"]["address"]
    assert data["type"] == test_data["property"]["type"]

def test_get_properties(
    auth_client: TestClient,
    db: Session,
    test_data: dict
) -> None:
    # First create a property
    auth_client.post("/api/v1/properties/", json=test_data["property"])
    
    # Then get all properties
    response = auth_client.get("/api/v1/properties/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(p["address"] == test_data["property"]["address"] for p in data)

def test_update_property(
    auth_client: TestClient,
    db: Session,
    test_data: dict
) -> None:
    # First create a property
    create_response = auth_client.post("/api/v1/properties/", json=test_data["property"])
    property_id = create_response.json()["id"]
    
    # Update the property
    update_data = {"rentAmount": 1200}
    response = auth_client.patch(f"/api/v1/properties/{property_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rentAmount"] == update_data["rentAmount"]

def test_delete_property(
    auth_client: TestClient,
    db: Session,
    test_data: dict
) -> None:
    # First create a property
    create_response = auth_client.post("/api/v1/properties/", json=test_data["property"])
    property_id = create_response.json()["id"]
    
    # Delete the property
    response = auth_client.delete(f"/api/v1/properties/{property_id}")
    assert response.status_code == 204
    
    # Verify property is deleted
    get_response = auth_client.get(f"/api/v1/properties/{property_id}")
    assert get_response.status_code == 404
