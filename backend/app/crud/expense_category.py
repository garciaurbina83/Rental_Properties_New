from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.expense_category import ExpenseCategory
from app.schemas.expense_category import ExpenseCategoryCreate, ExpenseCategoryUpdate

class CRUDExpenseCategory(CRUDBase[ExpenseCategory, ExpenseCategoryCreate, ExpenseCategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ExpenseCategory]:
        return db.query(ExpenseCategory).filter(ExpenseCategory.name == name).first()
    
    def get_active_categories(self, db: Session) -> List[ExpenseCategory]:
        return db.query(ExpenseCategory).filter(ExpenseCategory.is_active == True).all()
    
    def get_root_categories(self, db: Session) -> List[ExpenseCategory]:
        return db.query(ExpenseCategory).filter(ExpenseCategory.parent_id == None).all()
    
    def get_children(self, db: Session, *, parent_id: int) -> List[ExpenseCategory]:
        return db.query(ExpenseCategory).filter(ExpenseCategory.parent_id == parent_id).all()

expense_category = CRUDExpenseCategory(ExpenseCategory)
