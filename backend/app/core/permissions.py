from typing import Dict, List, Set
from enum import Enum
from fastapi import HTTPException

# Definición de roles y sus permisos correspondientes
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": [
        "create_property",
        "read_property",
        "update_property",
        "delete_property",
        "manage_users",
        "manage_payments",
        "view_reports",
        "manage_maintenance"
    ],
    "property_manager": [
        "create_property",
        "read_property",
        "update_property",
        "manage_tenants",
        "manage_payments",
        "view_reports",
        "create_maintenance_request"
    ],
    "tenant": [
        "read_property",
        "create_maintenance_request",
        "view_own_payments",
        "update_profile"
    ],
    "maintenance": [
        "read_property",
        "update_maintenance_status",
        "view_maintenance_requests"
    ],
    "viewer": [
        "read_property",
        "view_reports"
    ]
}

class PermissionLevel(Enum):
    READ = "read"
    WRITE = "write"
    APPROVE = "approve"
    ADMIN = "admin"

class ExpensePermission:
    def __init__(self, user, expense=None):
        self.user = user
        self.expense = expense

    def can_create(self) -> bool:
        return self.user.is_active

    def can_read(self) -> bool:
        if not self.expense:
            return self.user.is_active
        return (
            self.user.is_active and
            (self.user.is_superuser or
             self.expense.created_by_id == self.user.id or
             self.user.has_permission(PermissionLevel.READ))
        )

    def can_update(self) -> bool:
        if not self.expense:
            return False
        return (
            self.user.is_active and
            (self.user.is_superuser or
             self.expense.created_by_id == self.user.id or
             self.user.has_permission(PermissionLevel.WRITE))
        )

    def can_delete(self) -> bool:
        if not self.expense:
            return False
        return (
            self.user.is_active and
            (self.user.is_superuser or
             self.expense.created_by_id == self.user.id)
        )

    def can_approve(self) -> bool:
        if not self.expense:
            return False
        return (
            self.user.is_active and
            self.user.has_permission(PermissionLevel.APPROVE) and
            self.expense.created_by_id != self.user.id  # No self-approval
        )

    def check_amount_limit(self, amount: float) -> bool:
        """Check if user can approve expense with given amount."""
        if not self.user.approval_limit:
            return True
        return amount <= self.user.approval_limit

def check_permission(permission_func, error_message: str = "Not enough permissions"):
    """Decorator to check permissions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not permission_func(*args, **kwargs):
                raise HTTPException(status_code=403, detail=error_message)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_permissions_for_role(role: str) -> Set[str]:
    """
    Obtiene todos los permisos asociados a un rol específico
    """
    return set(ROLE_PERMISSIONS.get(role, []))

def get_all_permissions_for_roles(roles: List[str]) -> Set[str]:
    """
    Obtiene todos los permisos únicos para una lista de roles
    """
    permissions = set()
    for role in roles:
        permissions.update(get_permissions_for_role(role))
    return permissions

def get_all_available_roles() -> List[str]:
    """
    Retorna todos los roles disponibles en el sistema
    """
    return list(ROLE_PERMISSIONS.keys())

def get_all_available_permissions() -> Set[str]:
    """
    Retorna todos los permisos únicos disponibles en el sistema
    """
    permissions = set()
    for role_permissions in ROLE_PERMISSIONS.values():
        permissions.update(role_permissions)
    return permissions

def validate_role(role: str) -> bool:
    """
    Valida si un rol existe en el sistema
    """
    return role in ROLE_PERMISSIONS

def validate_permission(permission: str) -> bool:
    """
    Valida si un permiso existe en el sistema
    """
    return permission in get_all_available_permissions()

def get_role_hierarchy() -> Dict[str, Dict]:
    """
    Retorna la jerarquía de roles con sus permisos correspondientes
    """
    return {
        role: {
            "permissions": permissions,
            "permission_count": len(permissions)
        }
        for role, permissions in ROLE_PERMISSIONS.items()
    }
