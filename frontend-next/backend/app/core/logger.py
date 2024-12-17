"""
Configuración centralizada de logging para la aplicación.
Utiliza Loguru para un manejo más eficiente y flexible de logs.
"""

import sys
import logging
from pathlib import Path
from loguru import logger
from .config import settings

# Configuración de logs
LOG_LEVEL = settings.log_level
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Crear directorio de logs si no existe
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class InterceptHandler(logging.Handler):
    """
    Interceptor para redirigir los logs de Python estándar a Loguru.
    Esto asegura que todos los logs (incluyendo los de FastAPI) sean manejados por Loguru.
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    Configura el sistema de logging con Loguru.
    - Configura el formato de los logs
    - Establece los niveles de logging
    - Configura los handlers para diferentes tipos de logs
    """
    # Remover el handler por defecto
    logger.remove()
    
    # Configurar el handler para la consola
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True,
    )
    
    # Configurar el handler para archivo de logs general
    logger.add(
        LOG_DIR / "app.log",
        rotation="500 MB",
        retention="10 days",
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        compression="zip",
    )
    
    # Configurar el handler para errores
    logger.add(
        LOG_DIR / "error.log",
        rotation="100 MB",
        retention="30 days",
        format=LOG_FORMAT,
        level="ERROR",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # Configurar el handler para accesos a la API
    logger.add(
        LOG_DIR / "access.log",
        rotation="1 day",
        retention="7 days",
        format=LOG_FORMAT,
        level="INFO",
        compression="zip",
        filter=lambda record: "access" in record["extra"],
    )

    # Interceptar logs de Python estándar
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Interceptar logs de otras bibliotecas
    for logger_name in [
        "uvicorn",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "alembic",
    ]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

    return logger

# Exportar el logger configurado
logger = setup_logging()
