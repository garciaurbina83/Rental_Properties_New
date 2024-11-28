from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import InvalidTokenError
import httpx
from .config import settings

security = HTTPBearer(
    scheme_name="Clerk JWT",
    description="Ingrese su token JWT de Clerk",
    auto_error=True
)

async def get_clerk_jwks() -> Dict[str, Any]:
    """
    Obtiene las claves públicas de Clerk para verificar tokens
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{settings.clerk_frontend_api}/.well-known/jwks.json")
        response.raise_for_status()
        return response.json()

async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica un token JWT de Clerk
    """
    try:
        jwks = await get_clerk_jwks()
        unverified_header = jwt.get_unverified_header(token)
        
        # Encontrar la clave correcta en el JWKS
        key = None
        for jwk in jwks['keys']:
            if jwk['kid'] == unverified_header['kid']:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
            )
        
        # Verificar el token
        payload = jwt.decode(
            token,
            key=key,
            algorithms=['RS256'],
            audience=settings.clerk_frontend_api,
            options={"verify_exp": True}
        )
        
        return payload
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error validating token: {str(e)}",
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependencia para obtener el usuario actual desde el token JWT
    """
    token = credentials.credentials
    user_data = await verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Verificar si el usuario está activo
    if not user_data.get('active', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    return user_data

def check_permissions(required_permissions: list[str]):
    """
    Decorador para verificar permisos de usuario
    """
    async def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get('permissions', [])
        
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        
        return user
    
    return permission_checker

# Roles y permisos predefinidos
ROLES = {
    "admin": [
        "property:read",
        "property:write",
        "property:delete",
        "tenant:read",
        "tenant:write",
        "tenant:delete",
        "contract:read",
        "contract:write",
        "contract:delete",
        "payment:read",
        "payment:write",
        "payment:delete",
        "maintenance:read",
        "maintenance:write",
        "maintenance:delete",
    ],
    "property_manager": [
        "property:read",
        "property:write",
        "tenant:read",
        "tenant:write",
        "contract:read",
        "contract:write",
        "payment:read",
        "maintenance:read",
        "maintenance:write",
    ],
    "tenant": [
        "property:read",
        "contract:read",
        "payment:read",
        "payment:write",
        "maintenance:read",
        "maintenance:write",
    ],
}
