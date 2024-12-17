from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date

from ..crud.base import CRUDBase
from ..models.payment import Payment
from ..schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Payment]:
        """
        Obtener múltiples pagos con filtros opcionales.
        Los filtros soportados incluyen:
        - contract_id: ID del contrato
        - status: Estado del pago
        - concept: Concepto del pago
        - payment_date__gte: Fecha de pago mayor o igual que
        - payment_date__lte: Fecha de pago menor o igual que
        """
        query = db.query(self.model)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if key == "payment_date__gte":
                        conditions.append(self.model.payment_date >= value)
                    elif key == "payment_date__lte":
                        conditions.append(self.model.payment_date <= value)
                    else:
                        conditions.append(getattr(self.model, key) == value)
            
            if conditions:
                query = query.filter(and_(*conditions))
        
        return query.offset(skip).limit(limit).all()

    def get_contract_payments(
        self,
        db: Session,
        *,
        contract_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Payment]:
        """
        Obtener todos los pagos de un contrato específico,
        opcionalmente filtrados por rango de fechas.
        """
        query = db.query(self.model).filter(self.model.contract_id == contract_id)
        
        if start_date:
            query = query.filter(self.model.payment_date >= start_date)
        if end_date:
            query = query.filter(self.model.payment_date <= end_date)
        
        return query.all()

    def get_pending_payments(
        self,
        db: Session,
        *,
        contract_id: Optional[int] = None,
        due_before: Optional[date] = None
    ) -> List[Payment]:
        """
        Obtener pagos pendientes, opcionalmente filtrados por contrato
        y fecha de vencimiento.
        """
        from ..models.payment import PaymentStatus
        
        query = db.query(self.model).filter(
            self.model.status == PaymentStatus.PENDING
        )
        
        if contract_id:
            query = query.filter(self.model.contract_id == contract_id)
        if due_before:
            query = query.filter(self.model.due_date <= due_before)
        
        return query.all()

    def get_late_payments(
        self,
        db: Session,
        *,
        contract_id: Optional[int] = None
    ) -> List[Payment]:
        """
        Obtener pagos atrasados, opcionalmente filtrados por contrato.
        """
        from ..models.payment import PaymentStatus
        
        query = db.query(self.model).filter(
            self.model.status == PaymentStatus.LATE
        )
        
        if contract_id:
            query = query.filter(self.model.contract_id == contract_id)
        
        return query.all()

    def calculate_contract_balance(
        self,
        db: Session,
        *,
        contract_id: int
    ) -> Dict[str, float]:
        """
        Calcular el balance total de un contrato, incluyendo:
        - Total pagado
        - Total pendiente
        - Total en mora
        - Total de cargos por mora
        """
        from ..models.payment import PaymentStatus
        
        payments = self.get_contract_payments(db, contract_id=contract_id)
        
        total_paid = sum(
            p.amount for p in payments 
            if p.status == PaymentStatus.PAID
        )
        total_pending = sum(
            p.amount for p in payments 
            if p.status == PaymentStatus.PENDING
        )
        total_late = sum(
            p.amount for p in payments 
            if p.status == PaymentStatus.LATE
        )
        total_late_fees = sum(p.late_fee for p in payments)
        
        return {
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_late": total_late,
            "total_late_fees": total_late_fees,
            "total_balance": total_pending + total_late + total_late_fees
        }

payment = CRUDPayment(Payment)
