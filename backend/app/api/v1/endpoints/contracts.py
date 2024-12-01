from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session

from ....core.deps import get_db
from ....services.contract_service import ContractService
from ....models.contract import ContractStatus, PaymentMethod
from ....schemas.contract import (
    Contract,
    ContractCreate,
    ContractUpdate,
    ContractWithDetails,
    Payment,
    PaymentCreate,
    ContractDocument,
    ContractDocumentCreate
)

router = APIRouter()

@router.post("/", response_model=Contract, status_code=201)
async def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db)
) -> Contract:
    """
    Crear un nuevo contrato.
    """
    return await ContractService.create_contract(db=db, contract=contract)

@router.get("/{contract_id}", response_model=ContractWithDetails)
async def get_contract(
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Obtener un contrato por su ID, incluyendo detalles del inquilino y la unidad.
    """
    return await ContractService.get_contract(db=db, contract_id=contract_id)

@router.get("/", response_model=List[Contract])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[ContractStatus] = Query(None, description="Filtrar por estado del contrato"),
    db: Session = Depends(get_db)
) -> List[Contract]:
    """
    Listar contratos con paginación y filtros opcionales.
    """
    return await ContractService.get_contracts(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )

@router.put("/{contract_id}", response_model=Contract)
async def update_contract(
    contract_update: ContractUpdate,
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Actualizar información de un contrato.
    """
    return await ContractService.update_contract(
        db=db,
        contract_id=contract_id,
        contract_update=contract_update
    )

@router.post("/{contract_id}/terminate", response_model=Contract)
async def terminate_contract(
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    termination_date: date = Body(...),
    termination_notes: Optional[str] = Body(None),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Terminar un contrato activo.
    """
    return await ContractService.terminate_contract(
        db=db,
        contract_id=contract_id,
        termination_date=termination_date,
        termination_notes=termination_notes
    )

@router.post("/{contract_id}/renew", response_model=Contract)
async def renew_contract(
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    new_end_date: date = Body(...),
    new_rent_amount: Optional[float] = Body(None),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Renovar un contrato activo.
    """
    return await ContractService.renew_contract(
        db=db,
        contract_id=contract_id,
        new_end_date=new_end_date,
        new_rent_amount=new_rent_amount
    )

@router.post("/{contract_id}/payments", response_model=Payment)
async def add_payment(
    payment: PaymentCreate,
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Payment:
    """
    Registrar un nuevo pago para un contrato.
    """
    return await ContractService.add_payment(
        db=db,
        contract_id=contract_id,
        payment=payment
    )

@router.get("/{contract_id}/payments", response_model=List[Payment])
async def list_contract_payments(
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Payment]:
    """
    Listar todos los pagos de un contrato.
    """
    return await ContractService.get_contract_payments(
        db=db,
        contract_id=contract_id,
        skip=skip,
        limit=limit
    )

@router.post("/{contract_id}/documents", response_model=ContractDocument)
async def add_contract_document(
    document: ContractDocumentCreate,
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> ContractDocument:
    """
    Agregar un documento a un contrato.
    """
    return await ContractService.add_contract_document(
        db=db,
        contract_id=contract_id,
        document=document
    )

@router.get("/tenant/{tenant_id}", response_model=List[Contract])
async def get_tenant_contracts(
    tenant_id: int = Path(..., title="ID del inquilino", ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Contract]:
    """
    Obtener todos los contratos de un inquilino.
    """
    return await ContractService.get_contracts_by_tenant(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )

@router.get("/unit/{unit_id}", response_model=List[Contract])
async def get_unit_contracts(
    unit_id: int = Path(..., title="ID de la unidad", ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Contract]:
    """
    Obtener todos los contratos de una unidad.
    """
    return await ContractService.get_contracts_by_unit(
        db=db,
        unit_id=unit_id,
        skip=skip,
        limit=limit
    )

@router.post("/{contract_id}/deposit-refund", response_model=Contract)
async def process_deposit_refund(
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    deductions: float = Body(..., ge=0, description="Monto a deducir del depósito"),
    deduction_reason: str = Body(..., min_length=1, description="Razón de las deducciones"),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Procesar la devolución del depósito de garantía de un contrato.
    """
    return await ContractService.process_deposit_refund(
        db=db,
        contract_id=contract_id,
        deductions=deductions,
        deduction_reason=deduction_reason
    )

@router.put("/{contract_id}/guarantor", response_model=Contract)
async def update_contract_guarantor(
    guarantor_info: dict = Body(...),
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Actualizar la información del garante de un contrato.
    """
    return await ContractService.update_guarantor_info(
        db=db,
        contract_id=contract_id,
        guarantor_info=guarantor_info
    )

@router.put("/{contract_id}/utilities", response_model=Contract)
async def update_contract_utilities(
    utilities_included: dict = Body(...),
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Actualizar los servicios incluidos en un contrato.
    """
    return await ContractService.update_utilities(
        db=db,
        contract_id=contract_id,
        utilities_included=utilities_included
    )

@router.put("/{contract_id}/payment-method", response_model=Contract)
async def update_contract_payment_method(
    payment_method: PaymentMethod,
    contract_id: int = Path(..., title="ID del contrato", ge=1),
    db: Session = Depends(get_db)
) -> Contract:
    """
    Actualizar el método de pago de un contrato.
    """
    return await ContractService.update_payment_method(
        db=db,
        contract_id=contract_id,
        payment_method=payment_method
    )
