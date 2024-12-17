import logging
from typing import Dict, Any
from twilio.rest import Client
from app.core.config import settings
from app.schemas.notification import NotificationType

logger = logging.getLogger(__name__)

class SMSManager:
    def __init__(self):
        try:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.from_number = settings.TWILIO_FROM_NUMBER
            self.initialized = True
            
            # Message templates for different notification types
            self.message_templates = {
                NotificationType.EXPENSE_CREATED: (
                    "New expense of {amount} requires your approval. "
                    "Created by {created_by}."
                ),
                NotificationType.EXPENSE_UPDATED: (
                    "Expense #{expense_id} has been updated by {updated_by}. "
                    "Amount: {amount}"
                ),
                NotificationType.EXPENSE_APPROVED: (
                    "Your expense of {amount} has been approved by {approved_by}."
                ),
                NotificationType.EXPENSE_CANCELLED: (
                    "Expense #{expense_id} has been cancelled by {cancelled_by}."
                ),
                NotificationType.EXPENSE_ATTACHMENT_ADDED: (
                    "New attachment added to expense #{expense_id} by {added_by}."
                ),
                NotificationType.EXPENSE_REMINDER: (
                    "Reminder: Expense of {amount} has been pending for {days_pending} days."
                ),
                NotificationType.RECURRING_EXPENSE_DUE: (
                    "Recurring expense of {amount} is due on {due_date}."
                ),
                NotificationType.VENDOR_CREATED: (
                    "New vendor {vendor_name} has been added by {created_by}."
                ),
                NotificationType.VENDOR_UPDATED: (
                    "Vendor {vendor_name} information has been updated by {updated_by}."
                ),
                NotificationType.VENDOR_RATED: (
                    "Vendor {vendor_name} has received a new rating of {rating}/5."
                )
            }
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.initialized = False

    async def send_notification(self, notification) -> bool:
        """
        Send an SMS notification using Twilio.
        """
        if not self.initialized:
            logger.error("Twilio client not initialized")
            return False

        try:
            if not notification.user.phone:
                logger.warning(f"No phone number for user {notification.user.id}")
                return False

            template = self.message_templates.get(notification.type)
            if not template:
                logger.error(f"No template found for notification type: {notification.type}")
                return False

            # Format message with notification data
            message = template.format(**notification.data)

            # Add amount formatting if present in data
            if "amount" in notification.data:
                notification.data["amount"] = self._format_currency(notification.data["amount"])
            
            # Add date formatting if present in data
            if "due_date" in notification.data:
                notification.data["due_date"] = self._format_date(notification.data["due_date"])

            # Send SMS
            response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=notification.user.phone
            )

            logger.info(f"Successfully sent SMS notification: {response.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False

    def _format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        return f"${amount:,.2f}"

    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        from datetime import datetime
        date = datetime.fromisoformat(date_str)
        return date.strftime("%B %d, %Y")

sms_manager = SMSManager()
