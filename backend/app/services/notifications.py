from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
import json
import logging

from ..core.config import settings
from ..crud import payment as crud_payment
from ..crud import contract as crud_contract
from ..models.payment import PaymentStatus

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración de correo
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    TEMPLATE_FOLDER=Path(__file__).parent / "../templates"
)

fastmail = FastMail(conf)

class NotificationService:
    @staticmethod
    async def send_email_notification(
        email_to: str,
        subject: str,
        template_name: str,
        template_data: dict
    ):
        """Enviar notificación por correo usando una plantilla"""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[email_to],
                template_body=template_data,
                subtype="html"
            )
            
            await fastmail.send_message(
                message,
                template_name=template_name
            )
            logger.info(f"Email notification sent to {email_to}")
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    @staticmethod
    async def send_payment_reminder(
        db: Session,
        payment_id: int,
        reminder_type: str
    ):
        """Enviar recordatorio de pago"""
        payment = crud_payment.get(db, id=payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found for reminder")
            return
        
        contract = crud_contract.get(db, id=payment.contract_id)
        if not contract:
            logger.error(f"Contract {payment.contract_id} not found for payment reminder")
            return
        
        template_data = {
            "tenant_name": contract.tenant.full_name,
            "amount": payment.amount,
            "due_date": payment.due_date.strftime("%Y-%m-%d"),
            "contract_number": contract.contract_number,
            "payment_concept": payment.concept.value
        }
        
        subject = {
            "upcoming": "Recordatorio: Próximo pago de renta",
            "due": "Recordatorio: Pago de renta vence hoy",
            "overdue": "Alerta: Pago de renta vencido"
        }.get(reminder_type, "Recordatorio de pago")
        
        template_name = f"payment_reminder_{reminder_type}.html"
        
        await NotificationService.send_email_notification(
            email_to=contract.tenant.email,
            subject=subject,
            template_name=template_name,
            template_data=template_data
        )

    @staticmethod
    async def send_payment_confirmation(
        db: Session,
        payment_id: int
    ):
        """Enviar confirmación de pago recibido"""
        payment = crud_payment.get(db, id=payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found for confirmation")
            return
        
        contract = crud_contract.get(db, id=payment.contract_id)
        if not contract:
            logger.error(f"Contract {payment.contract_id} not found for payment confirmation")
            return
        
        template_data = {
            "tenant_name": contract.tenant.full_name,
            "amount": payment.amount,
            "payment_date": payment.payment_date.strftime("%Y-%m-%d"),
            "contract_number": contract.contract_number,
            "payment_concept": payment.concept.value,
            "payment_method": payment.payment_method.value,
            "reference_number": payment.reference_number
        }
        
        await NotificationService.send_email_notification(
            email_to=contract.tenant.email,
            subject="Confirmación de pago recibido",
            template_name="payment_confirmation.html",
            template_data=template_data
        )

    @staticmethod
    async def send_late_payment_alert(
        db: Session,
        payment_id: int
    ):
        """Enviar alerta de pago atrasado"""
        payment = crud_payment.get(db, id=payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found for late payment alert")
            return
        
        contract = crud_contract.get(db, id=payment.contract_id)
        if not contract:
            logger.error(f"Contract {payment.contract_id} not found for late payment alert")
            return
        
        days_late = (date.today() - payment.due_date).days
        template_data = {
            "tenant_name": contract.tenant.full_name,
            "amount": payment.amount,
            "due_date": payment.due_date.strftime("%Y-%m-%d"),
            "days_late": days_late,
            "contract_number": contract.contract_number,
            "late_fee": payment.late_fee
        }
        
        await NotificationService.send_email_notification(
            email_to=contract.tenant.email,
            subject="Alerta: Pago atrasado",
            template_name="late_payment_alert.html",
            template_data=template_data
        )

def schedule_payment_reminders(
    db: Session,
    background_tasks: BackgroundTasks
):
    """Programar recordatorios de pago"""
    today = date.today()
    upcoming_date = today + timedelta(days=7)
    
    # Recordatorios de pagos próximos (7 días antes)
    upcoming_payments = crud_payment.get_multi(
        db,
        filters={
            "status": PaymentStatus.PENDING,
            "due_date": upcoming_date
        }
    )
    
    for payment in upcoming_payments:
        background_tasks.add_task(
            NotificationService.send_payment_reminder,
            db,
            payment.id,
            "upcoming"
        )
    
    # Recordatorios de pagos que vencen hoy
    due_payments = crud_payment.get_multi(
        db,
        filters={
            "status": PaymentStatus.PENDING,
            "due_date": today
        }
    )
    
    for payment in due_payments:
        background_tasks.add_task(
            NotificationService.send_payment_reminder,
            db,
            payment.id,
            "due"
        )
    
    # Alertas de pagos vencidos
    overdue_payments = crud_payment.get_multi(
        db,
        filters={
            "status": PaymentStatus.LATE,
            "due_date__lt": today
        }
    )
    
    for payment in overdue_payments:
        background_tasks.add_task(
            NotificationService.send_late_payment_alert,
            db,
            payment.id
        )
