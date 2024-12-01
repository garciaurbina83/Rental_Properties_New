from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
from datetime import datetime

from app.api import deps
from app.schemas import expense as schemas
from app.crud import expense as crud
from app.core.security import get_current_active_user
from app.models.user import User
from app.core.expense_validation import expense_validator
from app.services.expense_service import expense_service
from app.services.notification_service import notification_service

router = APIRouter()

@router.post("/", response_model=schemas.Expense)
async def create_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_in: schemas.ExpenseCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new expense.
    """
    # Validate expense data
    expense_validator.validate_create(db, expense_in, current_user)
    
    # Create expense
    return await expense_service.create_expense(db, expense_in, current_user)

@router.get("/", response_model=List[schemas.ExpenseDetail])
def read_expenses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    expense_type: Optional[schemas.ExpenseType] = None,
    status: Optional[schemas.ExpenseStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_recurring: Optional[bool] = None,
    requires_approval: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve expenses with optional filtering.
    """
    filters = {
        "property_id": property_id,
        "vendor_id": vendor_id,
        "expense_type": expense_type,
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "is_recurring": is_recurring,
        "requires_approval": requires_approval
    }
    expenses = crud.expense.get_multi_with_filters(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters
    )
    return expenses

@router.get("/{expense_id}", response_model=schemas.ExpenseDetail)
def read_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense by ID.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=schemas.Expense)
async def update_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    expense_in: schemas.ExpenseUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update expense.
    """
    # Validate expense data
    expense_validator.validate_update(db, expense_id, expense_in, current_user)
    
    # Update expense
    return await expense_service.update_expense(db, expense_id, expense_in, current_user)

@router.delete("/{expense_id}")
def delete_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense = crud.expense.remove(db=db, id=expense_id)
    return {"message": "Expense deleted successfully"}

@router.post("/{expense_id}/approve", response_model=schemas.Expense)
async def approve_expense(
    expense_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Approve an expense."""
    expense = expense_service.approve_expense(db, expense_id, current_user)
    
    # Send notification asynchronously
    await notification_service.notify_expense_approved(
        db,
        expense,
        current_user,
        background_tasks
    )
    
    return expense

@router.post("/{expense_id}/reject", response_model=schemas.Expense)
def reject_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    rejection_reason: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Reject an expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.status != schemas.ExpenseStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Expense is not pending approval")
    
    update_data = {
        "status": schemas.ExpenseStatus.REJECTED,
        "rejection_reason": rejection_reason,
        "approved_by": current_user.id,
        "approved_at": date.today()
    }
    expense = crud.expense.update(db=db, db_obj=expense, obj_in=update_data)
    return expense

@router.post("/{expense_id}/recurring", response_model=schemas.Expense)
def create_recurring_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    recurrence_interval: schemas.RecurrenceInterval,
    recurrence_end_date: date,
    current_user: User = Depends(get_current_active_user)
):
    """
    Convert an expense to a recurring expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.is_recurring:
        raise HTTPException(status_code=400, detail="Expense is already recurring")
    
    update_data = {
        "is_recurring": True,
        "recurrence_interval": recurrence_interval,
        "recurrence_end_date": recurrence_end_date
    }
    expense = crud.expense.update(db=db, db_obj=expense, obj_in=update_data)
    return expense

@router.post("/{expense_id}/cancel", response_model=schemas.Expense)
async def cancel_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel an expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.status not in [schemas.ExpenseStatus.PENDING, schemas.ExpenseStatus.APPROVED]:
        raise HTTPException(
            status_code=400,
            detail="Only pending or approved expenses can be cancelled"
        )
    
    return await expense_service.cancel_expense(db, expense_id, current_user)

@router.post("/{expense_id}/attachments", response_model=schemas.ExpenseAttachment)
async def add_attachment(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    attachment_in: schemas.ExpenseAttachmentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add attachment to expense.
    """
    return await expense_service.add_attachment(db, expense_id, attachment_in, current_user)

@router.get("/{expense_id}/attachments", response_model=List[schemas.ExpenseAttachment])
def get_expense_attachments(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all attachments for an expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    attachments = crud.expense.get_attachments(db=db, expense_id=expense_id)
    return attachments

@router.get("/summary", response_model=schemas.ExpenseSummary)
def get_expense_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    property_id: Optional[int] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense summary.
    """
    return expense_service.get_expense_summary(
        db,
        start_date=start_date,
        end_date=end_date,
        property_id=property_id,
        category=category
    )

@router.get("/summary/category", response_model=List[schemas.ExpenseCategorySummary])
def get_category_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense summary by category.
    """
    return expense_service.get_category_summary(db, start_date=start_date, end_date=end_date)

@router.get("/summary/property", response_model=List[schemas.PropertyExpenseSummary])
def get_property_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense summary by property.
    """
    return expense_service.get_property_summary(db, start_date=start_date, end_date=end_date)

@router.get("/summary/vendor", response_model=List[schemas.VendorExpenseSummary])
def get_vendor_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense summary by vendor.
    """
    return expense_service.get_vendor_summary(db, start_date=start_date, end_date=end_date)

@router.get("/recurring", response_model=List[schemas.RecurringExpenseSummary])
def get_recurring_expenses(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recurring expenses.
    """
    return expense_service.get_recurring_expenses(db, current_user, skip=skip, limit=limit)
