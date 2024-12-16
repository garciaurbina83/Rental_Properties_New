from typing import List, Optional, Dict
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from ..models.contract import Contract, ContractDocument, ContractStatus
from ..models.payment import Payment, PaymentMethod
from ..models.tenant import Tenant
from ..models.unit import Unit
from ..schemas.contract import ContractCreate, ContractUpdate, PaymentCreate, ContractDocumentCreate

class ContractService:
    @staticmethod
    async def validate_contract_dates(start_date: date, end_date: date):
        today = date.today()
        if start_date <= today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract start date must be in the future"
            )
        if end_date <= start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract end date must be after start date"
            )

    @staticmethod
    async def validate_contract_amounts(rent_amount: float, security_deposit: float):
        if rent_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rent amount must be greater than 0"
            )
        if security_deposit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security deposit must be greater than or equal to 0"
            )

    @staticmethod
    async def validate_guarantor_info(guarantor_info: Optional[Dict[str, str]]):
        if guarantor_info:
            required_fields = ["name", "contact", "address", "relationship"]
            missing_fields = [field for field in required_fields if field not in guarantor_info]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required guarantor information: {', '.join(missing_fields)}"
                )

    @staticmethod
    async def validate_required_documents(documents: Optional[List[ContractDocumentCreate]]):
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one document is required for the contract"
            )
        
        required_types = ["identification", "proof_of_income", "contract_agreement"]
        provided_types = [doc.document_type for doc in documents]
        missing_types = [doc_type for doc_type in required_types if doc_type not in provided_types]
        
        if missing_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required document types: {', '.join(missing_types)}"
            )

    @staticmethod
    async def validate_unit_availability(db: AsyncSession, unit_id: int, start_date: date, end_date: date):
        # Verificar contratos existentes que se superpongan con las fechas propuestas
        stmt = select(Contract).where(
            Contract.unit_id == unit_id,
            Contract.status.in_([ContractStatus.ACTIVE, ContractStatus.RENEWED]),
            Contract.end_date >= start_date,
            Contract.start_date <= end_date
        )
        result = await db.execute(stmt)
        existing_contract = result.scalar_one_or_none()
        
        if existing_contract:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit is not available for the specified period. There is an existing contract from {existing_contract.start_date} to {existing_contract.end_date}"
            )

    @staticmethod
    async def create_contract(db: AsyncSession, contract: ContractCreate) -> Contract:
        # Validar las fechas del contrato
        await ContractService.validate_contract_dates(contract.start_date, contract.end_date)
        
        # Validar los montos del contrato
        await ContractService.validate_contract_amounts(contract.rent_amount, contract.security_deposit)
        
        # Validar la información del garante si está presente
        await ContractService.validate_guarantor_info(contract.guarantor_info)
        
        # Validar los documentos requeridos
        await ContractService.validate_required_documents(contract.documents)

        # Verificar que el inquilino existe
        stmt = select(Tenant).where(Tenant.id == contract.tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # Verificar que la unidad existe
        stmt = select(Unit).where(Unit.id == contract.unit_id)
        result = await db.execute(stmt)
        unit = result.scalar_one_or_none()
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )

        # Verificar la disponibilidad de la unidad para el período solicitado
        await ContractService.validate_unit_availability(
            db, 
            contract.unit_id,
            contract.start_date,
            contract.end_date
        )

        # Crear el contrato
        new_contract = Contract(
            tenant_id=contract.tenant_id,
            unit_id=contract.unit_id,
            contract_number=contract.contract_number,
            status=contract.status,
            start_date=contract.start_date,
            end_date=contract.end_date,
            rent_amount=contract.rent_amount,
            security_deposit=contract.security_deposit,
            payment_frequency=contract.payment_frequency,
            payment_due_day=contract.payment_due_day,
            payment_method=contract.payment_method,
            utilities_included=contract.utilities_included,
            guarantor_info=contract.guarantor_info,
            terms_and_conditions=contract.terms_and_conditions,
            special_conditions=contract.special_conditions,
            is_renewable=contract.is_renewable,
            renewal_price_increase=contract.renewal_price_increase,
            auto_renewal=contract.auto_renewal
        )

        db.add(new_contract)
        await db.commit()
        await db.refresh(new_contract)

        # Crear documentos si existen
        if contract.documents:
            for document in contract.documents:
                db_document = ContractDocument(
                    **document.dict(),
                    contract_id=new_contract.id
                )
                db.add(db_document)
            await db.commit()

        return new_contract

    @staticmethod
    async def get_contract(db: AsyncSession, contract_id: int) -> Optional[Contract]:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_contracts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ContractStatus] = None
    ) -> List[Contract]:
        stmt = select(Contract)
        if status:
            stmt = stmt.where(Contract.status == status)
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_contract(
        db: AsyncSession,
        contract_id: int,
        contract_update: ContractUpdate
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        # No permitir cambios en contratos terminados
        if db_contract.status in [ContractStatus.TERMINATED, ContractStatus.EXPIRED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update terminated or expired contracts"
            )

        # Actualizar solo los campos proporcionados
        update_data = contract_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_contract, field, value)

        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def terminate_contract(
        db: AsyncSession,
        contract_id: int,
        termination_date: date,
        termination_notes: Optional[str] = None
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        if db_contract.status != ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active contracts can be terminated"
            )

        db_contract.status = ContractStatus.TERMINATED
        db_contract.end_date = termination_date
        if termination_notes:
            db_contract.notes = termination_notes

        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def renew_contract(
        db: AsyncSession,
        contract_id: int,
        new_end_date: date,
        new_rent_amount: Optional[float] = None
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        if not db_contract.is_renewable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract is not renewable"
            )

        if db_contract.status != ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active contracts can be renewed"
            )

        # Calcular nuevo monto de renta si no se proporciona
        if new_rent_amount is None and db_contract.renewal_price_increase:
            new_rent_amount = db_contract.rent_amount * (1 + db_contract.renewal_price_increase / 100)

        db_contract.end_date = new_end_date
        if new_rent_amount:
            db_contract.rent_amount = new_rent_amount
        db_contract.status = ContractStatus.RENEWED

        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def add_payment(
        db: AsyncSession,
        contract_id: int,
        payment: PaymentCreate
    ) -> Payment:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        if db_contract.status not in [ContractStatus.ACTIVE, ContractStatus.RENEWED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only add payments to active or renewed contracts"
            )

        db_payment = Payment(**payment.dict(), contract_id=contract_id)
        
        # Verificar si el pago es tardío
        if payment.payment_date > payment.due_date:
            db_payment.is_late = True
            # Aquí podrías implementar la lógica para calcular la multa por pago tardío

        db.add(db_payment)
        
        # Actualizar la fecha del último pago en el contrato
        db_contract.last_payment_date = payment.payment_date
        
        await db.commit()
        await db.refresh(db_payment)
        return db_payment

    @staticmethod
    async def add_contract_document(
        db: AsyncSession,
        contract_id: int,
        document: ContractDocumentCreate
    ) -> ContractDocument:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        db_document = ContractDocument(**document.dict(), contract_id=contract_id)
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)
        return db_document

    @staticmethod
    async def get_contract_payments(
        db: AsyncSession,
        contract_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        stmt = select(Payment).where(Payment.contract_id == contract_id)
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_contracts_by_tenant(
        db: AsyncSession,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contract]:
        stmt = select(Contract).where(Contract.tenant_id == tenant_id)
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_contracts_by_unit(
        db: AsyncSession,
        unit_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contract]:
        stmt = select(Contract).where(Contract.unit_id == unit_id)
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def process_deposit_refund(
        db: AsyncSession,
        contract_id: int,
        deductions: float,
        deduction_reason: str
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        if db_contract.status not in [ContractStatus.TERMINATED, ContractStatus.EXPIRED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only process deposit refund for terminated or expired contracts"
            )

        if db_contract.deposit_returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deposit has already been refunded"
            )

        if deductions < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deductions cannot be negative"
            )

        if deductions > db_contract.security_deposit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deductions cannot exceed security deposit amount"
            )

        db_contract.deposit_deductions = deductions
        db_contract.deposit_notes = deduction_reason
        db_contract.deposit_returned = True
        db_contract.deposit_return_date = date.today()

        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def update_guarantor_info(
        db: AsyncSession,
        contract_id: int,
        guarantor_info: dict
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        db_contract.guarantor_info = guarantor_info
        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def update_utilities(
        db: AsyncSession,
        contract_id: int,
        utilities_included: dict
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        db_contract.utilities_included = utilities_included
        await db.commit()
        await db.refresh(db_contract)
        return db_contract

    @staticmethod
    async def update_payment_method(
        db: AsyncSession,
        contract_id: int,
        payment_method: PaymentMethod
    ) -> Contract:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await db.execute(stmt)
        db_contract = result.scalar_one_or_none()

        if not db_contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

        db_contract.payment_method = payment_method
        await db.commit()
        await db.refresh(db_contract)
        return db_contract
