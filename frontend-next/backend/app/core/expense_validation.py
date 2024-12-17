from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

from app.models.user import User
from app.schemas import expense as schemas
from app.crud import expense as crud_expense
from app.crud import property as crud_property
from app.crud import vendor as crud_vendor

logger = logging.getLogger(__name__)

class ExpenseValidator:
    def validate_create(
        self, 
        db: Session, 
        expense_in: schemas.ExpenseCreate, 
        current_user: User
    ) -> None:
        """Validate expense creation data."""
        try:
            # Validate amount
            if expense_in.amount <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Amount must be greater than zero"
                )

            # Validate date
            if expense_in.date > date.today():
                raise HTTPException(
                    status_code=400,
                    detail="Expense date cannot be in the future"
                )

            # Validate property if provided
            if expense_in.property_id:
                property = crud_property.get(db, id=expense_in.property_id)
                if not property:
                    raise HTTPException(
                        status_code=404,
                        detail="Property not found"
                    )

            # Validate vendor if provided
            if expense_in.vendor_id:
                vendor = crud_vendor.get(db, id=expense_in.vendor_id)
                if not vendor:
                    raise HTTPException(
                        status_code=404,
                        detail="Vendor not found"
                    )

            # Validate category
            if not expense_in.category:
                raise HTTPException(
                    status_code=400,
                    detail="Category is required"
                )

            # Validate description
            if not expense_in.description:
                raise HTTPException(
                    status_code=400,
                    detail="Description is required"
                )

            # Validate recurring expense data if applicable
            if expense_in.is_recurring:
                self._validate_recurring_data(expense_in)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating expense creation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error validating expense data"
            )

    def validate_update(
        self, 
        db: Session, 
        expense_id: int, 
        expense_in: schemas.ExpenseUpdate, 
        current_user: User
    ) -> None:
        """Validate expense update data."""
        try:
            # Get existing expense
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(
                    status_code=404,
                    detail="Expense not found"
                )

            # Check permissions
            if not crud_expense.is_owner(db, expense_id=expense.id, user_id=current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )

            # Validate amount if provided
            if expense_in.amount is not None and expense_in.amount <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Amount must be greater than zero"
                )

            # Validate date if provided
            if expense_in.date and expense_in.date > date.today():
                raise HTTPException(
                    status_code=400,
                    detail="Expense date cannot be in the future"
                )

            # Validate property if provided
            if expense_in.property_id:
                property = crud_property.get(db, id=expense_in.property_id)
                if not property:
                    raise HTTPException(
                        status_code=404,
                        detail="Property not found"
                    )

            # Validate vendor if provided
            if expense_in.vendor_id:
                vendor = crud_vendor.get(db, id=expense_in.vendor_id)
                if not vendor:
                    raise HTTPException(
                        status_code=404,
                        detail="Vendor not found"
                    )

            # Validate recurring expense data if applicable
            if expense_in.is_recurring:
                self._validate_recurring_data(expense_in)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating expense update: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error validating expense data"
            )

    def validate_approval(self, db: Session, expense_id: int, current_user: User) -> None:
        """Validate expense approval."""
        try:
            expense = crud_expense.get(db, id=expense_id)
            if not expense:
                raise HTTPException(
                    status_code=404,
                    detail="Expense not found"
                )

            if expense.status != schemas.ExpenseStatus.PENDING_APPROVAL:
                raise HTTPException(
                    status_code=400,
                    detail="Expense is not pending approval"
                )

            # Add additional approval validations here
            # For example, check if user has approval permissions
            # if not current_user.can_approve_expenses:
            #     raise HTTPException(
            #         status_code=403,
            #         detail="User does not have approval permissions"
            #     )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating expense approval: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error validating expense approval"
            )

    def _validate_recurring_data(self, expense_data: schemas.ExpenseCreate | schemas.ExpenseUpdate) -> None:
        """Validate recurring expense specific data."""
        if not expense_data.recurrence_interval:
            raise HTTPException(
                status_code=400,
                detail="Recurrence interval is required for recurring expenses"
            )

        if not expense_data.recurrence_end_date:
            raise HTTPException(
                status_code=400,
                detail="Recurrence end date is required for recurring expenses"
            )

        if expense_data.recurrence_end_date <= date.today():
            raise HTTPException(
                status_code=400,
                detail="Recurrence end date must be in the future"
            )

expense_validator = ExpenseValidator()
