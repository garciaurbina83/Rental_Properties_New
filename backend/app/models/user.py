from sqlalchemy import Boolean, Column, Integer, String, Float, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.core.permissions import PermissionLevel, ROLE_PERMISSIONS

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    
    # Roles y permisos
    roles = Column(ARRAY(String), default=[])
    permissions = Column(ARRAY(String), default=[])
    approval_limit = Column(Float, nullable=True)  # Límite máximo para aprobar gastos
    
    # Relaciones
    expenses_created = relationship(
        "Expense",
        back_populates="created_by",
        foreign_keys="[Expense.created_by_id]"
    )
    expenses_approved = relationship(
        "Expense",
        back_populates="approved_by",
        foreign_keys="[Expense.approved_by]"
    )
    audit_logs = relationship("AuditLog", back_populates="user")

    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles or self.is_superuser

    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if user has specific permission."""
        if self.is_superuser:
            return True
            
        permission_value = permission.value
        # Check direct permissions
        if permission_value in self.permissions:
            return True
            
        # Check role-based permissions
        for role in self.roles:
            if role in ROLE_PERMISSIONS and permission_value in ROLE_PERMISSIONS[role]:
                return True
                
        return False

    def get_all_permissions(self) -> set[str]:
        """Get all permissions for user including role-based ones."""
        if self.is_superuser:
            return set(perm.value for perm in PermissionLevel)
            
        permissions = set(self.permissions)
        for role in self.roles:
            if role in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role])
                
        return permissions
