"""
Middleware personalizado para la aplicación.
Incluye middleware para logging, manejo de errores y métricas.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import logger
from .exceptions import AppError

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar información sobre las solicitudes HTTP.
    Registra el tiempo de respuesta, método, ruta y código de estado.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generar ID único para la request
        request_id = str(time.time())
        request.state.request_id = request_id
        
        # Log de inicio de request
        logger.bind(request_id=request_id).info(
            f"Started {request.method} {request.url.path}"
        )
        
        try:
            response = await call_next(request)
            
            # Calcular tiempo de proceso
            process_time = time.time() - start_time
            
            # Log de fin de request
            logger.bind(
                request_id=request_id,
                access=True
            ).info(
                f"Completed {request.method} {request.url.path} "
                f"[{response.status_code}] in {process_time:.2f}s"
            )
            
            # Agregar headers de rendimiento
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log de error
            logger.bind(request_id=request_id).error(
                f"Error processing {request.method} {request.url.path}: {str(e)}"
            )
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para el manejo centralizado de errores.
    Captura excepciones y las convierte en respuestas HTTP apropiadas.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppError as e:
            # Manejar errores de aplicación personalizados
            logger.bind(
                request_id=request.state.request_id
            ).error(f"Application error: {str(e)}")
            return e.to_response()
        except Exception as e:
            # Manejar errores no esperados
            logger.bind(
                request_id=request.state.request_id
            ).exception("Unexpected error occurred")
            return {
                "detail": "Internal server error",
                "type": "InternalError",
                "request_id": request.state.request_id
            }

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para recolectar métricas de la aplicación.
    Registra tiempos de respuesta, contadores de endpoints, etc.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas
            process_time = time.time() - start_time
            endpoint = f"{request.method} {request.url.path}"
            
            # TODO: Integrar con sistema de métricas (e.g., Prometheus)
            logger.bind(
                metrics=True,
                endpoint=endpoint,
                process_time=process_time,
                status_code=response.status_code
            ).debug("Request metrics collected")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            endpoint = f"{request.method} {request.url.path}"
            
            # Registrar métricas de error
            logger.bind(
                metrics=True,
                endpoint=endpoint,
                process_time=process_time,
                error=str(e)
            ).debug("Error metrics collected")
            
            raise
