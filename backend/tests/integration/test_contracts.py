import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.contract import ContractStatus, PaymentFrequency
from app.models.tenant import Tenant
from app.models.unit import Unit
from app.schemas.contract import ContractCreate, PaymentCreate, ContractDocumentCreate

@pytest.fixture
def valid_contract_data(db: Session):
    # Crear inquilino y unidad de prueba
    tenant = Tenant(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        identification_type="DNI",
        identification_number="12345678",
        emergency_contact_name="Jane",
        emergency_contact_phone="0987654321"
    )
    db.add(tenant)
    
    unit = Unit(
        property_id=1,  # Asumiendo que existe una propiedad con ID 1
        unit_number="A101",
        floor=1,
        size=100.0,
        bedrooms=2,
        bathrooms=1
    )
    db.add(unit)
    db.commit()

    return {
        "contract_number": "CTR-2023-001",
        "tenant_id": tenant.id,
        "unit_id": unit.id,
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=365)),
        "rent_amount": 1000.0,
        "security_deposit": 2000.0,
        "payment_frequency": PaymentFrequency.MONTHLY,
        "payment_due_day": 5,
        "terms_and_conditions": "Standard terms and conditions",
        "is_renewable": True,
        "renewal_price_increase": 5.0
    }

@pytest.fixture
def valid_payment_data():
    return {
        "amount": 1000.0,
        "payment_date": str(date.today()),
        "due_date": str(date.today()),
        "payment_method": "bank_transfer",
        "transaction_id": "TRX-001"
    }

@pytest.fixture
def valid_document_data():
    return {
        "document_type": "contract",
        "file_path": "/documents/contract.pdf",
        "upload_date": str(date.today()),
        "is_signed": True,
        "signed_date": str(date.today())
    }

def test_create_contract(client: TestClient, db: Session, valid_contract_data):
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    assert response.status_code == 201
    data = response.json()
    assert data["contract_number"] == valid_contract_data["contract_number"]
    assert "id" in data

def test_get_contract(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Obtener contrato
    response = client.get(f"/api/v1/contracts/{contract_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["contract_number"] == valid_contract_data["contract_number"]

def test_list_contracts(client: TestClient, db: Session, valid_contract_data):
    # Crear varios contratos
    client.post("/api/v1/contracts/", json=valid_contract_data)
    valid_contract_data["contract_number"] = "CTR-2023-002"
    client.post("/api/v1/contracts/", json=valid_contract_data)

    response = client.get("/api/v1/contracts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_update_contract(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Actualizar contrato
    update_data = {"rent_amount": 1200.0, "renewal_price_increase": 7.0}
    response = client.put(f"/api/v1/contracts/{contract_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rent_amount"] == 1200.0
    assert data["renewal_price_increase"] == 7.0

def test_terminate_contract(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Terminar contrato
    termination_data = {
        "termination_date": str(date.today()),
        "termination_notes": "Early termination due to relocation"
    }
    response = client.post(f"/api/v1/contracts/{contract_id}/terminate", json=termination_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ContractStatus.TERMINATED

def test_renew_contract(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Renovar contrato
    renewal_data = {
        "new_end_date": str(date.today() + timedelta(days=730)),
        "new_rent_amount": 1100.0
    }
    response = client.post(f"/api/v1/contracts/{contract_id}/renew", json=renewal_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ContractStatus.RENEWED
    assert data["rent_amount"] == 1100.0

def test_add_payment(client: TestClient, db: Session, valid_contract_data, valid_payment_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Agregar pago
    response = client.post(f"/api/v1/contracts/{contract_id}/payments", json=valid_payment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == valid_payment_data["amount"]
    assert data["contract_id"] == contract_id

def test_list_contract_payments(client: TestClient, db: Session, valid_contract_data, valid_payment_data):
    # Crear contrato y pagos
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]
    
    client.post(f"/api/v1/contracts/{contract_id}/payments", json=valid_payment_data)
    valid_payment_data["transaction_id"] = "TRX-002"
    client.post(f"/api/v1/contracts/{contract_id}/payments", json=valid_payment_data)

    response = client.get(f"/api/v1/contracts/{contract_id}/payments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_add_contract_document(client: TestClient, db: Session, valid_contract_data, valid_document_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    contract_id = response.json()["id"]

    # Agregar documento
    response = client.post(f"/api/v1/contracts/{contract_id}/documents", json=valid_document_data)
    assert response.status_code == 200
    data = response.json()
    assert data["document_type"] == valid_document_data["document_type"]
    assert data["contract_id"] == contract_id

def test_get_tenant_contracts(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    tenant_id = valid_contract_data["tenant_id"]

    response = client.get(f"/api/v1/contracts/tenant/{tenant_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["tenant_id"] == tenant_id

def test_get_unit_contracts(client: TestClient, db: Session, valid_contract_data):
    # Crear contrato
    response = client.post("/api/v1/contracts/", json=valid_contract_data)
    unit_id = valid_contract_data["unit_id"]

    response = client.get(f"/api/v1/contracts/unit/{unit_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["unit_id"] == unit_id
