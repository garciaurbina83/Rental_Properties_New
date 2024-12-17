"""
Módulo para la gestión de roles y permisos en la aplicación.
Define los roles disponibles y sus permisos asociados.
"""

from typing import Dict, List, Set

# Definición de permisos disponibles
PERMISSIONS = {
    # Permisos de propiedades
    "property:read": "Ver propiedades",
    "property:write": "Crear y modificar propiedades",
    "property:delete": "Eliminar propiedades",
    
    # Permisos de inquilinos
    "tenant:read": "Ver inquilinos",
    "tenant:write": "Gestionar inquilinos",
    "tenant:delete": "Eliminar inquilinos",
    
    # Permisos de contratos
    "contract:read": "Ver contratos",
    "contract:write": "Gestionar contratos",
    "contract:delete": "Eliminar contratos",
    
    # Permisos de pagos
    "payment:read": "Ver pagos",
    "payment:write": "Gestionar pagos",
    
    # Permisos de mantenimiento
    "maintenance:read": "Ver solicitudes de mantenimiento",
    "maintenance:write": "Gestionar mantenimiento",
    
    # Permisos de administración
    "admin:access": "Acceso a funciones administrativas",
    "user:manage": "Gestionar usuarios"
}

# Definición de roles y sus permisos asociados
ROLES: Dict[str, List[str]] = {
    "admin": list(PERMISSIONS.keys()),  # Administrador tiene todos los permisos
    
    "property_manager": [
        "property:read", "property:write",
        "tenant:read", "tenant:write",
        "contract:read", "contract:write",
        "payment:read", "payment:write",
        "maintenance:read", "maintenance:write"
    ],
    
    "tenant": [
        "property:read",
        "tenant:read",
        "contract:read",
        "payment:read",
        "maintenance:read", "maintenance:write"
    ],
    
    "maintenance_staff": [
        "property:read",
        "maintenance:read", "maintenance:write"
    ],
    
    "viewer": [
        "property:read",
        "tenant:read",
        "contract:read",
        "payment:read",
        "maintenance:read"
    ]
}

def get_role_permissions(role: str) -> Set[str]:
    """
    Obtiene los permisos asociados a un rol específico.
    
    Args:
        role (str): Nombre del rol
        
    Returns:
        Set[str]: Conjunto de permisos asociados al rol
    """
    return set(ROLES.get(role, []))

def get_user_permissions(roles: List[str]) -> Set[str]:
    """
    Obtiene todos los permisos de un usuario basado en sus roles.
    
    Args:
        roles (List[str]): Lista de roles del usuario
        
    Returns:
        Set[str]: Conjunto de todos los permisos del usuario
    """
    permissions = set()
    for role in roles:
        permissions.update(get_role_permissions(role))
    return permissions

def has_required_permissions(user_permissions: Set[str], required_permissions: List[str]) -> bool:
    """
    Verifica si un usuario tiene todos los permisos requeridos.
    
    Args:
        user_permissions (Set[str]): Conjunto de permisos del usuario
        required_permissions (List[str]): Lista de permisos requeridos
        
    Returns:
        bool: True si el usuario tiene todos los permisos requeridos
    """
    return all(perm in user_permissions for perm in required_permissions)

def get_available_roles() -> Dict[str, List[str]]:
    """
    Obtiene todos los roles disponibles y sus permisos asociados.
    
    Returns:
        Dict[str, List[str]]: Diccionario de roles y sus permisos
    """
    return ROLES
