import pytest
from datetime import date, datetime
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.expense import Expense
from app.schemas.expense import ExpenseStatus
from app.core.security import create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_token_headers(db_session):
    access_token = create_access_token(
        data={"sub": "test@example.com", "user_id": 1}
    )
    return {"Authorization": f"Bearer {access_token}"}

def test_create_expense(client, user_token_headers):
    """Test expense creation endpoint."""
    data = {
        "amount": 100.50,
        "date": date.today().isoformat(),
        "description": "Test expense",
        "expense_type": "maintenance"
    }
    
    response = client.post(
        "/api/v1/expenses/",
        headers=user_token_headers,
        json=data
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["amount"] == 100.50
    assert content["description"] == "Test expense"
    assert content["status"] == ExpenseStatus.PENDING_APPROVAL.value

def test_read_expense(client, user_token_headers, db_session):
    """Test reading expense endpoint."""
    # Create test expense
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        created_by_id=1
    )
    db_session.add(expense)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/expenses/{expense.id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == expense.id
    assert content["amount"] == float(expense.amount)

def test_update_expense(client, user_token_headers, db_session):
    """Test updating expense endpoint."""
    # Create test expense
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        created_by_id=1
    )
    db_session.add(expense)
    db_session.commit()
    
    update_data = {
        "amount": 150.75,
        "description": "Updated description"
    }
    
    response = client.put(
        f"/api/v1/expenses/{expense.id}",
        headers=user_token_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["amount"] == 150.75
    assert content["description"] == "Updated description"

def test_approve_expense(client, user_token_headers, db_session):
    """Test expense approval endpoint."""
    # Create test expense
    expense = Expense(
        amount=Decimal("100.50"),
        date=date.today(),
        description="Test expense",
        status=ExpenseStatus.PENDING_APPROVAL,
        created_by_id=1
    )
    db_session.add(expense)
    db_session.commit()
    
    response = client.post(
        f"/api/v1/expenses/{expense.id}/approve",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == ExpenseStatus.APPROVED.value
    assert content["approved_by"] is not None

def test_get_expense_summary(client, user_token_headers):
    """Test expense summary endpoint."""
    params = {
        "start_date": date.today().isoformat(),
        "end_date": date.today().isoformat()
    }
    
    response = client.get(
        "/api/v1/expenses/summary",
        headers=user_token_headers,
        params=params
    )
    
    assert response.status_code == 200
    content = response.json()
    assert "total_amount" in content
    assert "count" in content

def test_export_expenses(client, user_token_headers):
    """Test expense export endpoint."""
    params = {
        "start_date": date.today().isoformat(),
        "end_date": date.today().isoformat()
    }
    
    response = client.get(
        "/api/v1/expenses/export",
        headers=user_token_headers,
        params=params
    )
    
    assert response.status_code == 200
    assert "filename" in response.json()
    assert "file_path" in response.json()
