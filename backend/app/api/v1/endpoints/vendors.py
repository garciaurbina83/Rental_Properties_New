from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date

from app.api import deps
from app.schemas import vendor as schemas, expense as expense_schemas
from app.services import vendor_service, notification_service
from app.crud import expense as crud_expense
from app.core.security import get_current_active_user
from app.models.user import User
from app.core.vendor_validation import vendor_validator

router = APIRouter()

@router.post("/", response_model=schemas.Vendor)
async def create_vendor(
    *,
    vendor_in: schemas.VendorCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Create new vendor.
    """
    vendor = await vendor_service.create_vendor(db, vendor_in, current_user)
    
    # Send notification asynchronously
    await notification_service.notify_vendor_created(
        db,
        vendor,
        current_user,
        background_tasks
    )
    
    return vendor

@router.get("/", response_model=List[schemas.Vendor])
def read_vendors(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve vendors with optional filtering.
    """
    vendors = vendor_service.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        filters={
            "is_active": is_active,
            "is_verified": is_verified
        }
    )
    return vendors

@router.get("/{vendor_id}", response_model=schemas.Vendor)
def read_vendor(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get vendor by ID.
    """
    vendor = vendor_service.get(db=db, id=vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.put("/{vendor_id}", response_model=schemas.Vendor)
async def update_vendor(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    vendor_in: schemas.VendorUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update vendor.
    """
    return await vendor_service.update_vendor(db, vendor_id, vendor_in, current_user)

@router.delete("/{vendor_id}")
def delete_vendor(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete vendor.
    """
    vendor = vendor_service.get(db=db, id=vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor_service.remove(db=db, id=vendor_id)
    return {"message": "Vendor deleted successfully"}

@router.post("/{vendor_id}/rate", response_model=schemas.Vendor)
async def rate_vendor(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    rating_in: schemas.VendorRating,
    current_user: User = Depends(get_current_active_user)
):
    """
    Rate a vendor.
    """
    return await vendor_service.rate_vendor(db, vendor_id, rating_in, current_user)

@router.get("/{vendor_id}/stats", response_model=schemas.VendorWithStats)
def get_vendor_stats(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get vendor statistics.
    """
    return vendor_service.get_vendor_with_stats(db, vendor_id)

@router.get("/top", response_model=List[schemas.VendorWithStats])
def get_top_vendors(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get top rated vendors.
    """
    return vendor_service.get_top_vendors(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[schemas.Vendor])
def search_vendors(
    *,
    db: Session = Depends(deps.get_db),
    query: str,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search vendors.
    """
    return vendor_service.search_vendors(db, query, skip=skip, limit=limit)

@router.get("/{vendor_id}/expenses", response_model=List[expense_schemas.ExpenseDetail])
def get_vendor_expenses(
    *,
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[expense_schemas.ExpenseStatus] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all expenses for a vendor.
    """
    vendor = vendor_service.get(db=db, id=vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    expenses = crud_expense.get_by_vendor_id(
        db=db,
        vendor_id=vendor_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        status=status
    )
    return expenses
