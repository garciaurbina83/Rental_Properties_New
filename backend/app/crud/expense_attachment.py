from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.expense_attachment import ExpenseAttachment
from app.schemas.expense_attachment import ExpenseAttachmentCreate, ExpenseAttachmentUpdate
from app.core.config import settings

class CRUDExpenseAttachment(CRUDBase[ExpenseAttachment, ExpenseAttachmentCreate, ExpenseAttachmentUpdate]):
    async def create_with_file(
        self,
        db: Session,
        *,
        expense_id: int,
        file: UploadFile,
        uploaded_by: int
    ) -> ExpenseAttachment:
        """Create a new expense attachment with file upload."""
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, "expenses", str(expense_id))
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create attachment record
        file_size = os.path.getsize(file_path)
        db_obj = ExpenseAttachment(
            expense_id=expense_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file_size,
            uploaded_by=uploaded_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_expense(
        self,
        db: Session,
        *,
        expense_id: int
    ) -> List[ExpenseAttachment]:
        """Get all attachments for a specific expense."""
        return db.query(ExpenseAttachment)\
            .filter(ExpenseAttachment.expense_id == expense_id)\
            .all()

    def remove(self, db: Session, *, id: int) -> ExpenseAttachment:
        """Remove an attachment and its associated file."""
        obj = db.query(ExpenseAttachment).get(id)
        if obj and os.path.exists(obj.file_path):
            os.remove(obj.file_path)
        return super().remove(db, id=id)

expense_attachment = CRUDExpenseAttachment(ExpenseAttachment)
