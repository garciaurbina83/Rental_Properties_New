from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy import DateTime
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.vendor import Vendor, VendorRating
from app.models.expense import Expense
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorWithStats

class CRUDVendor(CRUDBase[Vendor, VendorCreate, VendorUpdate]):
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> List[Vendor]:
        query = db.query(self.model)
        
        if search:
            search_filter = or_(
                self.model.name.ilike(f"%{search}%"),
                self.model.business_type.ilike(f"%{search}%"),
                self.model.contact_person.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def update_rating(
        self,
        db: Session,
        *,
        vendor_id: int,
        rating: float,
        rated_by: int
    ) -> Vendor:
        # Create new rating
        vendor_rating = VendorRating(
            vendor_id=vendor_id,
            rating=rating,
            rated_by=rated_by,
            rated_at=datetime.utcnow()
        )
        db.add(vendor_rating)
        
        # Update vendor's average rating
        vendor = self.get(db=db, id=vendor_id)
        if vendor:
            ratings = db.query(VendorRating).filter(
                VendorRating.vendor_id == vendor_id
            ).all()
            
            total_rating = sum(r.rating for r in ratings)
            vendor.rating = total_rating / len(ratings)
            
            db.commit()
            db.refresh(vendor)
        
        return vendor

    def get_with_stats(
        self,
        db: Session,
        *,
        vendor_id: int
    ) -> Optional[VendorWithStats]:
        vendor = self.get(db=db, id=vendor_id)
        if not vendor:
            return None

        # Get expense statistics
        expense_stats = db.query(
            func.count(Expense.id).label("total_expenses"),
            func.sum(Expense.amount).label("total_amount"),
            func.avg(Expense.amount).label("average_expense"),
            func.max(Expense.date_incurred).label("last_expense_date")
        ).filter(
            Expense.vendor_id == vendor_id
        ).first()

        # Get rating statistics
        rating_stats = db.query(
            func.count(VendorRating.id).label("rating_count"),
            func.avg(VendorRating.rating).label("average_rating")
        ).filter(
            VendorRating.vendor_id == vendor_id
        ).first()

        return VendorWithStats(
            **vendor.__dict__,
            total_expenses=expense_stats.total_expenses or 0,
            total_amount=expense_stats.total_amount or 0,
            average_expense=expense_stats.average_expense or 0,
            last_expense_date=expense_stats.last_expense_date,
            rating_count=rating_stats.rating_count or 0,
            average_rating=rating_stats.average_rating
        )

vendor = CRUDVendor(Vendor)
