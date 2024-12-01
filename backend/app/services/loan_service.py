from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import (
    Loan, LoanDocument, LoanPayment, 
    LoanStatus, PaymentStatus
)
from app.schemas.loan import (
    LoanCreate, LoanUpdate, 
    LoanDocumentCreate,
    LoanSummary
)
from app.core.exceptions import NotFoundException, ValidationError
from app.services.audit_service import audit_service

class LoanService:
    @staticmethod
    async def create_loan(db: Session, loan_data: LoanCreate, user_id: int) -> Loan:
        """Crear un nuevo préstamo"""
        # Calcular fecha de fin basada en el plazo
        end_date = loan_data.start_date + timedelta(days=30 * loan_data.term_months)
        
        # Calcular pago mensual (fórmula de amortización)
        r = loan_data.interest_rate / 12 / 100  # Tasa mensual
        n = loan_data.term_months  # Número de pagos
        p = loan_data.principal_amount  # Monto principal
        monthly_payment = p * (r * (1 + r)**n) / ((1 + r)**n - 1)

        loan = Loan(
            property_id=loan_data.property_id,
            loan_type=loan_data.loan_type,
            principal_amount=loan_data.principal_amount,
            interest_rate=loan_data.interest_rate,
            term_months=loan_data.term_months,
            start_date=loan_data.start_date,
            end_date=end_date,
            payment_day=loan_data.payment_day,
            status=LoanStatus.PENDING,
            remaining_balance=loan_data.principal_amount,
            monthly_payment=monthly_payment,
            lender_name=loan_data.lender_name,
            lender_contact=loan_data.lender_contact,
            loan_number=loan_data.loan_number,
            notes=loan_data.notes
        )

        db.add(loan)
        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db, 
            "loan", 
            loan.id, 
            "created", 
            None, 
            loan.dict(),
            user_id
        )

        return loan

    @staticmethod
    async def get_loan(db: Session, loan_id: int) -> Optional[Loan]:
        """Obtener un préstamo por ID"""
        return await db.query(Loan).filter(Loan.id == loan_id).first()

    @staticmethod
    async def get_loans(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        property_id: Optional[int] = None,
        status: Optional[LoanStatus] = None
    ) -> List[Loan]:
        """Obtener lista de préstamos con filtros opcionales"""
        query = db.query(Loan)
        
        if property_id:
            query = query.filter(Loan.property_id == property_id)
        if status:
            query = query.filter(Loan.status == status)
            
        return await query.offset(skip).limit(limit).all()

    @staticmethod
    async def update_loan(
        db: Session, 
        loan_id: int, 
        loan_data: LoanUpdate,
        user_id: int
    ) -> Loan:
        """Actualizar un préstamo"""
        loan = await LoanService.get_loan(db, loan_id)
        if not loan:
            raise NotFoundException(f"Préstamo {loan_id} no encontrado")

        old_data = loan.dict()
        
        # Actualizar campos permitidos
        for field, value in loan_data.dict(exclude_unset=True).items():
            setattr(loan, field, value)

        # Si se modifica la tasa de interés o el plazo, recalcular pagos
        if "interest_rate" in loan_data.dict() or "term_months" in loan_data.dict():
            r = loan.interest_rate / 12 / 100
            n = loan.term_months
            p = loan.remaining_balance
            loan.monthly_payment = p * (r * (1 + r)**n) / ((1 + r)**n - 1)

        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db,
            "loan",
            loan.id,
            "updated",
            old_data,
            loan.dict(),
            user_id
        )

        return loan

    @staticmethod
    async def add_document(
        db: Session,
        loan_id: int,
        document_data: LoanDocumentCreate,
        user_id: int
    ) -> LoanDocument:
        """Añadir un documento al préstamo"""
        loan = await LoanService.get_loan(db, loan_id)
        if not loan:
            raise NotFoundException(f"Préstamo {loan_id} no encontrado")

        document = LoanDocument(
            loan_id=loan_id,
            document_type=document_data.document_type,
            file_path=document_data.file_path,
            upload_date=date.today(),
            description=document_data.description
        )

        db.add(document)
        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db,
            "loan_document",
            document.id,
            "created",
            None,
            document.dict(),
            user_id
        )

        return document

    @staticmethod
    async def verify_document(
        db: Session,
        document_id: int,
        user_id: int
    ) -> LoanDocument:
        """Verificar un documento de préstamo"""
        document = await db.query(LoanDocument).filter(
            LoanDocument.id == document_id
        ).first()

        if not document:
            raise NotFoundException(f"Documento {document_id} no encontrado")

        old_data = document.dict()
        
        document.is_verified = True
        document.verified_by = user_id
        document.verified_at = datetime.utcnow()

        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db,
            "loan_document",
            document.id,
            "verified",
            old_data,
            document.dict(),
            user_id
        )

        return document

    @staticmethod
    async def get_loan_summary(db: Session, loan_id: int) -> LoanSummary:
        """Obtener resumen del préstamo con información de pagos"""
        loan = await LoanService.get_loan(db, loan_id)
        if not loan:
            raise NotFoundException(f"Préstamo {loan_id} no encontrado")

        # Obtener pagos completados
        completed_payments = await db.query(LoanPayment).filter(
            and_(
                LoanPayment.loan_id == loan_id,
                LoanPayment.status == PaymentStatus.COMPLETED
            )
        ).all()

        # Calcular totales
        total_paid = sum(payment.amount for payment in completed_payments)
        total_principal_paid = sum(payment.principal_amount for payment in completed_payments)
        total_interest_paid = sum(payment.interest_amount for payment in completed_payments)
        total_late_fees = sum(payment.late_fee for payment in completed_payments)

        # Calcular próximo pago
        next_payment = await db.query(LoanPayment).filter(
            and_(
                LoanPayment.loan_id == loan_id,
                LoanPayment.status == PaymentStatus.PENDING,
                LoanPayment.due_date >= date.today()
            )
        ).order_by(LoanPayment.due_date).first()

        return LoanSummary(
            loan_id=loan_id,
            total_amount=loan.principal_amount,
            remaining_balance=loan.remaining_balance,
            total_paid=total_paid,
            total_principal_paid=total_principal_paid,
            total_interest_paid=total_interest_paid,
            total_late_fees=total_late_fees,
            monthly_payment=loan.monthly_payment,
            next_payment_date=next_payment.due_date if next_payment else None,
            next_payment_amount=next_payment.amount if next_payment else None,
            status=loan.status,
            payments_made=len(completed_payments),
            remaining_payments=loan.term_months - len(completed_payments)
        )

    @staticmethod
    async def generate_amortization_schedule(
        db: Session,
        loan_id: int
    ) -> List[Dict]:
        """Generar tabla de amortización del préstamo"""
        loan = await LoanService.get_loan(db, loan_id)
        if not loan:
            raise NotFoundException(f"Préstamo {loan_id} no encontrado")

        schedule = []
        remaining_balance = loan.principal_amount
        monthly_rate = loan.interest_rate / 12 / 100
        payment_amount = loan.monthly_payment

        for month in range(1, loan.term_months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = payment_amount - interest_payment
            remaining_balance -= principal_payment

            payment_date = loan.start_date + timedelta(days=30 * month)
            
            schedule.append({
                "payment_number": month,
                "payment_date": payment_date,
                "payment_amount": payment_amount,
                "principal_payment": principal_payment,
                "interest_payment": interest_payment,
                "remaining_balance": max(0, remaining_balance)
            })

        return schedule
