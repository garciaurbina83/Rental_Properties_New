import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
from app.models import (
    Loan, LoanPayment,
    LoanStatus, PaymentStatus, PaymentMethod
)
from app.services.loan_payment_service import LoanPaymentService
from app.core.exceptions import (
    NotFoundException, ValidationError,
    PaymentProcessError
)
from ..fixtures.loan_fixtures import (
    loan_with_payments_fixture,
    loan_payment_fixture,
    processed_payment_fixture
)

@pytest.mark.asyncio
async def test_create_payment(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()

    # Act
    payment = await LoanPaymentService.create_payment(
        db_session, loan.id, Mock(**payment_data), user_id=1
    )

    # Assert
    assert payment.loan_id == loan.id
    assert payment.amount == payment_data["amount"]
    assert payment.payment_method == payment_data["payment_method"]
    assert payment.status == PaymentStatus.PENDING

@pytest.mark.asyncio
async def test_create_payment_invalid_amount(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()
    payment_data["amount"] = 0  # Monto inválido

    # Act & Assert
    with pytest.raises(ValidationError):
        await LoanPaymentService.create_payment(
            db_session, loan.id, Mock(**payment_data), user_id=1
        )

@pytest.mark.asyncio
async def test_process_payment(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = loan_payment_fixture()
    payment = LoanPayment(loan_id=loan.id, **payment_data)
    db_session.add(payment)
    await db_session.flush()

    initial_balance = loan.remaining_balance

    # Act
    processed = await LoanPaymentService.process_payment(
        db_session, payment.id, user_id=1
    )

    # Assert
    assert processed.status == PaymentStatus.COMPLETED
    assert processed.processed_by == 1
    assert processed.processed_at is not None
    assert processed.principal_amount > 0
    assert processed.interest_amount > 0
    assert loan.remaining_balance < initial_balance
    assert loan.last_payment_date == payment_data["payment_date"]

@pytest.mark.asyncio
async def test_process_payment_already_processed(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = processed_payment_fixture()
    payment = LoanPayment(loan_id=loan.id, **payment_data)
    db_session.add(payment)
    await db_session.flush()

    # Act & Assert
    with pytest.raises(PaymentProcessError):
        await LoanPaymentService.process_payment(
            db_session, payment.id, user_id=1
        )

@pytest.mark.asyncio
async def test_cancel_payment(db_session):
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
    cancelled = await LoanPaymentService.cancel_payment(
        db_session, payment.id, user_id=1
    )

    # Assert
    assert cancelled.status == PaymentStatus.CANCELLED
    assert cancelled.cancelled_by == 1
    assert cancelled.cancelled_at is not None

@pytest.mark.asyncio
async def test_cancel_completed_payment(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    payment_data = processed_payment_fixture()
    payment = LoanPayment(loan_id=loan.id, **payment_data)
    db_session.add(payment)
    await db_session.flush()

    # Act & Assert
    with pytest.raises(PaymentProcessError):
        await LoanPaymentService.cancel_payment(
            db_session, payment.id, user_id=1
        )

@pytest.mark.asyncio
async def test_get_loan_payments(db_session):
    # Arrange
    loan_data = loan_with_payments_fixture()
    loan = Loan(**loan_data)
    db_session.add(loan)
    await db_session.flush()

    # Crear varios pagos
    payment1 = LoanPayment(
        loan_id=loan.id,
        payment_date=date.today(),
        due_date=date.today(),
        amount=1000,
        payment_method=PaymentMethod.TRANSFER,
        status=PaymentStatus.COMPLETED
    )
    payment2 = LoanPayment(
        loan_id=loan.id,
        payment_date=date.today() + timedelta(days=30),
        due_date=date.today() + timedelta(days=30),
        amount=1000,
        payment_method=PaymentMethod.TRANSFER,
        status=PaymentStatus.PENDING
    )
    db_session.add_all([payment1, payment2])
    await db_session.flush()

    # Act
    payments = await LoanPaymentService.get_loan_payments(db_session, loan.id)

    # Assert
    assert len(payments) == 2
    assert any(p.status == PaymentStatus.COMPLETED for p in payments)
    assert any(p.status == PaymentStatus.PENDING for p in payments)

@pytest.mark.asyncio
async def test_get_payment(db_session):
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
    result = await LoanPaymentService.get_payment(db_session, payment.id)

    # Assert
    assert result is not None
    assert result.id == payment.id
    assert result.loan_id == loan.id
    assert result.amount == payment_data["amount"]

@pytest.mark.asyncio
async def test_get_payment_not_found(db_session):
    # Act
    result = await LoanPaymentService.get_payment(db_session, 999)

    # Assert
    assert result is None
