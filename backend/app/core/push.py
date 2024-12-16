import logging
from typing import Dict, Any
from firebase_admin import messaging, initialize_app, credentials
from app.core.config import settings
from app.schemas.notification import NotificationType

logger = logging.getLogger(__name__)

class PushManager:
    def __init__(self):
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            initialize_app(cred)
            self.initialized = True
            
            # Title and body templates for different notification types
            self.notification_templates = {
                NotificationType.EXPENSE_CREATED: {
                    "title": "New Expense for Review",
                    "body": "A new expense of {amount} requires your approval"
                },
                NotificationType.EXPENSE_UPDATED: {
                    "title": "Expense Updated",
                    "body": "An expense has been updated by {updated_by}"
                },
                NotificationType.EXPENSE_APPROVED: {
                    "title": "Expense Approved",
                    "body": "Your expense of {amount} has been approved"
                },
                NotificationType.EXPENSE_CANCELLED: {
                    "title": "Expense Cancelled",
                    "body": "An expense has been cancelled by {cancelled_by}"
                },
                NotificationType.EXPENSE_ATTACHMENT_ADDED: {
                    "title": "New Attachment Added",
                    "body": "A new attachment has been added to expense #{expense_id}"
                },
                NotificationType.EXPENSE_REMINDER: {
                    "title": "Pending Expense Reminder",
                    "body": "You have a pending expense of {amount} awaiting approval"
                },
                NotificationType.RECURRING_EXPENSE_DUE: {
                    "title": "Recurring Expense Due",
                    "body": "Recurring expense of {amount} is due on {due_date}"
                },
                NotificationType.VENDOR_CREATED: {
                    "title": "New Vendor Added",
                    "body": "A new vendor {vendor_name} has been added"
                },
                NotificationType.VENDOR_UPDATED: {
                    "title": "Vendor Updated",
                    "body": "Vendor {vendor_name} information has been updated"
                },
                NotificationType.VENDOR_RATED: {
                    "title": "New Vendor Rating",
                    "body": "Vendor {vendor_name} has received a new rating"
                }
            }
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            self.initialized = False

    async def send_notification(self, notification) -> bool:
        """
        Send a push notification using Firebase Cloud Messaging.
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False

        try:
            if not notification.user.push_token:
                logger.warning(f"No push token for user {notification.user.id}")
                return False

            template = self.notification_templates.get(notification.type)
            if not template:
                logger.error(f"No template found for notification type: {notification.type}")
                return False

            # Format title and body with notification data
            title = template["title"].format(**notification.data)
            body = template["body"].format(**notification.data)

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    "type": notification.type.value,
                    "reference_id": str(notification.reference_id) if notification.reference_id else "",
                    "reference_type": notification.reference_type if notification.reference_type else ""
                },
                token=notification.user.push_token
            )

            response = messaging.send(message)
            logger.info(f"Successfully sent push notification: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False

    def _format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        return f"${amount:,.2f}"

    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        from datetime import datetime
        date = datetime.fromisoformat(date_str)
        return date.strftime("%B %d, %Y")

push_manager = PushManager()
