import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
from app.models import (
    Loan, LoanDocument, LoanPayment,
    LoanStatus, PaymentStatus
)
from app.services.loan_service import LoanService
from app.core.exceptions import NotFoundException, ValidationError
from ..fixtures.loan_fixtures import (
    loan_fixture, loan_document_fixture,
    loan_with_payments_fixture, amortization_schedule_fixture,
    loan_summary_fixture
)

@pytest.mark.asyncio
async def test_create_loan(db_session):
    # Arrange
    loan_data = loan_fixture()
    user_id = 1

    # Act
    loan = await LoanService.create_loan(db_session, Mock(**loan_data), user_id)

    # Assert
    assert loan.property_id == loan_data["property_id"]
    assert loan.loan_type == loan_data["loan_type"]
    assert loan.principal_amount == loan_data["principal_amount"]
    assert loan.interest_rate == loan_data["interest_rate"]
    assert loan.term_months == loan_data["term_months"]
    assert loan.payment_day == loan_data["payment_day"]
    assert loan.status == LoanStatus.PENDING
    assert loan.remaining_balance == loan_data["principal_amount"]
    assert loan.monthly_payment > 0

@pytest.mark.asyncio
async def test_get_loan(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Act
    result = await LoanService.get_loan(db_session, loan.id)

    # Assert
    assert result is not None
    assert result.id == loan.id
    assert result.property_id == loan_data["property_id"]
    assert result.loan_type == loan_data["loan_type"]

@pytest.mark.asyncio
async def test_get_loan_not_found(db_session):
    # Act
    result = await LoanService.get_loan(db_session, 999)

    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_update_loan(db_session):
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
    updated_loan = await LoanService.update_loan(
        db_session, loan.id, Mock(**update_data), user_id=1
    )

    # Assert
    assert updated_loan.interest_rate == update_data["interest_rate"]
    assert updated_loan.payment_day == update_data["payment_day"]
    assert updated_loan.notes == update_data["notes"]
    assert updated_loan.monthly_payment > loan.monthly_payment  # Debido al aumento de tasa

@pytest.mark.asyncio
async def test_update_loan_not_found(db_session):
    # Arrange
    update_data = {"interest_rate": 6.0}

    # Act & Assert
    with pytest.raises(NotFoundException):
        await LoanService.update_loan(
            db_session, 999, Mock(**update_data), user_id=1
        )

@pytest.mark.asyncio
async def test_add_document(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    document_data = loan_document_fixture()

    # Act
    document = await LoanService.add_document(
        db_session, loan.id, Mock(**document_data), user_id=1
    )

    # Assert
    assert document.loan_id == loan.id
    assert document.document_type == document_data["document_type"]
    assert document.file_path == document_data["file_path"]
    assert not document.is_verified

@pytest.mark.asyncio
async def test_verify_document(db_session):
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
    verified_doc = await LoanService.verify_document(
        db_session, document.id, user_id=1
    )

    # Assert
    assert verified_doc.is_verified
    assert verified_doc.verified_by == 1
    assert verified_doc.verified_at is not None

@pytest.mark.asyncio
async def test_get_loan_summary(db_session):
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
    summary = await LoanService.get_loan_summary(db_session, loan.id)

    # Assert
    assert summary.loan_id == loan.id
    assert summary.total_amount == loan_data["principal_amount"]
    assert summary.total_paid == loan.monthly_payment * 2
    assert summary.payments_made == 2
    assert summary.remaining_payments == loan.term_months - 2

@pytest.mark.asyncio
async def test_generate_amortization_schedule(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Act
    schedule = await LoanService.generate_amortization_schedule(db_session, loan.id)

    # Assert
    assert len(schedule) == loan.term_months
    assert schedule[0]["payment_number"] == 1
    assert schedule[0]["payment_amount"] == loan.monthly_payment
    assert schedule[-1]["remaining_balance"] == pytest.approx(0, abs=0.01)

    # Verificar que los pagos suman el total del préstamo más intereses
    total_payments = sum(payment["payment_amount"] for payment in schedule)
    total_principal = sum(payment["principal_payment"] for payment in schedule)
    total_interest = sum(payment["interest_payment"] for payment in schedule)

    assert total_principal == pytest.approx(loan.principal_amount, abs=0.01)
    assert total_payments == total_principal + total_interest
