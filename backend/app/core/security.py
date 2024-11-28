"""
Security module for handling authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from jwt.exceptions import InvalidTokenError
from .config import settings
from .test_auth import get_test_user, verify_test_token

security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=False
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
    Verify a JWT token based on environment
    """
    if settings.ENVIRONMENT == "test":
        return verify_test_token(token)
    else:
        # Use Clerk verification for non-test environments
        try:
            jwks = await get_clerk_jwks()
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the correct key in JWKS
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
            
            # Verify the token
            payload = jwt.decode(
                token,
                key=key,
                algorithms=['RS256'],
                audience=settings.CLERK_PUBLISHABLE_KEY,
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
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Get current user based on environment
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    if settings.ENVIRONMENT == "test":
        return await get_test_user(credentials)
    
    token = credentials.credentials
    user_data = await verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    if not user_data.get('active', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    return user_data

def check_permissions(required_permissions: list[str]):
    """
    Check if user has required permissions
    """
    async def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get('permissions', [])
        
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
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

def create_test_token(user_id: str = "test_user", role: str = "admin") -> str:
    """Create a test JWT token with specified user_id and role"""
    permissions = ROLES.get(role, [])
    payload = {
        "sub": user_id,
        "permissions": permissions,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
