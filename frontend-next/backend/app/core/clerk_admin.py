import requests
from typing import List, Dict
from .config import settings
from .permissions import get_permissions_for_role, validate_role

class ClerkAdmin:
    def __init__(self):
        self.clerk_secret_key = settings.clerk_secret_key
        self.clerk_api_base = "https://api.clerk.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.clerk_secret_key}",
            "Content-Type": "application/json"
        }

    def get_all_users(self) -> List[Dict]:
        """
        Obtiene todos los usuarios de Clerk
        """
        response = requests.get(
            f"{self.clerk_api_base}/users",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id: str) -> Dict:
        """
        Obtiene un usuario específico de Clerk
        """
        response = requests.get(
            f"{self.clerk_api_base}/users/{user_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_user_metadata(self, user_id: str, metadata: Dict) -> Dict:
        """
        Actualiza los metadatos de un usuario
        """
        response = requests.patch(
            f"{self.clerk_api_base}/users/{user_id}/metadata",
            headers=self.headers,
            json=metadata
        )
        response.raise_for_status()
        return response.json()

    def assign_role(self, user_id: str, role: str) -> Dict:
        """
        Asigna un rol a un usuario y actualiza sus permisos
        """
        if not validate_role(role):
            raise ValueError(f"Rol inválido: {role}")

        # Obtener metadatos actuales
        user = self.get_user(user_id)
        current_metadata = user.get("metadata", {})
        
        # Obtener roles actuales
        current_roles = current_metadata.get("roles", [])
        if role not in current_roles:
            current_roles.append(role)

        # Obtener todos los permisos basados en los roles
        permissions = set()
        for user_role in current_roles:
            permissions.update(get_permissions_for_role(user_role))

        # Actualizar metadatos
        new_metadata = {
            "roles": current_roles,
            "permissions": list(permissions)
        }

        return self.update_user_metadata(user_id, new_metadata)

    def remove_role(self, user_id: str, role: str) -> Dict:
        """
        Remueve un rol de un usuario y actualiza sus permisos
        """
        # Obtener metadatos actuales
        user = self.get_user(user_id)
        current_metadata = user.get("metadata", {})
        
        # Obtener roles actuales
        current_roles = current_metadata.get("roles", [])
        if role in current_roles:
            current_roles.remove(role)

        # Obtener todos los permisos basados en los roles restantes
        permissions = set()
        for user_role in current_roles:
            permissions.update(get_permissions_for_role(user_role))

        # Actualizar metadatos
        new_metadata = {
            "roles": current_roles,
            "permissions": list(permissions)
        }

        return self.update_user_metadata(user_id, new_metadata)

    def get_user_roles_and_permissions(self, user_id: str) -> Dict:
        """
        Obtiene los roles y permisos actuales de un usuario
        """
        user = self.get_user(user_id)
        metadata = user.get("metadata", {})
        return {
            "roles": metadata.get("roles", []),
            "permissions": metadata.get("permissions", [])
        }

# Crear una instancia global
clerk_admin = ClerkAdmin()
