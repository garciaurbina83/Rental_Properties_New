from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.loan import (
    Loan, LoanCreate, LoanUpdate, LoanDetail,
    LoanDocument, LoanDocumentCreate,
    LoanPayment, LoanPaymentCreate,
    LoanSummary, AmortizationEntry
)
from app.models import LoanStatus, PaymentStatus
from app.services.loan_service import LoanService
from app.services.loan_payment_service import LoanPaymentService
from app.core.exceptions import NotFoundException, ValidationError

router = APIRouter()

@router.post("/", response_model=Loan)
async def create_loan(
    loan_data: LoanCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Crear un nuevo préstamo"""
    try:
        return await LoanService.create_loan(db, loan_data, current_user.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Loan])
async def get_loans(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    status: Optional[LoanStatus] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Obtener lista de préstamos con filtros opcionales"""
    return await LoanService.get_loans(db, skip, limit, property_id, status)

@router.get("/{loan_id}", response_model=LoanDetail)
async def get_loan(
    loan_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Obtener detalles de un préstamo específico"""
    loan = await LoanService.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan

@router.put("/{loan_id}", response_model=Loan)
async def update_loan(
    loan_id: int,
    loan_data: LoanUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Actualizar un préstamo existente"""
    try:
        return await LoanService.update_loan(db, loan_id, loan_data, current_user.id)
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(status_code=404 if isinstance(e, NotFoundException) else 400, detail=str(e))

@router.post("/{loan_id}/documents", response_model=LoanDocument)
async def add_loan_document(
    loan_id: int,
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Añadir un documento al préstamo"""
    try:
        # Guardar el archivo
        file_path = f"loans/{loan_id}/documents/{file.filename}"
        # TODO: Implementar el guardado real del archivo
        
        document_data = LoanDocumentCreate(
            document_type=document_type,
            file_path=file_path,
            description=description
        )
        
        return await LoanService.add_document(db, loan_id, document_data, current_user.id)
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(status_code=404 if isinstance(e, NotFoundException) else 400, detail=str(e))

@router.post("/{loan_id}/documents/{document_id}/verify", response_model=LoanDocument)
async def verify_loan_document(
    loan_id: int,
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Verificar un documento de préstamo"""
    try:
        return await LoanService.verify_document(db, document_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{loan_id}/summary", response_model=LoanSummary)
async def get_loan_summary(
    loan_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Obtener resumen del préstamo con información de pagos"""
    try:
        return await LoanService.get_loan_summary(db, loan_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{loan_id}/amortization", response_model=List[AmortizationEntry])
async def get_amortization_schedule(
    loan_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Obtener tabla de amortización del préstamo"""
    try:
        return await LoanService.generate_amortization_schedule(db, loan_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{loan_id}/payments", response_model=LoanPayment)
async def create_loan_payment(
    loan_id: int,
    payment_data: LoanPaymentCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Registrar un nuevo pago de préstamo"""
    try:
        return await LoanPaymentService.create_payment(db, loan_id, payment_data, current_user.id)
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(status_code=404 if isinstance(e, NotFoundException) else 400, detail=str(e))

@router.post("/{loan_id}/payments/{payment_id}/process", response_model=LoanPayment)
async def process_loan_payment(
    loan_id: int,
    payment_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Procesar un pago pendiente"""
    try:
        return await LoanPaymentService.process_payment(db, payment_id, current_user.id)
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(status_code=404 if isinstance(e, NotFoundException) else 400, detail=str(e))

@router.get("/{loan_id}/payments", response_model=List[LoanPayment])
async def get_loan_payments(
    loan_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[PaymentStatus] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Obtener pagos de un préstamo con filtros opcionales"""
    return await LoanPaymentService.get_loan_payments(db, loan_id, skip, limit, status)

@router.post("/{loan_id}/payments/{payment_id}/cancel", response_model=LoanPayment)
async def cancel_loan_payment(
    loan_id: int,
    payment_id: int,
    cancellation_reason: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Cancelar un pago pendiente"""
    try:
        return await LoanPaymentService.cancel_payment(
            db, payment_id, current_user.id, cancellation_reason
        )
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(status_code=404 if isinstance(e, NotFoundException) else 400, detail=str(e))
