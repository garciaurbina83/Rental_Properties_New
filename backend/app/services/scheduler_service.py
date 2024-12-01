from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models import Loan, LoanPayment, PaymentStatus, LoanStatus
from app.services.late_fee_service import LateFeeService
from app.services.notification_service import NotificationService
from app.services.loan_report_service import LoanReportService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    @staticmethod
    async def schedule_daily_tasks(
        db: Session,
        background_tasks: BackgroundTasks,
        system_user_id: int
    ):
        """Programar tareas diarias"""
        try:
            # Actualizar multas por pagos tardíos
            updated_count = await LateFeeService.update_late_payments(db, system_user_id)
            logger.info(f"Actualizadas {updated_count} multas por pagos tardíos")

            # Enviar recordatorios de pagos próximos (7 días antes)
            await SchedulerService.send_upcoming_payment_reminders(db)

            # Enviar recordatorios de pagos que vencen hoy
            await SchedulerService.send_due_payment_reminders(db)

            # Enviar alertas de pagos vencidos
            await SchedulerService.send_overdue_payment_alerts(db)

        except Exception as e:
            logger.error(f"Error en tareas programadas: {str(e)}")
            raise

    @staticmethod
    async def send_upcoming_payment_reminders(db: Session):
        """Enviar recordatorios de pagos próximos"""
        upcoming_date = date.today() + timedelta(days=7)
        payments = await db.query(LoanPayment).filter(
            LoanPayment.status == PaymentStatus.PENDING,
            LoanPayment.due_date == upcoming_date
        ).all()

        for payment in payments:
            try:
                await NotificationService.send_payment_reminder(
                    db,
                    payment.id,
                    "upcoming"
                )
                logger.info(f"Enviado recordatorio de pago próximo para payment_id={payment.id}")
            except Exception as e:
                logger.error(f"Error enviando recordatorio de pago próximo {payment.id}: {str(e)}")

    @staticmethod
    async def send_due_payment_reminders(db: Session):
        """Enviar recordatorios de pagos que vencen hoy"""
        today = date.today()
        payments = await db.query(LoanPayment).filter(
            LoanPayment.status == PaymentStatus.PENDING,
            LoanPayment.due_date == today
        ).all()

        for payment in payments:
            try:
                await NotificationService.send_payment_reminder(
                    db,
                    payment.id,
                    "due"
                )
                logger.info(f"Enviado recordatorio de pago que vence hoy para payment_id={payment.id}")
            except Exception as e:
                logger.error(f"Error enviando recordatorio de pago que vence hoy {payment.id}: {str(e)}")

    @staticmethod
    async def send_overdue_payment_alerts(db: Session):
        """Enviar alertas de pagos vencidos"""
        today = date.today()
        payments = await db.query(LoanPayment).filter(
            LoanPayment.status == PaymentStatus.LATE,
            LoanPayment.due_date < today
        ).all()

        for payment in payments:
            try:
                days_late = (today - payment.due_date).days
                # Enviar alertas solo en días específicos (1, 3, 7, 15, 30)
                if days_late in [1, 3, 7, 15, 30]:
                    await NotificationService.send_late_payment_alert(
                        db,
                        payment.id
                    )
                    logger.info(f"Enviada alerta de pago vencido para payment_id={payment.id}")
            except Exception as e:
                logger.error(f"Error enviando alerta de pago vencido {payment.id}: {str(e)}")

    @staticmethod
    async def schedule_monthly_tasks(db: Session):
        """Programar tareas mensuales"""
        try:
            # Generar reportes mensuales
            today = date.today()
            report = await LoanReportService.generate_monthly_report(
                db,
                month=today.month,
                year=today.year
            )
            logger.info(f"Reporte mensual generado para {today.month}/{today.year}")

            # Actualizar estados de préstamos
            await SchedulerService.update_loan_statuses(db)

            # Generar métricas de rendimiento para todos los préstamos activos
            loans = await db.query(Loan).filter(
                Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.DEFAULT])
            ).all()
            
            for loan in loans:
                try:
                    metrics = await LoanReportService.generate_loan_performance_metrics(db, loan.id)
                    logger.info(f"Métricas generadas para préstamo {loan.id}")
                except Exception as e:
                    logger.error(f"Error generando métricas para préstamo {loan.id}: {str(e)}")

        except Exception as e:
            logger.error(f"Error en tareas mensuales: {str(e)}")
            raise

    @staticmethod
    async def update_loan_statuses(db: Session):
        """Actualizar estados de préstamos"""
        today = date.today()
        loans = await db.query(Loan).all()

        for loan in loans:
            try:
                # Verificar préstamos vencidos
                if loan.end_date and loan.end_date < today and loan.status not in [LoanStatus.PAID, LoanStatus.DEFAULT]:
                    loan.status = LoanStatus.DEFAULT
                    logger.info(f"Préstamo {loan.id} marcado como vencido")

                # Verificar préstamos pagados
                elif loan.remaining_balance <= 0 and loan.status != LoanStatus.PAID:
                    loan.status = LoanStatus.PAID
                    logger.info(f"Préstamo {loan.id} marcado como pagado")

            except Exception as e:
                logger.error(f"Error actualizando estado del préstamo {loan.id}: {str(e)}")

        await db.commit()
