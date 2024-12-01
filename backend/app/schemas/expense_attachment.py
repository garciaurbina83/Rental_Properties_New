from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ExpenseAttachmentBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int

class ExpenseAttachmentCreate(ExpenseAttachmentBase):
    expense_id: int
    file_path: str
    uploaded_by: int

class ExpenseAttachmentInDBBase(ExpenseAttachmentBase):
    id: int
    expense_id: int
    file_path: str
    uploaded_by: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ExpenseAttachment(ExpenseAttachmentInDBBase):
    pass

class ExpenseAttachmentDetail(ExpenseAttachment):
    uploader: "UserBase"

from app.schemas.user import UserBase
ExpenseAttachmentDetail.update_forward_refs()
