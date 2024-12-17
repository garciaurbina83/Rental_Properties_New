from typing import Optional, List
from pydantic import BaseModel

class ExpenseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategoryUpdate(ExpenseCategoryBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class ExpenseCategoryInDBBase(ExpenseCategoryBase):
    id: int
    
    class Config:
        orm_mode = True

class ExpenseCategory(ExpenseCategoryInDBBase):
    children: List['ExpenseCategory'] = []
    parent: Optional['ExpenseCategory'] = None

ExpenseCategory.update_forward_refs()
