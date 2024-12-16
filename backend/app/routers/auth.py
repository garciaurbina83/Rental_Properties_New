from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from ..core.security import get_current_user, check_permissions, ROLES
from ..schemas.auth import UserResponse, RoleResponse

router = APIRouter()

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Obtiene la información del usuario autenticado actualmente.",
)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtiene información del usuario actual.
    """
    return {
        "id": current_user.get("sub"),
        "email": current_user.get("email"),
        "name": current_user.get("name", ""),
        "roles": current_user.get("roles", []),
        "permissions": current_user.get("permissions", [])
    }

@router.get(
    "/roles",
    response_model=Dict[str, RoleResponse],
    summary="Obtener roles disponibles",
    description="""
    Obtiene la lista de roles disponibles y sus permisos asociados.
    Requiere el permiso 'admin:read'.
    """,
)
async def get_roles(
    current_user: Dict = Depends(get_current_user),
    _: Dict = Depends(check_permissions(["admin:read"]))
):
    """
    Obtiene la lista de roles y sus permisos.
    """
    return {
        role: {"name": role, "permissions": permissions}
        for role, permissions in ROLES.items()
    }

@router.get(
    "/verify",
    summary="Verificar token",
    description="Verifica si el token JWT actual es válido.",
)
async def verify_token(
    current_user: Dict = Depends(get_current_user)
):
    """
    Verifica la validez del token actual.
    """
    return {
        "valid": True,
        "user_id": current_user.get("sub"),
        "expires_at": current_user.get("exp")
    }

@router.get(
    "/permissions",
    summary="Verificar permisos",
    description="Verifica si el usuario tiene los permisos especificados.",
)
async def check_user_permissions(
    permissions: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Verifica si el usuario tiene los permisos especificados.
    """
    required_permissions = permissions.split(",")
    user_permissions = current_user.get("permissions", [])
    
    has_permissions = all(
        perm in user_permissions 
        for perm in required_permissions
    )
    
    if not has_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no tiene los permisos requeridos"
        )
    
    return {
        "has_permissions": True,
        "required_permissions": required_permissions,
        "user_permissions": user_permissions
    }
