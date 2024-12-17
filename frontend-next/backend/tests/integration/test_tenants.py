import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.models.tenant import Tenant, ContactMethod
from app.schemas.tenant import TenantCreate, TenantReferenceCreate, TenantDocumentCreate

@pytest.fixture
def valid_tenant_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "occupation": "Software Engineer",
        "monthly_income": 5000.0,
        "previous_address": "123 Previous St",
        "identification_type": "DNI",
        "identification_number": "12345678",
        "preferred_contact_method": ContactMethod.EMAIL,
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "0987654321"
    }

@pytest.fixture
def valid_reference_data():
    return {
        "name": "Jane Smith",
        "relationship": "Former Landlord",
        "phone": "1234567890",
        "email": "jane.smith@example.com",
        "notes": "Excellent tenant"
    }

@pytest.fixture
def valid_document_data():
    return {
        "document_type": "ID",
        "file_path": "/documents/id.pdf",
        "upload_date": str(date.today()),
        "expiry_date": str(date.today().replace(year=date.today().year + 5)),
        "is_verified": False
    }

def test_create_tenant(client: TestClient, db: Session, valid_tenant_data):
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == valid_tenant_data["email"]
    assert data["first_name"] == valid_tenant_data["first_name"]
    assert "id" in data

def test_create_tenant_duplicate_email(client: TestClient, db: Session, valid_tenant_data):
    # Crear el primer inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    assert response.status_code == 201

    # Intentar crear otro inquilino con el mismo email
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_get_tenant(client: TestClient, db: Session, valid_tenant_data):
    # Crear inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    tenant_id = response.json()["id"]

    # Obtener inquilino
    response = client.get(f"/api/v1/tenants/{tenant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == valid_tenant_data["email"]

def test_get_nonexistent_tenant(client: TestClient, db: Session):
    response = client.get("/api/v1/tenants/999999")
    assert response.status_code == 404
    assert "Tenant not found" in response.json()["detail"]

def test_list_tenants(client: TestClient, db: Session, valid_tenant_data):
    # Crear varios inquilinos
    client.post("/api/v1/tenants/", json=valid_tenant_data)
    valid_tenant_data["email"] = "another@example.com"
    client.post("/api/v1/tenants/", json=valid_tenant_data)

    response = client.get("/api/v1/tenants/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_update_tenant(client: TestClient, db: Session, valid_tenant_data):
    # Crear inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    tenant_id = response.json()["id"]

    # Actualizar inquilino
    update_data = {"first_name": "Jane", "monthly_income": 6000.0}
    response = client.put(f"/api/v1/tenants/{tenant_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["monthly_income"] == 6000.0

def test_delete_tenant(client: TestClient, db: Session, valid_tenant_data):
    # Crear inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    tenant_id = response.json()["id"]

    # Eliminar inquilino
    response = client.delete(f"/api/v1/tenants/{tenant_id}")
    assert response.status_code == 200

    # Verificar que fue eliminado
    response = client.get(f"/api/v1/tenants/{tenant_id}")
    assert response.status_code == 404

def test_add_tenant_reference(client: TestClient, db: Session, valid_tenant_data, valid_reference_data):
    # Crear inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    tenant_id = response.json()["id"]

    # Agregar referencia
    response = client.post(f"/api/v1/tenants/{tenant_id}/references", json=valid_reference_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == valid_reference_data["name"]
    assert data["tenant_id"] == tenant_id

def test_add_tenant_document(client: TestClient, db: Session, valid_tenant_data, valid_document_data):
    # Crear inquilino
    response = client.post("/api/v1/tenants/", json=valid_tenant_data)
    tenant_id = response.json()["id"]

    # Agregar documento
    response = client.post(f"/api/v1/tenants/{tenant_id}/documents", json=valid_document_data)
    assert response.status_code == 200
    data = response.json()
    assert data["document_type"] == valid_document_data["document_type"]
    assert data["tenant_id"] == tenant_id

def test_search_tenants(client: TestClient, db: Session, valid_tenant_data):
    # Crear inquilino
    client.post("/api/v1/tenants/", json=valid_tenant_data)

    # Buscar por nombre
    response = client.get("/api/v1/tenants/search/?q=John")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["first_name"] == "John"

    # Buscar por email
    response = client.get("/api/v1/tenants/search/?q=john.doe")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["email"] == "john.doe@example.com"
