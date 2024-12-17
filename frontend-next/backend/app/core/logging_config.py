import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from app.core.config import settings

def setup_logging():
    """
    Configure logging for the notification system.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # File handlers
    # General log file
    general_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "notification_system.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    general_handler.setFormatter(file_formatter)
    general_handler.setLevel(logging.INFO)
    root_logger.addHandler(general_handler)

    # Error log file
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "notification_errors.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Notification delivery log file
    delivery_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "notification_delivery.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    delivery_handler.setFormatter(file_formatter)
    delivery_handler.setLevel(logging.INFO)
    
    # Create specific logger for notification delivery
    delivery_logger = logging.getLogger("notification.delivery")
    delivery_logger.addHandler(delivery_handler)
    delivery_logger.propagate = False  # Don't propagate to root logger

    # Set logging levels based on environment
    if settings.ENVIRONMENT.lower() == "development":
        root_logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)

    logging.info("Logging system initialized successfully")
