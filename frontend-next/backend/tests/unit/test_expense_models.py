import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.schemas.expense import ExpenseStatus, ExpenseType

def test_expense_model_creation():
    """Test basic expense model creation."""
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        expense_type=ExpenseType.MAINTENANCE,
        status=ExpenseStatus.PENDING_APPROVAL
    )
    
    assert expense.amount == Decimal("100.50")
    assert expense.date == date.today()
    assert expense.description == "Test expense"
    assert expense.expense_type == ExpenseType.MAINTENANCE
    assert expense.status == ExpenseStatus.PENDING_APPROVAL

def test_expense_relationships(db_session):
    """Test expense relationships with other models."""
    # Create test category
    category = ExpenseCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    # Create expense with relationships
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        category_id=category.id
    )
    db_session.add(expense)
    db_session.commit()
    
    # Test relationships
    assert expense.category.name == "Test Category"

def test_expense_approval_fields():
    """Test expense approval-related fields."""
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        status=ExpenseStatus.APPROVED,
        approved_by=1,
        approved_at=datetime.utcnow()
    )
    
    assert expense.status == ExpenseStatus.APPROVED
    assert expense.approved_by == 1
    assert expense.approved_at is not None

def test_expense_recurring_fields():
    """Test expense recurring fields."""
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        is_recurring=True,
        recurrence_interval="monthly",
        recurrence_day=1
    )
    
    assert expense.is_recurring is True
    assert expense.recurrence_interval == "monthly"
    assert expense.recurrence_day == 1

def test_expense_custom_fields():
    """Test expense custom fields."""
    custom_fields = {
        "invoice_number": "INV-001",
        "payment_method": "credit_card"
    }
    
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        custom_fields=custom_fields
    )
    
    assert expense.custom_fields == custom_fields
    assert expense.custom_fields["invoice_number"] == "INV-001"
