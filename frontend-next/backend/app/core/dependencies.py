"""
Módulo para las dependencias de FastAPI relacionadas con autenticación y autorización.
"""

from typing import List, Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token, get_jwks
from app.core.roles import get_user_permissions, has_required_permissions
from app.core.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    TokenVerificationError
)

security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependencia para obtener el usuario actual a partir del token JWT.
    
    Args:
        request (Request): Objeto Request de FastAPI
        credentials (HTTPAuthorizationCredentials): Credenciales de autorización
        
    Returns:
        dict: Información del usuario autenticado
        
    Raises:
        AuthenticationError: Si las credenciales no son válidas
        TokenVerificationError: Si hay un error al verificar el token
    """
    try:
        jwks = await get_jwks()
        token = credentials.credentials
        payload = await verify_token(token, jwks)
        
        # Almacenar el payload del token en el request state para uso posterior
        request.state.user = payload
        return payload
    except Exception as e:
        raise AuthenticationError(str(e))

def check_permissions(required_permissions: List[str]):
    """
    Dependencia para verificar los permisos del usuario.
    
    Args:
        required_permissions (List[str]): Lista de permisos requeridos
        
    Returns:
        Callable: Función de dependencia de FastAPI
        
    Raises:
        PermissionDeniedError: Si el usuario no tiene los permisos necesarios
    """
    async def permission_checker(user: dict = Depends(get_current_user)) -> None:
        user_roles = user.get("roles", [])
        user_permissions = get_user_permissions(user_roles)
        
        if not has_required_permissions(user_permissions, required_permissions):
            raise PermissionDeniedError(
                f"Required permissions: {', '.join(required_permissions)}"
            )
    
    return permission_checker

def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Dependencia para autenticación opcional.
    Útil para endpoints que pueden funcionar con o sin autenticación.
    
    Args:
        credentials (Optional[HTTPAuthorizationCredentials]): Credenciales opcionales
        
    Returns:
        Optional[dict]: Información del usuario si está autenticado, None si no
    """
    if not credentials:
        return None
        
    try:
        jwks = await get_jwks()
        token = credentials.credentials
        return await verify_token(token, jwks)
    except Exception:
        return None
