from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.ExpenseCategory])
def read_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve expense categories.
    """
    categories = crud.expense_category.get_multi(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=schemas.ExpenseCategory)
def create_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: schemas.ExpenseCategoryCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new expense category.
    """
    if crud.expense_category.get_by_name(db, name=category_in.name):
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists."
        )
    category = crud.expense_category.create(db=db, obj_in=category_in)
    return category

@router.put("/{category_id}", response_model=schemas.ExpenseCategory)
def update_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: schemas.ExpenseCategoryUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update expense category.
    """
    category = crud.expense_category.get(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.expense_category.update(db=db, db_obj=category, obj_in=category_in)
    return category

@router.get("/active", response_model=List[schemas.ExpenseCategory])
def read_active_categories(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve active expense categories.
    """
    categories = crud.expense_category.get_active_categories(db)
    return categories

@router.get("/root", response_model=List[schemas.ExpenseCategory])
def read_root_categories(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve root expense categories (categories without parent).
    """
    categories = crud.expense_category.get_root_categories(db)
    return categories

@router.get("/{category_id}/children", response_model=List[schemas.ExpenseCategory])
def read_category_children(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve child categories of a specific category.
    """
    if not crud.expense_category.get(db=db, id=category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    categories = crud.expense_category.get_children(db=db, parent_id=category_id)
    return categories
