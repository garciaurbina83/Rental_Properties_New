from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/{expense_id}", response_model=schemas.ExpenseAttachment)
async def create_attachment(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new expense attachment.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return await crud.expense_attachment.create_with_file(
        db=db,
        expense_id=expense_id,
        file=file,
        uploaded_by=current_user.id
    )

@router.get("/{expense_id}", response_model=List[schemas.ExpenseAttachmentDetail])
def read_attachments(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve attachments for a specific expense.
    """
    expense = crud.expense.get(db=db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return crud.expense_attachment.get_by_expense(db=db, expense_id=expense_id)

@router.delete("/{attachment_id}")
def delete_attachment(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an attachment.
    """
    attachment = crud.expense_attachment.get(db=db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Check if user has permission to delete the attachment
    expense = crud.expense.get(db=db, id=attachment.expense_id)
    if not expense or (expense.created_by_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud.expense_attachment.remove(db=db, id=attachment_id)
    return {"status": "success"}
