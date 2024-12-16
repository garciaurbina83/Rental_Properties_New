from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.deps import get_db, get_current_active_superuser, get_current_active_user
from ....schemas.audit import AuditLogCreate, AuditLogResponse
from ....services.audit import AuditService
from ....models.user import User

router = APIRouter()

@router.get("/resource-history/{resource_type}/{resource_id}", response_model=List[AuditLogResponse])
def get_resource_history(
    resource_type: str,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener historial de cambios de un recurso específico
    """
    return AuditService.get_resource_history(db, resource_type, resource_id)

@router.get("/user-actions/{user_id}", response_model=List[AuditLogResponse])
def get_user_actions(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Obtener acciones realizadas por un usuario (solo superusuarios)
    """
    return AuditService.get_user_actions(db, user_id, start_date, end_date)

@router.get("/sensitive-operations", response_model=List[AuditLogResponse])
def get_sensitive_operations(
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Obtener operaciones sensibles (solo superusuarios)
    """
    return AuditService.get_sensitive_operations(
        db,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
