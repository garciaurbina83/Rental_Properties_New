"""
Módulo para manejar excepciones personalizadas de la aplicación.
"""

from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    """Excepción para errores de autenticación"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionDeniedError(HTTPException):
    """Excepción para errores de permisos"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class TokenVerificationError(HTTPException):
    """Excepción para errores en la verificación de tokens"""
    def __init__(self, detail: str = "Token verification failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class InvalidTokenError(HTTPException):
    """Excepción para tokens inválidos"""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class UserNotFoundError(HTTPException):
    """Excepción para usuarios no encontrados"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ConfigurationError(HTTPException):
    """Excepción para errores de configuración"""
    def __init__(self, detail: str = "Service configuration error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class BadRequestException(HTTPException):
    """Exception for bad request errors"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class NotFoundException(HTTPException):
    """Exception for not found errors"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
