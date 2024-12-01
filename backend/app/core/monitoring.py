"""
Configuración de monitoreo y métricas para la aplicación.
Integra Prometheus para métricas y Sentry para rastreo de errores.
"""

import time
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .logger import logger
import logging
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
from app.schemas.notification import NotificationType, NotificationChannel, NotificationStatus

# Configure logging
logger = logging.getLogger(__name__)

# Configuración de Sentry
def init_sentry():
    """Inicializar Sentry para rastreo de errores"""
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=1.0,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # Configuración de rendimiento
        enable_tracing=True,
        profiles_sample_rate=1.0,
    )

# Métricas de Prometheus
# Contadores
http_requests_total = Counter(
    'http_requests_total',
    'Total de solicitudes HTTP',
    ['method', 'endpoint', 'status']
)

db_operations_total = Counter(
    'db_operations_total',
    'Total de operaciones de base de datos',
    ['operation', 'table']
)

errors_total = Counter(
    'errors_total',
    'Total de errores',
    ['type', 'endpoint']
)

notification_total = Counter(
    'notification_total',
    'Total number of notifications sent',
    ['type', 'channel', 'status']
)

# Histogramas
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'Duración de las solicitudes HTTP',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

db_operation_duration_seconds = Histogram(
    'db_operation_duration_seconds',
    'Duración de operaciones de base de datos',
    ['operation', 'table'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

notification_duration = Histogram(
    'notification_duration_seconds',
    'Time spent sending notifications',
    ['type', 'channel']
)

# Gauges
active_requests = Gauge(
    'active_requests',
    'Número actual de solicitudes activas'
)

db_connections = Gauge(
    'db_connections',
    'Número actual de conexiones a la base de datos'
)

notification_queue_size = Gauge(
    'notification_queue_size',
    'Number of notifications in queue'
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware para recolectar métricas de Prometheus"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        # Incrementar contadores
        active_requests.inc()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas
            duration = time.time() - start_time
            status = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status
            ).inc()
            
            request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Registrar errores
            errors_total.labels(
                type=type(e).__name__,
                endpoint=path
            ).inc()
            raise
            
        finally:
            active_requests.dec()

async def metrics_endpoint():
    """Endpoint para exponer métricas de Prometheus"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Funciones de utilidad para métricas
def track_db_operation(operation: str, table: str):
    """Decorador para rastrear operaciones de base de datos"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                db_operations_total.labels(
                    operation=operation,
                    table=table
                ).inc()
                
                db_operation_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                
                return result
                
            except Exception as e:
                errors_total.labels(
                    type=type(e).__name__,
                    endpoint=f"db_{table}_{operation}"
                ).inc()
                raise
                
        return wrapper
    return decorator

def track_error(error_type: str, endpoint: str):
    """Registrar un error en las métricas"""
    errors_total.labels(
        type=error_type,
        endpoint=endpoint
    ).inc()
    
def set_db_connections(count: int):
    """Actualizar el número de conexiones de base de datos"""
    db_connections.set(count)

class NotificationMonitoring:
    """
    Monitoring manager for notification-related metrics.
    """
    @staticmethod
    def record_notification_sent(
        notification_type: NotificationType,
        channel: NotificationChannel,
        status: NotificationStatus,
        duration: float
    ):
        """
        Record metrics for a sent notification.
        """
        try:
            # Increment notification counter
            notification_total.labels(
                type=notification_type.value,
                channel=channel.value,
                status=status.value
            ).inc()

            # Record sending duration
            notification_duration.labels(
                type=notification_type.value,
                channel=channel.value
            ).observe(duration)

            logger.info(
                f"Notification metrics recorded - Type: {notification_type}, "
                f"Channel: {channel}, Status: {status}, Duration: {duration:.2f}s"
            )
        except Exception as e:
            logger.error(f"Failed to record notification metrics: {str(e)}")

    @staticmethod
    def update_queue_size(size: int):
        """
        Update notification queue size metric.
        """
        try:
            notification_queue_size.set(size)
        except Exception as e:
            logger.error(f"Failed to update queue size metric: {str(e)}")

    @staticmethod
    def monitor_notification_sending(func):
        """
        Decorator to monitor notification sending.
        """
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract notification details from the first argument (notification object)
                if args and hasattr(args[0], 'type') and hasattr(args[0], 'channels'):
                    notification = args[0]
                    for channel in notification.channels:
                        NotificationMonitoring.record_notification_sent(
                            notification.type,
                            channel,
                            NotificationStatus.SENT,
                            duration
                        )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failure metrics
                if args and hasattr(args[0], 'type') and hasattr(args[0], 'channels'):
                    notification = args[0]
                    for channel in notification.channels:
                        NotificationMonitoring.record_notification_sent(
                            notification.type,
                            channel,
                            NotificationStatus.FAILED,
                            duration
                        )
                
                raise e
        
        return wrapper

notification_monitoring = NotificationMonitoring()
