from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, between
from datetime import date
from sqlalchemy import func, case
from app.crud.base import CRUDBase
from app.models.expense import Expense, ExpenseAttachment
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseSummary, ExpenseCategorySummary, PropertyExpenseSummary, VendorExpenseSummary, RecurringExpenseSummary
from app.models.property import Property
from app.models.vendor import Vendor
from app.utils import save_upload_file
from fastapi import UploadFile
from app.models.expense_category import ExpenseCategory

class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    def create_with_owner(
        self,
        db: Session,
        *,
        obj_in: ExpenseCreate,
        owner_id: int
    ) -> Expense:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, created_by=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Expense]:
        query = db.query(self.model)
        
        if filters:
            # Filtros básicos
            basic_filters = [
                "property_id", "vendor_id", "expense_type",
                "status", "is_recurring", "requires_approval"
            ]
            for field in basic_filters:
                value = filters.get(field)
                if value is not None:
                    query = query.filter(getattr(self.model, field) == value)
            
            # Filtro por rango de fechas
            start_date = filters.get("start_date")
            end_date = filters.get("end_date")
            if start_date and end_date:
                query = query.filter(
                    between(self.model.date_incurred, start_date, end_date)
                )
            elif start_date:
                query = query.filter(self.model.date_incurred >= start_date)
            elif end_date:
                query = query.filter(self.model.date_incurred <= end_date)
        
        return query.offset(skip).limit(limit).all()

    def get_recurring_expenses_to_generate(
        self,
        db: Session,
        *,
        current_date: date
    ) -> List[Expense]:
        """
        Obtiene los gastos recurrentes que necesitan generar nuevas instancias
        basado en su intervalo de recurrencia y fecha final.
        """
        return db.query(self.model).filter(
            and_(
                self.model.is_recurring == True,
                self.model.recurrence_end_date >= current_date
            )
        ).all()

    def create_recurring_instance(
        self,
        db: Session,
        *,
        parent_expense: Expense,
        new_date: date
    ) -> Expense:
        """
        Crea una nueva instancia de un gasto recurrente.
        """
        expense_data = {
            "property_id": parent_expense.property_id,
            "unit_id": parent_expense.unit_id,
            "vendor_id": parent_expense.vendor_id,
            "description": parent_expense.description,
            "amount": parent_expense.amount,
            "expense_type": parent_expense.expense_type,
            "status": "draft",
            "date_incurred": new_date,
            "requires_approval": parent_expense.requires_approval,
            "parent_expense_id": parent_expense.id
        }
        
        db_obj = self.model(**expense_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cancel(self, db: Session, *, expense_id: int, user_id: int) -> Expense:
        expense = self.get(db=db, id=expense_id)
        if expense:
            expense.status = "cancelled"
            expense.updated_by = user_id
            expense.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(expense)
        return expense

    async def add_attachment(
        self,
        db: Session,
        *,
        expense_id: int,
        file: UploadFile,
        uploaded_by: int
    ) -> ExpenseAttachment:
        # Save file to storage
        file_path = f"expenses/{expense_id}/{file.filename}"
        await save_upload_file(file, file_path)
        
        # Create attachment record
        attachment = ExpenseAttachment(
            expense_id=expense_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=file.content_type,
            file_size=len(await file.read()),
            uploaded_by=uploaded_by
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

    def get_attachments(self, db: Session, expense_id: int) -> List[ExpenseAttachment]:
        return db.query(ExpenseAttachment).filter(
            ExpenseAttachment.expense_id == expense_id
        ).all()

    def get_summary(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        property_id: Optional[int] = None
    ) -> ExpenseSummary:
        query = db.query(
            func.sum(Expense.amount).label("total_amount"),
            func.count().label("total_count"),
            func.sum(case(
                (Expense.status == "paid", Expense.amount),
                else_=0
            )).label("paid_amount"),
            func.count(case(
                (Expense.status == "paid", 1),
                else_=None
            )).label("paid_count"),
            func.sum(case(
                (Expense.status == "pending", Expense.amount),
                else_=0
            )).label("pending_amount"),
            func.count(case(
                (Expense.status == "pending", 1),
                else_=None
            )).label("pending_count"),
            func.sum(case(
                (Expense.status == "overdue", Expense.amount),
                else_=0
            )).label("overdue_amount"),
            func.count(case(
                (Expense.status == "overdue", 1),
                else_=None
            )).label("overdue_count"),
            func.avg(
                func.extract('epoch', Expense.payment_date - Expense.date_incurred) / 86400
            ).label("average_processing_time")
        ).filter(
            between(Expense.date_incurred, start_date, end_date)
        )

        if property_id:
            query = query.filter(Expense.property_id == property_id)

        result = query.first()
        return ExpenseSummary(
            total_amount=result.total_amount or 0,
            paid_amount=result.paid_amount or 0,
            pending_amount=result.pending_amount or 0,
            overdue_amount=result.overdue_amount or 0,
            total_count=result.total_count or 0,
            paid_count=result.paid_count or 0,
            pending_count=result.pending_count or 0,
            overdue_count=result.overdue_count or 0,
            average_processing_time=result.average_processing_time
        )

    def get_by_category(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        property_id: Optional[int] = None
    ) -> List[ExpenseCategorySummary]:
        query = db.query(
            Expense.expense_type,
            func.sum(Expense.amount).label("total_amount"),
            func.count().label("count")
        ).filter(
            between(Expense.date_incurred, start_date, end_date)
        ).group_by(
            Expense.expense_type
        )

        if property_id:
            query = query.filter(Expense.property_id == property_id)

        results = query.all()
        total_amount = sum(r.total_amount for r in results)

        return [
            ExpenseCategorySummary(
                category=r.expense_type,
                total_amount=r.total_amount,
                count=r.count,
                percentage_of_total=(r.total_amount / total_amount * 100 if total_amount > 0 else 0)
            )
            for r in results
        ]

    def get_by_property(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date
    ) -> List[PropertyExpenseSummary]:
        query = db.query(
            Property.id,
            Property.name,
            func.sum(Expense.amount).label("total_amount"),
            func.count().label("count")
        ).join(
            Expense,
            Property.id == Expense.property_id
        ).filter(
            between(Expense.date_incurred, start_date, end_date)
        ).group_by(
            Property.id,
            Property.name
        )

        results = query.all()
        summaries = []

        for r in results:
            categories = self.get_by_category(
                db=db,
                start_date=start_date,
                end_date=end_date,
                property_id=r.id
            )
            summaries.append(
                PropertyExpenseSummary(
                    property_id=r.id,
                    property_name=r.name,
                    total_amount=r.total_amount,
                    count=r.count,
                    categories=categories
                )
            )

        return summaries

    def get_by_vendor(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        property_id: Optional[int] = None
    ) -> List[VendorExpenseSummary]:
        query = db.query(
            Vendor.id,
            Vendor.name,
            func.sum(Expense.amount).label("total_amount"),
            func.count().label("count"),
            func.avg(Expense.amount).label("average_amount")
        ).join(
            Expense,
            Vendor.id == Expense.vendor_id
        ).filter(
            between(Expense.date_incurred, start_date, end_date)
        )

        if property_id:
            query = query.filter(Expense.property_id == property_id)

        query = query.group_by(
            Vendor.id,
            Vendor.name
        )

        results = query.all()
        summaries = []

        for r in results:
            categories = self.get_by_category(
                db=db,
                start_date=start_date,
                end_date=end_date,
                property_id=property_id
            )
            summaries.append(
                VendorExpenseSummary(
                    vendor_id=r.id,
                    vendor_name=r.name,
                    total_amount=r.total_amount,
                    count=r.count,
                    average_amount=r.average_amount,
                    categories=categories
                )
            )

        return summaries

    def get_recurring(
        self,
        db: Session,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        property_id: Optional[int] = None
    ) -> List[RecurringExpenseSummary]:
        query = db.query(Expense).filter(
            Expense.is_recurring == True
        )

        if start_date and end_date:
            query = query.filter(
                or_(
                    between(Expense.date_incurred, start_date, end_date),
                    Expense.next_due_date.between(start_date, end_date)
                )
            )

        if property_id:
            query = query.filter(Expense.property_id == property_id)

        expenses = query.all()
        return [
            RecurringExpenseSummary(
                expense_id=e.id,
                description=e.description,
                amount=e.amount,
                expense_type=e.expense_type,
                recurrence_interval=e.recurrence_interval,
                next_due_date=e.next_due_date,
                property_id=e.property_id,
                unit_id=e.unit_id,
                vendor_id=e.vendor_id
            )
            for e in expenses
        ]

    def get_by_vendor_id(
        self,
        db: Session,
        *,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> List[Expense]:
        query = db.query(self.model).filter(self.model.vendor_id == vendor_id)

        if start_date and end_date:
            query = query.filter(between(self.model.date_incurred, start_date, end_date))

        if status:
            query = query.filter(self.model.status == status)

        if created_by:
            query = query.filter(self.model.created_by == created_by)

        return query.offset(skip).limit(limit).all()

    def get_by_category(
        self,
        db: Session,
        *,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        return db.query(Expense)\
            .filter(Expense.category_id == category_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_category_summary(
        self,
        db: Session,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        query = db.query(
            ExpenseCategory.name.label("category"),
            func.count(Expense.id).label("count"),
            func.sum(Expense.amount).label("total_amount")
        )\
        .join(Expense, ExpenseCategory.id == Expense.category_id)\
        .group_by(ExpenseCategory.name)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        return [
            {
                "category": row.category,
                "count": row.count,
                "total_amount": float(row.total_amount) if row.total_amount else 0.0
            }
            for row in query.all()
        ]

expense = CRUDExpense(Expense)
