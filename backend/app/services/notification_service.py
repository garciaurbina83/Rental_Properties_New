from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import NotificationType, NotificationStatus, NotificationPriority
from app.services.notification_manager import notification_manager
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def send_loan_payment_notification(
        db: Session,
        loan: Any,
        payment: Any,
        event_type: str
    ):
        """Enviar notificación relacionada con pagos de préstamos"""
        notification_data = {
            "loan_id": loan.id,
            "payment_id": payment.id,
            "amount": payment.amount,
            "payment_date": payment.payment_date.isoformat()
        }

        if event_type == "payment_processed":
            title = "Pago Procesado"
            message = f"El pago de ${payment.amount} ha sido procesado exitosamente."
            ntype = NotificationType.PAYMENT_RECEIVED
        elif event_type == "payment_due":
            title = "Pago Próximo"
            message = f"Tienes un pago de ${payment.amount} programado para {payment.due_date}."
            ntype = NotificationType.PAYMENT_DUE
        elif event_type == "payment_late":
            title = "Pago Atrasado"
            message = f"El pago de ${payment.amount} está atrasado. Fecha límite: {payment.due_date}."
            ntype = NotificationType.PAYMENT_LATE
        else:
            logger.error(f"Tipo de evento de pago no reconocido: {event_type}")
            return

        # Crear notificación en la base de datos
        notification = await notification_manager.create_notification(
            db=db,
            user_id=loan.borrower_id,  # Asumiendo que el préstamo tiene un borrower_id
            type=ntype,
            title=title,
            message=message,
            data=notification_data,
            priority="high" if event_type == "payment_late" else "normal"
        )

        # Enviar notificación en tiempo real si el usuario está conectado
        await notification_manager.send_notification(
            loan.borrower_id,
            notification.to_dict()
        )

    @staticmethod
    async def send_loan_status_notification(
        db: Session,
        loan: Any,
        status: str,
        user_id: int
    ):
        """Enviar notificación de cambio de estado de préstamo"""
        notification_data = {
            "loan_id": loan.id,
            "old_status": loan.status,
            "new_status": status
        }

        notification = await notification_manager.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.LOAN_STATUS,
            title="Estado de Préstamo Actualizado",
            message=f"El estado del préstamo #{loan.id} ha cambiado a {status}.",
            data=notification_data
        )

        await notification_manager.send_notification(
            user_id,
            notification.to_dict()
        )

    @staticmethod
    async def send_system_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ):
        """Enviar notificación del sistema"""
        notification = await notification_manager.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.SYSTEM,
            title=title,
            message=message,
            data=data,
            priority=priority
        )

        await notification_manager.send_notification(
            user_id,
            notification.to_dict()
        )

    @staticmethod
    async def send_maintenance_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        maintenance_data: Dict[str, Any],
        priority: str = "normal"
    ):
        """Enviar notificación de mantenimiento"""
        notification = await notification_manager.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.MAINTENANCE,
            title=title,
            message=message,
            data=maintenance_data,
            priority=priority
        )

        await notification_manager.send_notification(
            user_id,
            notification.to_dict()
        )

    @staticmethod
    async def send_contract_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        contract_data: Dict[str, Any],
        priority: str = "normal"
    ):
        """Enviar notificación relacionada con contratos"""
        notification = await notification_manager.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.CONTRACT,
            title=title,
            message=message,
            data=contract_data,
            priority=priority
        )

        await notification_manager.send_notification(
            user_id,
            notification.to_dict()
        )

    async def send_notification(
        self,
        db: Session,
        notification: Notification,
        background_tasks: BackgroundTasks
    ) -> bool:
        """
        Send a notification through all configured channels.
        """
        try:
            # Get user preferences from cache or database
            preferences = await notification_cache.get_user_preferences(notification.user_id)
            if not preferences:
                preferences = await notification_crud.get_user_preferences(db, notification.user_id)
                await notification_cache.set_user_preferences(notification.user_id, preferences)

            channels = self._get_enabled_channels(notification.type, preferences)
            
            for channel in channels:
                background_tasks.add_task(
                    self._send_through_channel,
                    db,
                    notification,
                    channel
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    async def _send_through_channel(
        self,
        db: Session,
        notification: Notification,
        channel: NotificationChannel
    ):
        """
        Send notification through a specific channel.
        """
        try:
            if channel == NotificationChannel.EMAIL:
                await email_manager.send_notification(notification)
            elif channel == NotificationChannel.PUSH:
                await push_manager.send_notification(notification)
            elif channel == NotificationChannel.SMS:
                await sms_manager.send_notification(notification)

            await notification_crud.update_notification_status(
                db,
                notification.id,
                channel,
                NotificationStatus.SENT
            )
        except Exception as e:
            logger.error(f"Failed to send {channel} notification: {str(e)}")
            await notification_crud.update_notification_status(
                db,
                notification.id,
                channel,
                NotificationStatus.FAILED
            )

    def _get_enabled_channels(
        self,
        notification_type: NotificationType,
        preferences: dict
    ) -> List[NotificationChannel]:
        """
        Get enabled notification channels based on user preferences.
        """
        channels = []
        type_preferences = preferences.get(notification_type.value, {})
        
        for channel in NotificationChannel:
            if type_preferences.get(channel.value, True):  # Default to True if not set
                channels.append(channel)
        
        return channels

    async def send_reminder_notifications(
        self,
        db: Session,
        current_time
    ):
        """
        Send reminder notifications for pending items.
        """
        try:
            pending_notifications = await notification_crud.get_pending_reminders(db, current_time)
            
            for notification in pending_notifications:
                await self.send_notification(db, notification, BackgroundTasks())
        except Exception as e:
            logger.error(f"Failed to send reminder notifications: {str(e)}")

    async def notify_expense_created(
        self,
        db: Session,
        expense: Expense,
        created_by: User
    ):
        """Send notification when expense is created."""
        # Notify approvers
        approvers = self._get_expense_approvers(db, expense)
        for approver in approvers:
            notification = Notification(
                user_id=approver.id,
                type=NotificationType.EXPENSE_CREATED,
                title="New Expense Requires Approval",
                message=f"A new expense of ${expense.amount:.2f} requires your approval.",
                priority=NotificationPriority.HIGH,
                reference_id=expense.id,
                reference_type="expense",
                data={
                    "expense_id": expense.id,
                    "amount": expense.amount,
                    "category": expense.category,
                    "created_by": created_by.full_name
                }
            )
            await self.send_notification(db, notification, BackgroundTasks())

    async def notify_expense_updated(
        self,
        db: Session,
        expense: Expense,
        updated_by: User
    ):
        """Send notification when expense is updated."""
        # Notify owner and approvers
        recipients = self._get_expense_stakeholders(db, expense)
        for recipient in recipients:
            if recipient.id != updated_by.id:
                notification = Notification(
                    user_id=recipient.id,
                    type=NotificationType.EXPENSE_UPDATED,
                    title="Expense Updated",
                    message=f"An expense of ${expense.amount:.2f} has been updated.",
                    reference_id=expense.id,
                    reference_type="expense",
                    data={
                        "expense_id": expense.id,
                        "amount": expense.amount,
                        "category": expense.category,
                        "updated_by": updated_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    async def notify_expense_approved(
        self,
        db: Session,
        expense: Expense,
        approved_by: User
    ):
        """Send notification when expense is approved."""
        notification = Notification(
            user_id=expense.created_by,
            type=NotificationType.EXPENSE_APPROVED,
            title="Expense Approved",
            message=f"Your expense of ${expense.amount:.2f} has been approved.",
            reference_id=expense.id,
            reference_type="expense",
            data={
                "expense_id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "approved_by": approved_by.full_name
            }
        )
        await self.send_notification(db, notification, BackgroundTasks())

    async def notify_expense_cancelled(
        self,
        db: Session,
        expense: Expense,
        cancelled_by: User
    ):
        """Send notification when expense is cancelled."""
        # Notify all stakeholders
        recipients = self._get_expense_stakeholders(db, expense)
        for recipient in recipients:
            if recipient.id != cancelled_by.id:
                notification = Notification(
                    user_id=recipient.id,
                    type=NotificationType.EXPENSE_CANCELLED,
                    title="Expense Cancelled",
                    message=f"An expense of ${expense.amount:.2f} has been cancelled.",
                    reference_id=expense.id,
                    reference_type="expense",
                    data={
                        "expense_id": expense.id,
                        "amount": expense.amount,
                        "category": expense.category,
                        "cancelled_by": cancelled_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    async def notify_attachment_added(
        self,
        db: Session,
        expense: Expense,
        attachment: ExpenseAttachment,
        added_by: User
    ):
        """Send notification when attachment is added to expense."""
        # Notify owner and approvers
        recipients = self._get_expense_stakeholders(db, expense)
        for recipient in recipients:
            if recipient.id != added_by.id:
                notification = Notification(
                    user_id=recipient.id,
                    type=NotificationType.EXPENSE_ATTACHMENT_ADDED,
                    title="Expense Attachment Added",
                    message=f"A new attachment has been added to expense ${expense.amount:.2f}.",
                    reference_id=expense.id,
                    reference_type="expense",
                    data={
                        "expense_id": expense.id,
                        "attachment_id": attachment.id,
                        "attachment_name": attachment.filename,
                        "added_by": added_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    async def notify_vendor_created(
        self,
        db: Session,
        vendor: Vendor,
        created_by: User
    ):
        """Send notification when vendor is created."""
        # Notify admins
        admins = self._get_admin_users(db)
        for admin in admins:
            if admin.id != created_by.id:
                notification = Notification(
                    user_id=admin.id,
                    type=NotificationType.VENDOR_CREATED,
                    title="New Vendor Added",
                    message=f"A new vendor '{vendor.name}' has been added.",
                    reference_id=vendor.id,
                    reference_type="vendor",
                    data={
                        "vendor_id": vendor.id,
                        "vendor_name": vendor.name,
                        "created_by": created_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    async def notify_vendor_updated(
        self,
        db: Session,
        vendor: Vendor,
        updated_by: User
    ):
        """Send notification when vendor is updated."""
        # Notify admins
        admins = self._get_admin_users(db)
        for admin in admins:
            if admin.id != updated_by.id:
                notification = Notification(
                    user_id=admin.id,
                    type=NotificationType.VENDOR_UPDATED,
                    title="Vendor Updated",
                    message=f"Vendor '{vendor.name}' has been updated.",
                    reference_id=vendor.id,
                    reference_type="vendor",
                    data={
                        "vendor_id": vendor.id,
                        "vendor_name": vendor.name,
                        "updated_by": updated_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    async def notify_vendor_rated(
        self,
        db: Session,
        vendor: Vendor,
        rating: float,
        rated_by: User
    ):
        """Send notification when vendor is rated."""
        # Notify admins
        admins = self._get_admin_users(db)
        for admin in admins:
            if admin.id != rated_by.id:
                notification = Notification(
                    user_id=admin.id,
                    type=NotificationType.VENDOR_RATED,
                    title="Vendor Rated",
                    message=f"Vendor '{vendor.name}' has received a new rating of {rating}.",
                    reference_id=vendor.id,
                    reference_type="vendor",
                    data={
                        "vendor_id": vendor.id,
                        "vendor_name": vendor.name,
                        "rating": rating,
                        "rated_by": rated_by.full_name
                    }
                )
                await self.send_notification(db, notification, BackgroundTasks())

    def _get_expense_approvers(self, db: Session, expense: Expense) -> List[User]:
        """Get list of users who can approve the expense."""
        # TODO: Implement logic to get approvers based on expense amount and type
        return []

    def _get_expense_stakeholders(self, db: Session, expense: Expense) -> List[User]:
        """Get list of users interested in the expense (owner, approvers)."""
        stakeholders = set()
        stakeholders.add(expense.created_by)
        stakeholders.update(self._get_expense_approvers(db, expense))
        return list(stakeholders)

    def _get_admin_users(self, db: Session) -> List[User]:
        """Get list of admin users."""
        # TODO: Implement logic to get admin users
        return []

notification_service = NotificationService()
