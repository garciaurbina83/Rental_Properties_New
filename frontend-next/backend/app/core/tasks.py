import logging
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.notification_service import notification_service

# Configure logging
logger = logging.getLogger(__name__)

async def process_notifications(background_tasks: BackgroundTasks):
    """
    Process pending notifications in the background.
    """
    try:
        db = SessionLocal()
        await notification_service.send_reminder_notifications(db, datetime.utcnow())
        db.close()
    except Exception as e:
        logger.error(f"Error processing notifications: {str(e)}")

async def schedule_notification_tasks(background_tasks: BackgroundTasks):
    """
    Schedule notification-related background tasks.
    """
    # Schedule reminder notifications
    background_tasks.add_task(process_notifications)
    
    # Schedule recurring tasks (can be expanded based on needs)
    # For example, daily summaries, weekly reports, etc.

def start_background_tasks():
    """
    Start all background tasks when the application starts.
    """
    background_tasks = BackgroundTasks()
    schedule_notification_tasks(background_tasks)
