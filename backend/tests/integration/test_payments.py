import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.payment import create_random_payment
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string
from app.crud import crud_payment
from app.models.payment import PaymentStatus, PaymentConcept

def test_create_payment(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    data = {
        "amount": 1000.0,
        "payment_date": str(date.today()),
        "concept": PaymentConcept.RENT.value,
        "status": PaymentStatus.PENDING.value,
        "contract_id": 1,
        "tenant_id": 1
    }
    response = client.post(
        f"{settings.API_V1_STR}/payments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["amount"] == data["amount"]
    assert content["status"] == PaymentStatus.PENDING.value
    assert "id" in content

def test_read_payment(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    payment = create_random_payment(db)
    response = client.get(
        f"{settings.API_V1_STR}/payments/{payment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == payment.id
    assert content["amount"] == payment.amount
    assert content["status"] == payment.status

def test_read_payments(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    payment = create_random_payment(db)
    response = client.get(
        f"{settings.API_V1_STR}/payments/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) > 0
    assert isinstance(content, list)
    assert any(p["id"] == payment.id for p in content)

def test_update_payment(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    payment = create_random_payment(db)
    data = {
        "amount": 2000.0,
        "status": PaymentStatus.PAID.value
    }
    response = client.put(
        f"{settings.API_V1_STR}/payments/{payment.id}",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == payment.id
    assert content["amount"] == data["amount"]
    assert content["status"] == data["status"]

def test_delete_payment(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    payment = create_random_payment(db)
    response = client.delete(
        f"{settings.API_V1_STR}/payments/{payment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == payment.id
    
    # Verificar que el pago fue eliminado
    payment_in_db = crud_payment.get(db, id=payment.id)
    assert payment_in_db is None

def test_payment_validation(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    # Intentar crear pago con monto negativo
    data = {
        "amount": -1000.0,
        "payment_date": str(date.today()),
        "concept": PaymentConcept.RENT.value,
        "status": PaymentStatus.PENDING.value,
        "contract_id": 1,
        "tenant_id": 1
    }
    response = client.post(
        f"{settings.API_V1_STR}/payments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422

def test_payment_filters(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    # Crear pagos con diferentes estados
    payment1 = create_random_payment(db, status=PaymentStatus.PAID)
    payment2 = create_random_payment(db, status=PaymentStatus.PENDING)
    
    # Filtrar por estado PAID
    response = client.get(
        f"{settings.API_V1_STR}/payments/?status={PaymentStatus.PAID.value}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert all(p["status"] == PaymentStatus.PAID.value for p in content)
    
    # Filtrar por estado PENDING
    response = client.get(
        f"{settings.API_V1_STR}/payments/?status={PaymentStatus.PENDING.value}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert all(p["status"] == PaymentStatus.PENDING.value for p in content)

def test_payment_date_range(
    client: TestClient,
    superuser_token_headers: dict,
    db: Session
) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Crear pagos con diferentes fechas
    payment1 = create_random_payment(db, payment_date=yesterday)
    payment2 = create_random_payment(db, payment_date=today)
    payment3 = create_random_payment(db, payment_date=tomorrow)
    
    # Filtrar por rango de fechas
    response = client.get(
        f"{settings.API_V1_STR}/payments/?start_date={yesterday}&end_date={today}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    payment_dates = [datetime.strptime(p["payment_date"], "%Y-%m-%d").date() 
                    for p in content]
    assert all(yesterday <= d <= today for d in payment_dates)

def test_payment_permissions(
    client: TestClient,
    normal_user_token_headers: dict,
    db: Session
) -> None:
    # Intentar acceder a endpoints restringidos con usuario normal
    response = client.get(
        f"{settings.API_V1_STR}/payments/sensitive",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
