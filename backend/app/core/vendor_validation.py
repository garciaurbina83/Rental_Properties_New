from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.vendor import Vendor
from app.models.expense import Expense
from app.models.user import User
from app.core.permissions import check_permission
from app.schemas.vendor import VendorCreate, VendorUpdate

class VendorValidator:
    @staticmethod
    def validate_name(name: str):
        """Validate vendor name."""
        if not name or len(name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor name is required"
            )

    @staticmethod
    def validate_contact_info(email: Optional[str], phone: Optional[str]):
        """Validate that at least one contact method is provided."""
        if not email and not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one contact method (email or phone) is required"
            )

    @staticmethod
    def validate_tax_id(tax_id: Optional[str]):
        """Validate tax ID format if provided."""
        if tax_id:
            # Add specific tax ID format validation based on your requirements
            if len(tax_id) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tax ID format"
                )

    @staticmethod
    def validate_duplicate_vendor(
        db: Session,
        name: str,
        tax_id: Optional[str] = None,
        exclude_id: Optional[int] = None
    ):
        """Check for duplicate vendors."""
        query = select(Vendor).where(Vendor.name == name)
        
        if exclude_id:
            query = query.where(Vendor.id != exclude_id)
        
        result = db.execute(query)
        existing_vendor = result.scalar_one_or_none()
        
        if existing_vendor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor with this name already exists"
            )
        
        if tax_id:
            query = select(Vendor).where(Vendor.tax_id == tax_id)
            if exclude_id:
                query = query.where(Vendor.id != exclude_id)
            
            result = db.execute(query)
            existing_vendor = result.scalar_one_or_none()
            
            if existing_vendor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vendor with this tax ID already exists"
                )

    @staticmethod
    def validate_rating(rating: float):
        """Validate vendor rating."""
        if rating < 0 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 0 and 5"
            )

    @staticmethod
    def validate_can_rate_vendor(
        db: Session,
        vendor_id: int,
        user: User
    ):
        """Validate that user has permission to rate vendor."""
        # Check if user has worked with vendor
        expenses = db.query(Expense).filter(
            Expense.vendor_id == vendor_id,
            Expense.created_by == user.id
        ).first()
        
        if not expenses:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must have worked with this vendor to rate them"
            )

    @classmethod
    def validate_create(
        cls,
        db: Session,
        vendor: VendorCreate,
        user: User
    ):
        """Validate vendor creation."""
        cls.validate_name(vendor.name)
        cls.validate_contact_info(vendor.email, vendor.phone)
        cls.validate_tax_id(vendor.tax_id)
        cls.validate_duplicate_vendor(db, vendor.name, vendor.tax_id)

    @classmethod
    def validate_update(
        cls,
        db: Session,
        vendor_id: int,
        vendor: VendorUpdate,
        user: User
    ):
        """Validate vendor update."""
        if vendor.name is not None:
            cls.validate_name(vendor.name)
            cls.validate_duplicate_vendor(db, vendor.name, None, exclude_id=vendor_id)
        
        if vendor.email is not None or vendor.phone is not None:
            current_vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
            cls.validate_contact_info(
                vendor.email if vendor.email is not None else current_vendor.email,
                vendor.phone if vendor.phone is not None else current_vendor.phone
            )
        
        if vendor.tax_id is not None:
            cls.validate_tax_id(vendor.tax_id)
            cls.validate_duplicate_vendor(db, "", vendor.tax_id, exclude_id=vendor_id)

    @classmethod
    def validate_rating_update(
        cls,
        db: Session,
        vendor_id: int,
        rating: float,
        user: User
    ):
        """Validate vendor rating update."""
        cls.validate_rating(rating)
        cls.validate_can_rate_vendor(db, vendor_id, user)

vendor_validator = VendorValidator()
