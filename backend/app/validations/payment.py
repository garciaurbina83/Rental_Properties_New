from datetime import date, datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..crud import payment as crud_payment
from ..crud import contract as crud_contract
from ..models.payment import Payment, PaymentStatus
from ..schemas.payment import PaymentCreate, PaymentUpdate

def validate_payment_amount(amount: float):
    """Validar que el monto sea positivo"""
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be positive"
        )

def validate_payment_dates(
    due_date: date,
    payment_date: Optional[date] = None,
    payment_period_start: Optional[date] = None,
    payment_period_end: Optional[date] = None
):
    """Validar fechas relacionadas con el pago"""
    today = date.today()
    
    # Validar fecha de vencimiento
    if due_date < today:
        raise HTTPException(
            status_code=400,
            detail="Due date cannot be in the past"
        )
    
    # Validar fecha de pago si está presente
    if payment_date and payment_date > today:
        raise HTTPException(
            status_code=400,
            detail="Payment date cannot be in the future"
        )
    
    # Validar período de pago si está presente
    if payment_period_start and payment_period_end:
        if payment_period_end < payment_period_start:
            raise HTTPException(
                status_code=400,
                detail="Payment period end date must be after start date"
            )

def validate_contract_status(db: Session, contract_id: int):
    """Validar que el contrato esté activo"""
    contract = crud_contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract with id {contract_id} not found"
        )
    
    today = date.today()
    if contract.end_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot create payment for an expired contract"
        )
    
    if not contract.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot create payment for an inactive contract"
        )

def validate_payment_against_contract(
    db: Session,
    contract_id: int,
    amount: float,
    payment_period_start: Optional[date] = None,
    payment_period_end: Optional[date] = None
):
    """Validar el monto del pago contra la renta establecida en el contrato"""
    contract = crud_contract.get(db, id=contract_id)
    
    # Validar que el monto no exceda significativamente la renta
    # (permitir un margen para cargos adicionales)
    if amount > contract.rent_amount * 2:
        raise HTTPException(
            status_code=400,
            detail="Payment amount significantly exceeds contract rent amount"
        )
    
    # Si se especifica período, validar que corresponda con el período del contrato
    if payment_period_start and payment_period_end:
        if payment_period_start < contract.start_date or payment_period_end > contract.end_date:
            raise HTTPException(
                status_code=400,
                detail="Payment period must be within contract dates"
            )

def validate_duplicate_payment(
    db: Session,
    contract_id: int,
    payment_period_start: Optional[date],
    payment_period_end: Optional[date],
    exclude_payment_id: Optional[int] = None
):
    """Validar que no exista un pago duplicado para el mismo período"""
    if not (payment_period_start and payment_period_end):
        return
    
    existing_payments = crud_payment.get_contract_payments(
        db,
        contract_id=contract_id,
        start_date=payment_period_start,
        end_date=payment_period_end
    )
    
    for payment in existing_payments:
        if payment.id != exclude_payment_id and payment.status != PaymentStatus.CANCELLED:
            raise HTTPException(
                status_code=400,
                detail="A payment for this period already exists"
            )

def validate_payment_sequence(
    db: Session,
    contract_id: int,
    payment_period_start: date,
    payment_period_end: date
):
    """Validar la secuencia de pagos (que no haya gaps significativos)"""
    # Obtener el último pago del contrato
    payments = crud_payment.get_contract_payments(
        db,
        contract_id=contract_id
    )
    
    if payments:
        last_payment = max(
            payments,
            key=lambda p: p.payment_period_end if p.payment_period_end else date.min
        )
        
        # Si hay un gap de más de un mes entre el último pago y este
        if (payment_period_start - last_payment.payment_period_end).days > 45:
            raise HTTPException(
                status_code=400,
                detail="Warning: Large gap detected between payments"
            )

def validate_payment_create(
    db: Session,
    payment_in: PaymentCreate
):
    """Validación completa para la creación de un pago"""
    # Validaciones básicas
    validate_payment_amount(payment_in.amount)
    validate_payment_dates(
        payment_in.due_date,
        payment_in.payment_date,
        payment_in.payment_period_start,
        payment_in.payment_period_end
    )
    
    # Validaciones de negocio
    validate_contract_status(db, payment_in.contract_id)
    validate_payment_against_contract(
        db,
        payment_in.contract_id,
        payment_in.amount,
        payment_in.payment_period_start,
        payment_in.payment_period_end
    )
    validate_duplicate_payment(
        db,
        payment_in.contract_id,
        payment_in.payment_period_start,
        payment_in.payment_period_end
    )
    
    if payment_in.payment_period_start and payment_in.payment_period_end:
        validate_payment_sequence(
            db,
            payment_in.contract_id,
            payment_in.payment_period_start,
            payment_in.payment_period_end
        )

def validate_payment_update(
    db: Session,
    payment_id: int,
    payment_in: PaymentUpdate
):
    """Validación completa para la actualización de un pago"""
    # Obtener el pago existente
    existing_payment = crud_payment.get(db, id=payment_id)
    if not existing_payment:
        raise HTTPException(
            status_code=404,
            detail=f"Payment with id {payment_id} not found"
        )
    
    # Validar cambios en el monto si se proporciona
    if payment_in.amount is not None:
        validate_payment_amount(payment_in.amount)
    
    # Validar fechas si se proporcionan
    if any([payment_in.due_date, payment_in.payment_date,
            payment_in.payment_period_start, payment_in.payment_period_end]):
        validate_payment_dates(
            payment_in.due_date or existing_payment.due_date,
            payment_in.payment_date,
            payment_in.payment_period_start,
            payment_in.payment_period_end
        )
    
    # Validar contra el contrato si hay cambios relevantes
    if payment_in.amount is not None or payment_in.payment_period_start is not None:
        validate_payment_against_contract(
            db,
            existing_payment.contract_id,
            payment_in.amount or existing_payment.amount,
            payment_in.payment_period_start or existing_payment.payment_period_start,
            payment_in.payment_period_end or existing_payment.payment_period_end
        )
    
    # Validar duplicados si hay cambios en el período
    if payment_in.payment_period_start is not None or payment_in.payment_period_end is not None:
        validate_duplicate_payment(
            db,
            existing_payment.contract_id,
            payment_in.payment_period_start or existing_payment.payment_period_start,
            payment_in.payment_period_end or existing_payment.payment_period_end,
            exclude_payment_id=payment_id
        )
