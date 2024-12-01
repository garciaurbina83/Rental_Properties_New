import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from app.models import (
    Loan, LoanDocument, LoanPayment,
    LoanStatus, PaymentStatus
)
from tests.fixtures.loan_fixtures import (
    loan_fixture, loan_document_fixture,
    loan_payment_fixture, loan_with_payments_fixture,
    amortization_schedule_fixture, loan_summary_fixture
)

@pytest.mark.asyncio
async def test_create_loan(async_client: AsyncClient, normal_user_token_headers):
    # Arrange
    loan_data = loan_fixture()

    # Act
    response = await async_client.post(
        "/api/v1/loans/",
        json=loan_data,
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["property_id"] == loan_data["property_id"]
    assert data["loan_type"] == loan_data["loan_type"]
    assert data["principal_amount"] == loan_data["principal_amount"]
    assert data["status"] == LoanStatus.PENDING.value

@pytest.mark.asyncio
async def test_get_loan(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Act
    response = await async_client.get(
        f"/api/v1/loans/{loan.id}",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == loan.id
    assert data["property_id"] == loan_data["property_id"]
    assert data["loan_type"] == loan_data["loan_type"]

@pytest.mark.asyncio
async def test_update_loan(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    update_data = {
        "interest_rate": 6.0,
        "payment_day": 10,
        "notes": "Actualización de prueba"
    }

    # Act
    response = await async_client.put(
        f"/api/v1/loans/{loan.id}",
        json=update_data,
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["interest_rate"] == update_data["interest_rate"]
    assert data["payment_day"] == update_data["payment_day"]
    assert data["notes"] == update_data["notes"]

@pytest.mark.asyncio
async def test_add_document(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    document_data = loan_document_fixture()

    # Act
    response = await async_client.post(
        f"/api/v1/loans/{loan.id}/documents",
        json=document_data,
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["loan_id"] == loan.id
    assert data["document_type"] == document_data["document_type"]
    assert not data["is_verified"]

@pytest.mark.asyncio
async def test_verify_document(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    document_data = loan_document_fixture()
    document = LoanDocument(loan_id=loan.id, **document_data)
    db_session.add(document)
    await db_session.flush()

    # Act
    response = await async_client.post(
        f"/api/v1/loans/{loan.id}/documents/{document.id}/verify",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["is_verified"]
    assert data["verified_by"] is not None
    assert data["verified_at"] is not None

@pytest.mark.asyncio
async def test_get_loan_summary(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Crear algunos pagos completados
    payment1 = LoanPayment(
        loan_id=loan.id,
        payment_date=date.today(),
        due_date=date.today(),
        amount=loan.monthly_payment,
        principal_amount=500,
        interest_amount=187.89,
        status=PaymentStatus.COMPLETED
    )
    payment2 = LoanPayment(
        loan_id=loan.id,
        payment_date=date.today() + timedelta(days=30),
        due_date=date.today() + timedelta(days=30),
        amount=loan.monthly_payment,
        principal_amount=502,
        interest_amount=185.89,
        status=PaymentStatus.COMPLETED
    )
    db_session.add_all([payment1, payment2])
    await db_session.flush()

    # Act
    response = await async_client.get(
        f"/api/v1/loans/{loan.id}/summary",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == loan.id
    assert data["total_amount"] == loan_data["principal_amount"]
    assert data["payments_made"] == 2
    assert data["remaining_payments"] == loan.term_months - 2

@pytest.mark.asyncio
async def test_get_amortization_schedule(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Act
    response = await async_client.get(
        f"/api/v1/loans/{loan.id}/amortization",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == loan.term_months
    assert data[0]["payment_number"] == 1
    assert data[-1]["remaining_balance"] == pytest.approx(0, abs=0.01)

@pytest.mark.asyncio
async def test_create_payment(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()

    # Act
    response = await async_client.post(
        f"/api/v1/loans/{loan.id}/payments",
        json=payment_data,
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["loan_id"] == loan.id
    assert data["amount"] == payment_data["amount"]
    assert data["status"] == PaymentStatus.PENDING.value

@pytest.mark.asyncio
async def test_process_payment(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()
    payment = LoanPayment(loan_id=loan.id, **payment_data)
    db_session.add(payment)
    await db_session.flush()

    # Act
    response = await async_client.post(
        f"/api/v1/loans/{loan.id}/payments/{payment.id}/process",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == PaymentStatus.COMPLETED.value
    assert data["processed_by"] is not None
    assert data["processed_at"] is not None

@pytest.mark.asyncio
async def test_cancel_payment(
    async_client: AsyncClient,
    db_session,
    normal_user_token_headers
):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()
    payment = LoanPayment(loan_id=loan.id, **payment_data)
    db_session.add(payment)
    await db_session.flush()

    # Act
    response = await async_client.post(
        f"/api/v1/loans/{loan.id}/payments/{payment.id}/cancel",
        headers=normal_user_token_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == PaymentStatus.CANCELLED.value
    assert data["cancelled_by"] is not None
    assert data["cancelled_at"] is not None
