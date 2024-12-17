import pytest
from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException

from app.core.expense_validation import expense_validator
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseStatus
from app.models.expense import Expense

def test_validate_create_expense_valid(db_session):
    """Test validation of valid expense creation."""
    expense_data = ExpenseCreate(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        property_id=1
    )
    
    # Should not raise any exception
    expense_validator.validate_create(db_session, expense_data)

def test_validate_create_expense_invalid_amount():
    """Test validation of expense with invalid amount."""
    expense_data = ExpenseCreate(
        amount=Decimal("-100.50"),
        date=date.today(),
        description="Test expense"
    )
    
    with pytest.raises(HTTPException) as exc:
        expense_validator.validate_create(None, expense_data)
    assert exc.value.status_code == 400
    assert "amount must be positive" in str(exc.value.detail)

def test_validate_create_expense_future_date():
    """Test validation of expense with future date."""
    future_date = date.today().replace(year=date.today().year + 1)
    expense_data = ExpenseCreate(
        amount=Decimal("100.50"),
        date=future_date,
        description="Test expense"
    )
    
    with pytest.raises(HTTPException) as exc:
        expense_validator.validate_create(None, expense_data)
    assert exc.value.status_code == 400
    assert "date cannot be in the future" in str(exc.value.detail)

def test_validate_update_expense_valid(db_session):
    """Test validation of valid expense update."""
    # Create initial expense
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        status=ExpenseStatus.PENDING_APPROVAL
    )
    db_session.add(expense)
    db_session.commit()
    
    # Update data
    update_data = ExpenseUpdate(
        amount=Decimal("150.75"),
        description="Updated description"
    )
    
    # Should not raise any exception
    expense_validator.validate_update(db_session, expense, update_data)

def test_validate_update_approved_expense(db_session):
    """Test validation of updating an approved expense."""
    # Create approved expense
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        status=ExpenseStatus.APPROVED,
        approved_by=1,
        approved_at=datetime.utcnow()
    )
    db_session.add(expense)
    db_session.commit()
    
    update_data = ExpenseUpdate(amount=Decimal("150.75"))
    
    with pytest.raises(HTTPException) as exc:
        expense_validator.validate_update(db_session, expense, update_data)
    assert exc.value.status_code == 400
    assert "approved expense cannot be modified" in str(exc.value.detail)

def test_validate_recurring_expense():
    """Test validation of recurring expense data."""
    expense_data = ExpenseCreate(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        is_recurring=True,
        recurrence_interval="invalid"
    )
    
    with pytest.raises(HTTPException) as exc:
        expense_validator.validate_create(None, expense_data)
    assert exc.value.status_code == 400
    assert "invalid recurrence interval" in str(exc.value.detail)
