import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.expense_service import expense_service
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseStatus
from app.models.expense import Expense
from app.models.user import User

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True,
        roles=["expense_approver"],
        approval_limit=Decimal("1000.00")
    )

@pytest.fixture
def mock_expense(db_session):
    expense = Expense(
        id=1,
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        status=ExpenseStatus.PENDING_APPROVAL,
        created_by_id=1
    )
    db_session.add(expense)
    db_session.commit()
    return expense

async def test_create_expense(db_session, mock_user):
    """Test expense creation."""
    expense_data = ExpenseCreate(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense"
    )
    
    with patch('app.services.notification_service.notify_expense_created'):
        expense = await expense_service.create_expense(
            db_session,
            expense_data,
            mock_user
        )
    
    assert expense.amount == Decimal("100.50")
    assert expense.created_by_id == mock_user.id
    assert expense.status == ExpenseStatus.PENDING_APPROVAL

async def test_update_expense(db_session, mock_user, mock_expense):
    """Test expense update."""
    update_data = ExpenseUpdate(
        amount=Decimal("150.75"),
        description="Updated description"
    )
    
    with patch('app.services.notification_service.notify_expense_updated'):
        expense = await expense_service.update_expense(
            db_session,
            expense_id=mock_expense.id,
            expense_in=update_data,
            current_user=mock_user
        )
    
    assert expense.amount == Decimal("150.75")
    assert expense.description == "Updated description"

async def test_approve_expense(db_session, mock_user, mock_expense):
    """Test expense approval."""
    with patch('app.services.notification_service.notify_expense_approved'):
        expense = await expense_service.approve_expense(
            db_session,
            expense_id=mock_expense.id,
            current_user=mock_user
        )
    
    assert expense.status == ExpenseStatus.APPROVED
    assert expense.approved_by == mock_user.id
    assert expense.approved_at is not None

async def test_approve_expense_over_limit(db_session, mock_user, mock_expense):
    """Test approval of expense over user's limit."""
    # Set expense amount over user's approval limit
    mock_expense.amount = Decimal("2000.00")
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        await expense_service.approve_expense(
            db_session,
            expense_id=mock_expense.id,
            current_user=mock_user
        )
    assert exc.value.status_code == 403
    assert "exceeds your approval limit" in str(exc.value.detail)

async def test_get_expense_summary(db_session, mock_expense):
    """Test expense summary generation."""
    summary = await expense_service.get_expense_summary(
        db_session,
        start_date=date.today(),
        end_date=date.today()
    )
    
    assert summary["total_amount"] > 0
    assert summary["count"] > 0

async def test_get_category_summary(db_session, mock_expense):
    """Test category summary generation."""
    summary = await expense_service.get_category_summary(
        db_session,
        start_date=date.today(),
        end_date=date.today()
    )
    
    assert isinstance(summary, list)
    if summary:
        assert "category" in summary[0]
        assert "total_amount" in summary[0]
