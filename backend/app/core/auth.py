from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..core.config import settings
import jwt
from typing import Optional, Dict, List
import requests
from functools import lru_cache

security = HTTPBearer()

class ClerkAuth:
    def __init__(self):
        self.clerk_secret_key = settings.CLERK_SECRET_KEY
        self.clerk_api_base = "https://api.clerk.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.clerk_secret_key}",
            "Content-Type": "application/json"
        }
    
    @lru_cache(maxsize=128)
    def get_user_metadata(self, user_id: str) -> Dict:
        """Get user metadata from Clerk"""
        response = requests.get(
            f"{self.clerk_api_base}/users/{user_id}/metadata",
            headers=self.headers
        )
        if response.status_code != 200:
            return {}
        return response.json()
    
    def verify_token(self, token: str) -> Dict:
        """Verify a Clerk JWT token"""
        try:
            # Verify the session
            response = requests.get(
                f"{self.clerk_api_base}/sessions/{token}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
                
            session_data = response.json()
            
            # Get user data
            user_response = requests.get(
                f"{self.clerk_api_base}/users/{session_data['user_id']}",
                headers=self.headers
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not verify user"
                )
                
            user_data = user_response.json()
            
            # Get user metadata (includes roles and permissions)
            user_metadata = self.get_user_metadata(user_data["id"])
            
            return {
                "user_id": user_data["id"],
                "email": user_data["email_addresses"][0]["email_address"],
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "session_id": session_data["id"],
                "roles": user_metadata.get("roles", []),
                "permissions": user_metadata.get("permissions", [])
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    def has_role(self, user_data: Dict, required_roles: List[str]) -> bool:
        """Check if user has any of the required roles"""
        user_roles = user_data.get("roles", [])
        return any(role in required_roles for role in user_roles)
    
    def has_permission(self, user_data: Dict, required_permissions: List[str]) -> bool:
        """Check if user has all required permissions"""
        user_permissions = user_data.get("permissions", [])
        return all(perm in user_permissions for perm in required_permissions)

clerk_auth = ClerkAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Dependency to get the current authenticated user
    
    Args:
        credentials: The HTTP Bearer token
        
    Returns:
        Dict: User information including roles and permissions
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        user_data = clerk_auth.verify_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

def require_roles(roles: List[str]):
    """
    Dependency to require specific roles
    
    Args:
        roles: List of required roles
    """
    async def role_checker(user: Dict = Depends(get_current_user)):
        if not clerk_auth.has_role(user, roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required roles: {roles}"
            )
        return user
    return role_checker

def require_permissions(permissions: List[str]):
    """
    Dependency to require specific permissions
    
    Args:
        permissions: List of required permissions
    """
    async def permission_checker(user: Dict = Depends(get_current_user)):
        if not clerk_auth.has_permission(user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permissions: {permissions}"
            )
        return user
    return permission_checker
