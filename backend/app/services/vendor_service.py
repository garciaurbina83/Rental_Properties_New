from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import vendor as crud_vendor
from app.crud import expense as crud_expense
from app.models.user import User
from app.schemas import vendor as schemas
from app.core.vendor_validation import vendor_validator
from app.services.notification_service import notification_service

class VendorService:
    @staticmethod
    async def create_vendor(
        db: Session,
        vendor_in: schemas.VendorCreate,
        current_user: User
    ) -> schemas.Vendor:
        """Create a new vendor with notifications."""
        # Validate vendor
        vendor_validator.validate_create(db, vendor_in, current_user)
        
        # Create vendor
        vendor = crud_vendor.create(db=db, obj_in=vendor_in)
        
        # Send notifications
        await notification_service.notify_vendor_created(db, vendor, current_user)
        
        return vendor

    @staticmethod
    async def update_vendor(
        db: Session,
        vendor_id: int,
        vendor_in: schemas.VendorUpdate,
        current_user: User
    ) -> schemas.Vendor:
        """Update a vendor with notifications."""
        # Validate update
        vendor_validator.validate_update(db, vendor_id, vendor_in, current_user)
        
        # Get existing vendor
        vendor = crud_vendor.get(db=db, id=vendor_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Update vendor
        updated_vendor = crud_vendor.update(
            db=db,
            db_obj=vendor,
            obj_in=vendor_in
        )
        
        # Send notifications
        await notification_service.notify_vendor_updated(db, updated_vendor, current_user)
        
        return updated_vendor

    @staticmethod
    async def rate_vendor(
        db: Session,
        vendor_id: int,
        rating_in: schemas.VendorRating,
        current_user: User
    ) -> schemas.Vendor:
        """Rate a vendor with notifications."""
        # Validate rating
        vendor_validator.validate_rating_update(db, vendor_id, rating_in.rating, current_user)
        
        # Update vendor rating
        vendor = crud_vendor.update_rating(
            db=db,
            vendor_id=vendor_id,
            rating=rating_in.rating
        )
        
        # Send notifications
        await notification_service.notify_vendor_rated(db, vendor, rating_in.rating, current_user)
        
        return vendor

    @staticmethod
    def get_vendor_with_stats(
        db: Session,
        vendor_id: int
    ) -> schemas.VendorWithStats:
        """Get vendor details with statistics."""
        return crud_vendor.get_with_stats(db=db, vendor_id=vendor_id)

    @staticmethod
    def get_top_vendors(
        db: Session,
        skip: int = 0,
        limit: int = 10
    ) -> List[schemas.VendorWithStats]:
        """Get list of top vendors by rating."""
        return crud_vendor.get_multi_with_stats(
            db=db,
            skip=skip,
            limit=limit,
            order_by="rating"
        )

    @staticmethod
    def search_vendors(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[schemas.Vendor]:
        """Search vendors by name or description."""
        return crud_vendor.search(
            db=db,
            query=query,
            skip=skip,
            limit=limit
        )

    @staticmethod
    def get_vendor_expenses(
        db: Session,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.Expense]:
        """Get list of expenses for a vendor."""
        return crud_expense.get_by_vendor_id(
            db=db,
            vendor_id=vendor_id,
            skip=skip,
            limit=limit
        )

vendor_service = VendorService()
