from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Loan, LoanPayment, PaymentStatus
from app.core.exceptions import ValidationError

class LateFeeService:
    @staticmethod
    async def calculate_late_fee(
        db: Session,
        payment: LoanPayment,
        calculation_date: Optional[date] = None
    ) -> float:
        """Calcular la multa por pago tardío"""
        if not calculation_date:
            calculation_date = date.today()

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError("Solo se pueden calcular multas para pagos pendientes")

        if calculation_date <= payment.due_date:
            return 0.0

        loan = await db.query(Loan).filter(Loan.id == payment.loan_id).first()
        if not loan:
            raise ValidationError("Préstamo no encontrado")

        days_late = (calculation_date - payment.due_date).days
        
        # Configuración de multas (podría moverse a configuración global)
        LATE_FEE_PERCENTAGE = 0.05  # 5% del monto del pago
        DAILY_INTEREST_RATE = 0.001  # 0.1% diario después de 5 días
        GRACE_PERIOD_DAYS = 5
        MAX_LATE_FEE_PERCENTAGE = 0.30  # Máximo 30% del pago

        # Calcular multa base
        base_late_fee = payment.amount * LATE_FEE_PERCENTAGE

        # Agregar interés diario después del período de gracia
        if days_late > GRACE_PERIOD_DAYS:
            extra_days = days_late - GRACE_PERIOD_DAYS
            daily_interest = payment.amount * DAILY_INTEREST_RATE * extra_days
            total_late_fee = base_late_fee + daily_interest
        else:
            total_late_fee = base_late_fee

        # Aplicar límite máximo
        max_late_fee = payment.amount * MAX_LATE_FEE_PERCENTAGE
        return min(total_late_fee, max_late_fee)

    @staticmethod
    async def apply_late_fee(
        db: Session,
        payment: LoanPayment,
        user_id: int
    ) -> LoanPayment:
        """Aplicar multa por pago tardío a un pago"""
        late_fee = await LateFeeService.calculate_late_fee(db, payment)
        
        if late_fee > 0:
            old_data = payment.dict()
            payment.late_fee = late_fee
            payment.status = PaymentStatus.LATE
            
            # Registrar el cambio en la auditoría
            from app.services.audit_service import audit_service
            await audit_service(
                db,
                "loan_payment",
                payment.id,
                "late_fee_applied",
                old_data,
                payment.dict(),
                user_id
            )

            await db.flush()
        
        return payment

    @staticmethod
    async def update_late_payments(
        db: Session,
        user_id: int
    ) -> int:
        """Actualizar multas para todos los pagos atrasados"""
        today = date.today()
        pending_payments = await db.query(LoanPayment).filter(
            LoanPayment.status == PaymentStatus.PENDING,
            LoanPayment.due_date < today
        ).all()

        updated_count = 0
        for payment in pending_payments:
            await LateFeeService.apply_late_fee(db, payment, user_id)
            updated_count += 1

        return updated_count
