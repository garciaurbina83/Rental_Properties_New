from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from ....core.deps import get_db, get_current_user
from ....services.integrations import (
    ContractIntegrationService,
    TenantIntegrationService,
    PropertyIntegrationService
)
from ....schemas.user import User

router = APIRouter()

@router.get("/contracts/{contract_id}/payment-status")
def get_contract_payment_status(
    contract_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener estado y métricas de pago de un contrato.
    """
    status = ContractIntegrationService.update_contract_payment_status(
        db,
        contract_id
    )
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Contract with id {contract_id} not found"
        )
    
    return status

@router.get("/tenants/{tenant_id}/payment-profile")
def get_tenant_payment_profile(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener perfil completo de pagos de un inquilino.
    """
    profile = TenantIntegrationService.get_tenant_payment_history(
        db,
        tenant_id
    )
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant with id {tenant_id} not found"
        )
    
    return profile

@router.get("/properties/{property_id}/financial-metrics")
def get_property_financial_metrics(
    property_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener métricas financieras de una propiedad.
    """
    metrics = PropertyIntegrationService.calculate_property_income(
        db,
        property_id,
        start_date,
        end_date
    )
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Property with id {property_id} not found"
        )
    
    return metrics
