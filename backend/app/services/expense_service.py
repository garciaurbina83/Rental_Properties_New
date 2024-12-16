from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
import logging

from app.crud import expense as crud_expense
from app.crud import property as crud_property
from app.crud import vendor as crud_vendor
from app.crud import expense_category as crud_expense_category
from app.models.expense import Expense
from app.models.user import User
from app.schemas import expense as schemas
from app.core.expense_validation import expense_validator
from app.services.notification_service import notification_service
from app.services.audit_service import audit_service
from app.core.permissions import ExpensePermission

logger = logging.getLogger(__name__)

class ExpenseService:
    async def create_expense(
        self, 
        db: Session, 
        expense_in: schemas.ExpenseCreate, 
        current_user: User,
        request: Request = None
    ) -> Expense:
        """Create a new expense with validation and notifications."""
        try:
            # Check permissions
            permission = ExpensePermission(current_user)
            if not permission.can_create():
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to create expense"
                )

            # Validate property exists if provided
            if expense_in.property_id:
                property = crud_property.get(db, id=expense_in.property_id)
                if not property:
                    raise HTTPException(status_code=404, detail="Property not found")

            # Validate vendor exists if provided
            if expense_in.vendor_id:
                vendor = crud_vendor.get(db, id=expense_in.vendor_id)
                if not vendor:
                    raise HTTPException(status_code=404, detail="Vendor not found")

            # Create expense
            expense = crud_expense.create(
                db=db,
                obj_in=expense_in,
                created_by_id=current_user.id
            )

            # Log action
            await audit_service.log_action(
                db=db,
                entity_type="expense",
                entity_id=expense.id,
                action="create",
                user=current_user,
                changes=expense_in.dict(),
                request=request
            )

            # Send notification
            await notification_service.notify_expense_created(
                db=db,
                expense=expense,
                current_user=current_user
            )

            return expense
            
        except Exception as e:
            logger.error(f"Error creating expense: {str(e)}")
            raise

    async def update_expense(
        self,
        db: Session,
        *,
        expense_id: int,
        expense_in: schemas.ExpenseUpdate,
        current_user: User,
        request: Request = None
    ) -> Expense:
        """Update expense with validation and notifications."""
        try:
            # Get existing expense
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")

            # Check permissions
            permission = ExpensePermission(current_user, expense)
            if not permission.can_update():
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to update expense"
                )

            # Validate property exists if being updated
            if expense_in.property_id:
                property = crud_property.get(db, id=expense_in.property_id)
                if not property:
                    raise HTTPException(status_code=404, detail="Property not found")

            # Validate vendor exists if being updated
            if expense_in.vendor_id:
                vendor = crud_vendor.get(db, id=expense_in.vendor_id)
                if not vendor:
                    raise HTTPException(status_code=404, detail="Vendor not found")

            # Get changes for audit log
            old_data = {
                k: v for k, v in expense.__dict__.items()
                if not k.startswith('_')
            }
            
            # Update expense
            expense = crud_expense.update(db=db, db_obj=expense, obj_in=expense_in)

            # Log changes
            changes = audit_service.compare_objects(
                old_data,
                {**old_data, **expense_in.dict(exclude_unset=True)}
            )
            await audit_service.log_action(
                db=db,
                entity_type="expense",
                entity_id=expense.id,
                action="update",
                user=current_user,
                changes=changes,
                request=request
            )

            # Send notification
            await notification_service.notify_expense_updated(
                db=db,
                expense=expense,
                current_user=current_user
            )

            return expense

        except Exception as e:
            logger.error(f"Error updating expense: {str(e)}")
            raise

    async def delete_expense(self, db: Session, expense_id: int, current_user: User) -> Expense:
        """Delete an expense with validation."""
        try:
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")

            if not crud_expense.is_owner(db, expense_id=expense.id, user_id=current_user.id):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            return crud_expense.remove(db=db, id=expense_id)
        except Exception as e:
            logger.error(f"Error deleting expense: {str(e)}")
            raise

    async def approve_expense(
        self,
        db: Session,
        *,
        expense_id: int,
        current_user: User,
        request: Request = None
    ) -> Expense:
        """Approve expense with validation and notifications."""
        try:
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")

            # Check permissions
            permission = ExpensePermission(current_user, expense)
            if not permission.can_approve():
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to approve expense"
                )

            # Check approval limit
            if not permission.check_amount_limit(expense.amount):
                raise HTTPException(
                    status_code=403,
                    detail="Amount exceeds your approval limit"
                )

            # Approve expense
            expense = crud_expense.approve(
                db=db,
                expense=expense,
                approved_by=current_user.id
            )

            # Log action
            await audit_service.log_action(
                db=db,
                entity_type="expense",
                entity_id=expense.id,
                action="approve",
                user=current_user,
                request=request
            )

            # Send notification
            await notification_service.notify_expense_approved(
                db=db,
                expense=expense,
                current_user=current_user
            )

            return expense

        except Exception as e:
            logger.error(f"Error approving expense: {str(e)}")
            raise

    async def cancel_expense(self, db: Session, expense_id: int, current_user: User) -> Expense:
        """Cancel an expense with validation."""
        try:
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")

            if expense.status not in [schemas.ExpenseStatus.PENDING, schemas.ExpenseStatus.APPROVED]:
                raise HTTPException(
                    status_code=400,
                    detail="Only pending or approved expenses can be cancelled"
                )

            update_data = {
                "status": schemas.ExpenseStatus.CANCELLED,
                "cancelled_by": current_user.id,
                "cancelled_at": datetime.utcnow()
            }
            return crud_expense.update(db=db, db_obj=expense, obj_in=update_data)
        except Exception as e:
            logger.error(f"Error cancelling expense: {str(e)}")
            raise

    async def add_attachment(
        self, 
        db: Session, 
        expense_id: int, 
        attachment_in: schemas.ExpenseAttachmentCreate, 
        current_user: User
    ) -> schemas.ExpenseAttachment:
        """Add an attachment to an expense."""
        try:
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")

            if not crud_expense.is_owner(db, expense_id=expense.id, user_id=current_user.id):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            return await crud_expense.add_attachment(
                db=db,
                expense_id=expense_id,
                attachment_in=attachment_in
            )
        except Exception as e:
            logger.error(f"Error adding attachment: {str(e)}")
            raise

    def get_expense_summary(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        property_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> schemas.ExpenseSummary:
        """Get expense summary with optional filters."""
        try:
            return crud_expense.get_summary(
                db,
                start_date=start_date,
                end_date=end_date,
                property_id=property_id,
                category=category
            )
        except Exception as e:
            logger.error(f"Error getting expense summary: {str(e)}")
            raise

    async def get_expenses_by_category(
        self,
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        """Get all expenses for a specific category."""
        category = crud_expense_category.get(db, id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return crud_expense.get_by_category(db, category_id=category_id, skip=skip, limit=limit)

    async def get_category_summary(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get expense summary grouped by category."""
        return crud_expense.get_category_summary(
            db,
            start_date=start_date,
            end_date=end_date
        )

    def get_category_summary_old(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[schemas.ExpenseCategorySummary]:
        """Get expense summary by category."""
        try:
            return crud_expense.get_category_summary(db, start_date=start_date, end_date=end_date)
        except Exception as e:
            logger.error(f"Error getting category summary: {str(e)}")
            raise

    def get_property_summary(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[schemas.PropertyExpenseSummary]:
        """Get expense summary by property."""
        try:
            return crud_expense.get_property_summary(db, start_date=start_date, end_date=end_date)
        except Exception as e:
            logger.error(f"Error getting property summary: {str(e)}")
            raise

    def get_vendor_summary(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[schemas.VendorExpenseSummary]:
        """Get expense summary by vendor."""
        try:
            return crud_expense.get_vendor_summary(db, start_date=start_date, end_date=end_date)
        except Exception as e:
            logger.error(f"Error getting vendor summary: {str(e)}")
            raise

    def get_recurring_expenses(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 10
    ) -> List[schemas.RecurringExpenseSummary]:
        """Get recurring expenses for a user."""
        try:
            return crud_expense.get_recurring_expenses(
                db,
                user_id=current_user.id,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting recurring expenses: {str(e)}")
            raise

expense_service = ExpenseService()
