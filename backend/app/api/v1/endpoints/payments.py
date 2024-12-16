from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from datetime import date

from ....core.deps import get_db, get_current_user
from ....crud import payment as crud_payment
from ....crud import contract as crud_contract
from ....schemas.payment import (
    Payment,
    PaymentCreate,
    PaymentUpdate,
    PaymentDetail,
    PaymentStatus,
    PaymentResponse
)
from ....schemas.user import User
from ....models.payment import PaymentConcept
from ....validations.payment import validate_payment_create, validate_payment_update
from ....services.notifications import NotificationService, schedule_payment_reminders
from ....services.audit import AuditService

router = APIRouter()

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_user),
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Crear un nuevo pago.
    """
    # Validaciones completas
    validate_payment_create(db, payment_in)
    
    # Crear el pago con el usuario que lo procesa
    payment_data = payment_in.model_dump()
    payment_data["processed_by_id"] = current_user.id
    payment = crud_payment.create(db, obj_in=payment_data)
    
    # Enviar confirmación de pago si ya está pagado
    if payment.status == PaymentStatus.PAID:
        background_tasks.add_task(
            NotificationService.send_payment_confirmation,
            db,
            payment.id
        )
    
    # Registrar en auditoría
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        resource_type="payment",
        resource_id=payment.id,
        new_values=payment_in.dict(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return payment

@router.get("/", response_model=List[PaymentDetail])
def list_payments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    contract_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    concept: Optional[PaymentConcept] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    _: User = Depends(get_current_user)
):
    """
    Listar pagos con filtros opcionales.
    """
    filters = {}
    if contract_id:
        filters["contract_id"] = contract_id
    if status:
        filters["status"] = status
    if concept:
        filters["concept"] = concept
    if start_date:
        filters["payment_date__gte"] = start_date
    if end_date:
        filters["payment_date__lte"] = end_date
    
    return crud_payment.get_multi(db, skip=skip, limit=limit, filters=filters)

@router.get("/{payment_id}", response_model=PaymentDetail)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener un pago específico por ID.
    """
    payment = crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=404,
            detail=f"Payment with id {payment_id} not found"
        )
    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    payment_in: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Actualizar un pago existente.
    """
    # Obtener el pago actual para comparar cambios
    current_payment = crud_payment.get(db, id=payment_id)
    if not current_payment:
        raise HTTPException(
            status_code=404,
            detail=f"Payment with id {payment_id} not found"
        )
    
    # Validaciones completas
    validate_payment_update(db, payment_id, payment_in)
    
    # Actualizar el pago
    payment_data = payment_in.model_dump(exclude_unset=True)
    payment_data["processed_by_id"] = current_user.id
    updated_payment = crud_payment.update(db, db_obj=current_payment, obj_in=payment_data)
    
    # Enviar notificaciones según los cambios
    if payment_in.status:
        if payment_in.status == PaymentStatus.PAID and current_payment.status != PaymentStatus.PAID:
            # Si el pago cambió a PAID, enviar confirmación
            background_tasks.add_task(
                NotificationService.send_payment_confirmation,
                db,
                payment_id
            )
        elif payment_in.status == PaymentStatus.LATE and current_payment.status != PaymentStatus.LATE:
            # Si el pago cambió a LATE, enviar alerta
            background_tasks.add_task(
                NotificationService.send_late_payment_alert,
                db,
                payment_id
            )
    
    # Registrar en auditoría
    old_values = {
        field: getattr(current_payment, field)
        for field in payment_in.dict(exclude_unset=True).keys()
    }
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        resource_type="payment",
        resource_id=payment_id,
        old_values=old_values,
        new_values=payment_in.dict(exclude_unset=True),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return updated_payment

@router.delete("/{payment_id}", response_model=PaymentResponse)
def delete_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    current_user: User = Depends(get_current_user),
    request: Request
):
    """
    Eliminar un pago.
    """
    payment = crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=404,
            detail=f"Payment with id {payment_id} not found"
        )
    
    old_values = payment.__dict__
    payment = crud_payment.remove(db, id=payment_id)
    
    # Registrar en auditoría
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        resource_type="payment",
        resource_id=payment_id,
        old_values=old_values,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return payment

@router.get("/contract/{contract_id}/summary")
def get_contract_payments_summary(
    contract_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener un resumen de los pagos de un contrato específico.
    """
    # Verificar que el contrato existe
    contract = crud_contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract with id {contract_id} not found"
        )
    
    # Obtener todos los pagos del contrato
    payments = crud_payment.get_multi(
        db,
        filters={"contract_id": contract_id}
    )
    
    # Calcular estadísticas
    total_paid = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
    total_pending = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
    total_late = sum(p.amount for p in payments if p.status == PaymentStatus.LATE)
    total_late_fees = sum(p.late_fee for p in payments)
    
    return {
        "contract_id": contract_id,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "total_late": total_late,
        "total_late_fees": total_late_fees,
        "payment_count": len(payments),
        "late_payments_count": sum(1 for p in payments if p.status == PaymentStatus.LATE)
    }

@router.post("/schedule-reminders")
async def trigger_payment_reminders(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Programar recordatorios de pago.
    Este endpoint puede ser llamado por un cron job diariamente.
    """
    schedule_payment_reminders(db, background_tasks)
    return {"message": "Payment reminders scheduled successfully"}
