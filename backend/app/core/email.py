import logging
from typing import Dict, Any, List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.core.config import settings
from app.schemas.notification import NotificationType
import logging

logger = logging.getLogger(__name__)

class EmailManager:
    def __init__(self):
        self.templates_dir = Path("app/templates/email")
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir))
        )
        
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True
        )
        
        self.fastmail = FastMail(self.mail_config)
        
        # Template mapping
        self.template_map = {
            NotificationType.EXPENSE_CREATED: "expense_created.html",
            NotificationType.EXPENSE_UPDATED: "expense_updated.html",
            NotificationType.EXPENSE_APPROVED: "expense_approved.html",
            NotificationType.EXPENSE_CANCELLED: "expense_cancelled.html",
            NotificationType.EXPENSE_ATTACHMENT_ADDED: "expense_attachment.html",
            NotificationType.EXPENSE_REMINDER: "expense_reminder.html",
            NotificationType.RECURRING_EXPENSE_DUE: "recurring_expense.html",
            NotificationType.VENDOR_CREATED: "vendor_created.html",
            NotificationType.VENDOR_UPDATED: "vendor_updated.html",
            NotificationType.VENDOR_RATED: "vendor_rated.html"
        }
        
        # Subject mapping
        self.subject_map = {
            NotificationType.EXPENSE_CREATED: "New Expense Requires Approval",
            NotificationType.EXPENSE_UPDATED: "Expense Updated",
            NotificationType.EXPENSE_APPROVED: "Expense Approved",
            NotificationType.EXPENSE_CANCELLED: "Expense Cancelled",
            NotificationType.EXPENSE_ATTACHMENT_ADDED: "New Attachment Added to Expense",
            NotificationType.EXPENSE_REMINDER: "Pending Expense Reminder",
            NotificationType.RECURRING_EXPENSE_DUE: "Recurring Expense Due",
            NotificationType.VENDOR_CREATED: "New Vendor Added",
            NotificationType.VENDOR_UPDATED: "Vendor Information Updated",
            NotificationType.VENDOR_RATED: "New Vendor Rating"
        }

    async def send_notification(self, notification) -> bool:
        """
        Send an email notification using the appropriate template.
        """
        try:
            template_name = self.template_map.get(notification.type)
            if not template_name:
                logger.error(f"No template found for notification type: {notification.type}")
                return False

            template = self.env.get_template(template_name)
            html_content = template.render(
                title=self.subject_map.get(notification.type),
                **notification.data
            )

            message = MessageSchema(
                subject=self.subject_map.get(notification.type),
                recipients=[notification.user.email],
                body=html_content,
                subtype="html"
            )

            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully to {notification.user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False

    def _format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        return f"${amount:,.2f}"

    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        from datetime import datetime
        date = datetime.fromisoformat(date_str)
        return date.strftime("%B %d, %Y")

email_manager = EmailManager()
