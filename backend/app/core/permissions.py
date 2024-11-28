from typing import Dict, List, Set

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
