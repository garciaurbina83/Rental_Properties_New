from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import (
    Loan, LoanPayment, 
    LoanStatus, PaymentStatus,
    PaymentMethod
)
from app.schemas.loan import LoanPaymentCreate
from app.core.exceptions import NotFoundException, ValidationError
from app.services.audit_service import audit_service
from app.services.notification_service import NotificationService
from app.services.late_fee_service import LateFeeService

class LoanPaymentService:
    @staticmethod
    async def create_payment(
        db: Session,
        loan_id: int,
        payment_data: LoanPaymentCreate,
        user_id: int
    ) -> LoanPayment:
        """Registrar un nuevo pago de préstamo"""
        loan = await db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise NotFoundException(f"Préstamo {loan_id} no encontrado")

        # Validar que el préstamo esté activo
        if loan.status not in [LoanStatus.ACTIVE, LoanStatus.DEFAULT]:
            raise ValidationError(f"No se pueden registrar pagos para préstamos en estado {loan.status}")

        # Calcular montos de principal e interés
        monthly_rate = loan.interest_rate / 12 / 100
        interest_amount = loan.remaining_balance * monthly_rate
        principal_amount = payment_data.amount - interest_amount - payment_data.late_fee

        # Validar que el pago sea suficiente para cubrir al menos los intereses
        if payment_data.amount < interest_amount:
            raise ValidationError("El pago debe cubrir al menos los intereses del mes")

        payment = LoanPayment(
            loan_id=loan_id,
            payment_date=payment_data.payment_date,
            due_date=payment_data.due_date,
            amount=payment_data.amount,
            principal_amount=principal_amount,
            interest_amount=interest_amount,
            late_fee=payment_data.late_fee,
            payment_method=payment_data.payment_method,
            reference_number=payment_data.reference_number,
            status=PaymentStatus.PENDING,
            notes=payment_data.notes,
            processed_by=user_id,
            processed_at=datetime.utcnow()
        )

        db.add(payment)
        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db,
            "loan_payment",
            payment.id,
            "created",
            None,
            payment.dict(),
            user_id
        )

        return payment

    @staticmethod
    async def process_payment(
        db: Session,
        payment_id: int,
        user_id: int
    ) -> LoanPayment:
        """Procesar un pago pendiente"""
        payment = await db.query(LoanPayment).filter(
            LoanPayment.id == payment_id
        ).first()

        if not payment:
            raise NotFoundException(f"Pago {payment_id} no encontrado")

        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.LATE]:
            raise ValidationError(f"El pago ya ha sido procesado: {payment.status}")

        loan = await db.query(Loan).filter(Loan.id == payment.loan_id).first()
        
        old_payment_data = payment.dict()
        old_loan_data = loan.dict()

        # Calcular multa por pago tardío si aplica
        if payment.status == PaymentStatus.PENDING and date.today() > payment.due_date:
            payment = await LateFeeService.apply_late_fee(db, payment, user_id)

        # Actualizar el pago
        payment.status = PaymentStatus.COMPLETED
        payment.processed_by = user_id
        payment.processed_at = datetime.utcnow()

        # Actualizar el préstamo
        loan.remaining_balance -= payment.principal_amount
        loan.last_payment_date = payment.payment_date
        
        # Calcular próxima fecha de pago
        next_payment_date = payment.due_date + timedelta(days=30)
        loan.next_payment_date = next_payment_date

        # Actualizar estado del préstamo si está pagado
        if loan.remaining_balance <= 0:
            loan.status = LoanStatus.PAID
            loan.remaining_balance = 0

        await db.flush()

        # Registrar cambios en auditoría
        await audit_service(
            db,
            "loan_payment",
            payment.id,
            "processed",
            old_payment_data,
            payment.dict(),
            user_id
        )

        await audit_service(
            db,
            "loan",
            loan.id,
            "payment_processed",
            old_loan_data,
            loan.dict(),
            user_id
        )

        # Enviar notificación de pago procesado
        await NotificationService.send_loan_payment_notification(
            db,
            loan,
            payment,
            "payment_processed"
        )

        return payment

    @staticmethod
    async def get_loan_payments(
        db: Session,
        loan_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PaymentStatus] = None
    ) -> List[LoanPayment]:
        """Obtener pagos de un préstamo con filtros opcionales"""
        query = db.query(LoanPayment).filter(LoanPayment.loan_id == loan_id)
        
        if status:
            query = query.filter(LoanPayment.status == status)
            
        return await query.order_by(LoanPayment.due_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    async def get_pending_payments(
        db: Session,
        days_ahead: int = 30
    ) -> List[LoanPayment]:
        """Obtener pagos pendientes para los próximos días"""
        future_date = date.today() + timedelta(days=days_ahead)
        
        return await db.query(LoanPayment).filter(
            and_(
                LoanPayment.status == PaymentStatus.PENDING,
                LoanPayment.due_date <= future_date
            )
        ).order_by(LoanPayment.due_date).all()

    @staticmethod
    async def cancel_payment(
        db: Session,
        payment_id: int,
        user_id: int,
        cancellation_reason: str
    ) -> LoanPayment:
        """Cancelar un pago pendiente"""
        payment = await db.query(LoanPayment).filter(
            LoanPayment.id == payment_id
        ).first()

        if not payment:
            raise NotFoundException(f"Pago {payment_id} no encontrado")

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(f"Solo se pueden cancelar pagos pendientes")

        old_data = payment.dict()

        payment.status = PaymentStatus.CANCELLED
        payment.notes = f"{payment.notes}\nCancelado: {cancellation_reason}"
        payment.processed_by = user_id
        payment.processed_at = datetime.utcnow()

        await db.flush()

        # Registrar en auditoría
        await audit_service(
            db,
            "loan_payment",
            payment.id,
            "cancelled",
            old_data,
            payment.dict(),
            user_id
        )

        return payment
