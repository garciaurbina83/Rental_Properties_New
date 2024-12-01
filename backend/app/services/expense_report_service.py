from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import logging

from app.crud import expense as crud_expense
from app.crud import property as crud_property
from app.crud import vendor as crud_vendor
from app.crud import expense_category as crud_expense_category
from app.models.expense import Expense
from app.models.property import Property
from app.models.vendor import Vendor
from app.models.expense_category import ExpenseCategory

logger = logging.getLogger(__name__)

class ExpenseReportService:
    async def generate_summary_report(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        property_id: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a summary report of expenses."""
        try:
            query = db.query(Expense)
            
            # Apply filters
            query = query.filter(Expense.date.between(start_date, end_date))
            if property_id:
                query = query.filter(Expense.property_id == property_id)
            if category_id:
                query = query.filter(Expense.category_id == category_id)

            # Calculate summary statistics
            total_amount = query.with_entities(func.sum(Expense.amount)).scalar() or 0
            total_count = query.count()
            avg_amount = total_amount / total_count if total_count > 0 else 0

            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_amount": float(total_amount),
                    "total_count": total_count,
                    "average_amount": float(avg_amount)
                }
            }
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            raise

    async def generate_trend_report(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        group_by: str = "month"
    ) -> List[Dict[str, Any]]:
        """Generate a trend report showing expense patterns over time."""
        try:
            query = db.query(
                func.date_trunc(group_by, Expense.date).label('period'),
                func.sum(Expense.amount).label('total_amount'),
                func.count(Expense.id).label('count')
            ).filter(
                Expense.date.between(start_date, end_date)
            ).group_by(
                func.date_trunc(group_by, Expense.date)
            ).order_by('period')

            return [
                {
                    "period": row.period.strftime("%Y-%m-%d"),
                    "total_amount": float(row.total_amount),
                    "count": row.count
                }
                for row in query.all()
            ]
        except Exception as e:
            logger.error(f"Error generating trend report: {str(e)}")
            raise

    async def generate_category_distribution(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate a report showing expense distribution by category."""
        try:
            query = db.query(
                ExpenseCategory.name.label('category'),
                func.sum(Expense.amount).label('total_amount'),
                func.count(Expense.id).label('count')
            ).join(
                Expense, Expense.category_id == ExpenseCategory.id
            ).filter(
                Expense.date.between(start_date, end_date)
            ).group_by(
                ExpenseCategory.name
            )

            return [
                {
                    "category": row.category,
                    "total_amount": float(row.total_amount),
                    "count": row.count
                }
                for row in query.all()
            ]
        except Exception as e:
            logger.error(f"Error generating category distribution: {str(e)}")
            raise

    async def generate_property_comparison(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate a report comparing expenses across properties."""
        try:
            query = db.query(
                Property.name.label('property'),
                func.sum(Expense.amount).label('total_amount'),
                func.count(Expense.id).label('count'),
                func.avg(Expense.amount).label('avg_amount')
            ).join(
                Expense, Expense.property_id == Property.id
            ).filter(
                Expense.date.between(start_date, end_date)
            ).group_by(
                Property.name
            )

            return [
                {
                    "property": row.property,
                    "total_amount": float(row.total_amount),
                    "count": row.count,
                    "average_amount": float(row.avg_amount)
                }
                for row in query.all()
            ]
        except Exception as e:
            logger.error(f"Error generating property comparison: {str(e)}")
            raise

    async def export_to_excel(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        file_path: str
    ) -> str:
        """Export expense data to Excel file."""
        try:
            # Get expense data
            expenses = db.query(
                Expense.date,
                Expense.description,
                Expense.amount,
                Property.name.label('property'),
                Vendor.name.label('vendor'),
                ExpenseCategory.name.label('category')
            ).join(
                Property, Expense.property_id == Property.id, isouter=True
            ).join(
                Vendor, Expense.vendor_id == Vendor.id, isouter=True
            ).join(
                ExpenseCategory, Expense.category_id == ExpenseCategory.id, isouter=True
            ).filter(
                Expense.date.between(start_date, end_date)
            ).all()

            # Convert to DataFrame
            df = pd.DataFrame(expenses)
            
            # Add summary row
            summary = pd.DataFrame({
                'date': ['Total'],
                'description': [''],
                'amount': [df['amount'].sum()],
                'property': [''],
                'vendor': [''],
                'category': ['']
            })
            df = pd.concat([df, summary])

            # Save to Excel
            df.to_excel(file_path, index=False, sheet_name='Expenses')
            return file_path

        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            raise

expense_report_service = ExpenseReportService()
