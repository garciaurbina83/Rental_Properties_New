"""
Test-specific authentication module that bypasses Clerk in test environment.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from .config import settings

security = HTTPBearer()

def create_test_token() -> str:
    """
    Create a test JWT token for testing purposes
    """
    payload = {
        "sub": "test_user_id",
        "id": "test_user_id",  # Make sure id is present
        "email": "test@example.com",
        "name": "Test User",
        "permissions": [
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
            "admin:read"
        ],
        "active": True,
        "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp())
    }
    
    token = jwt.encode(
        payload,
        "test_secret_key_for_development_only",  # Use a fixed test key
        algorithm="HS256"
    )
    return token

def verify_test_token(token: str) -> Dict[str, Any]:
    """
    Verify a test JWT token
    """
    try:
        payload = jwt.decode(
            token,
            "test_secret_key_for_development_only",  # Use the same fixed test key
            algorithms=["HS256"]
        )
        # Make sure id is present
        if "id" not in payload and "sub" in payload:
            payload["id"] = payload["sub"]
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_test_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Get test user data from token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return verify_test_token(credentials.credentials)
