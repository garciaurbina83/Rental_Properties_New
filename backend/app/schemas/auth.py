from typing import List, Optional
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    """Esquema para la respuesta de información de usuario"""
    id: str
    email: EmailStr
    name: str
    roles: List[str]
    permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_2xJ8K9p4M5",
                "email": "user@example.com",
                "name": "John Doe",
                "roles": ["property_manager"],
                "permissions": ["property:read", "property:write"]
            }
        }

class RoleResponse(BaseModel):
    """Esquema para la respuesta de roles"""
    name: str
    permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "property_manager",
                "permissions": [
                    "property:read",
                    "property:write",
                    "tenant:read",
                    "tenant:write"
                ]
            }
        }

class TokenVerifyResponse(BaseModel):
    """Esquema para la respuesta de verificación de token"""
    valid: bool
    user_id: str
    expires_at: int

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user_id": "user_2xJ8K9p4M5",
                "expires_at": 1637097600
            }
        }

class PermissionCheckResponse(BaseModel):
    """Esquema para la respuesta de verificación de permisos"""
    has_permissions: bool
    required_permissions: List[str]
    user_permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "has_permissions": True,
                "required_permissions": ["property:read"],
                "user_permissions": [
                    "property:read",
                    "property:write",
                    "tenant:read"
                ]
            }
        }
