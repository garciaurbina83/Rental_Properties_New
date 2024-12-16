from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..crud import payment as crud_payment
from ..crud import contract as crud_contract
from ..crud import tenant as crud_tenant
from ..crud import property as crud_property
from ..models.payment import Payment, PaymentStatus
from ..models.contract import Contract
from ..models.property import Property
from ..models.unit import Unit

class ContractIntegrationService:
    @staticmethod
    def update_contract_payment_status(
        db: Session,
        contract_id: int
    ) -> Dict[str, Any]:
        """
        Actualizar el estado de pagos de un contrato y calcular métricas
        """
        # Obtener todos los pagos del contrato
        payments = crud_payment.get_contract_payments(db, contract_id=contract_id)
        contract = crud_contract.get(db, id=contract_id)
        
        if not contract:
            return None
        
        # Calcular métricas
        total_paid = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
        total_pending = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
        total_late = sum(p.amount for p in payments if p.status == PaymentStatus.LATE)
        
        # Calcular porcentaje de pagos a tiempo
        total_payments = len([p for p in payments if p.status == PaymentStatus.PAID])
        late_payments = len([p for p in payments if p.status == PaymentStatus.LATE])
        on_time_percentage = ((total_payments - late_payments) / total_payments * 100) if total_payments > 0 else 100
        
        return {
            "contract_id": contract_id,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_late": total_late,
            "on_time_payment_percentage": on_time_percentage,
            "payment_status": "good" if on_time_percentage >= 80 else "warning" if on_time_percentage >= 60 else "bad"
        }

class TenantIntegrationService:
    @staticmethod
    def get_tenant_payment_history(
        db: Session,
        tenant_id: int
    ) -> Dict[str, Any]:
        """
        Obtener historial completo de pagos de un inquilino
        a través de todos sus contratos
        """
        tenant = crud_tenant.get(db, id=tenant_id)
        if not tenant:
            return None
        
        # Obtener todos los contratos del inquilino
        contracts = db.query(Contract).filter(Contract.tenant_id == tenant_id).all()
        
        payment_history = []
        total_stats = {
            "total_paid": 0,
            "total_pending": 0,
            "total_late": 0,
            "total_late_fees": 0,
            "contracts_count": len(contracts),
            "on_time_payments": 0,
            "late_payments": 0
        }
        
        for contract in contracts:
            payments = crud_payment.get_contract_payments(db, contract_id=contract.id)
            
            for payment in payments:
                payment_history.append({
                    "contract_number": contract.contract_number,
                    "payment_date": payment.payment_date,
                    "amount": payment.amount,
                    "status": payment.status.value,
                    "late_fee": payment.late_fee
                })
                
                if payment.status == PaymentStatus.PAID:
                    total_stats["total_paid"] += payment.amount
                    if payment.payment_date and payment.payment_date <= payment.due_date:
                        total_stats["on_time_payments"] += 1
                elif payment.status == PaymentStatus.PENDING:
                    total_stats["total_pending"] += payment.amount
                elif payment.status == PaymentStatus.LATE:
                    total_stats["total_late"] += payment.amount
                    total_stats["late_payments"] += 1
                
                total_stats["total_late_fees"] += payment.late_fee
        
        total_payments = total_stats["on_time_payments"] + total_stats["late_payments"]
        payment_reliability = (total_stats["on_time_payments"] / total_payments * 100) if total_payments > 0 else 100
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.full_name,
            "payment_history": payment_history,
            "statistics": total_stats,
            "payment_reliability_score": payment_reliability
        }

class PropertyIntegrationService:
    @staticmethod
    def calculate_property_income(
        db: Session,
        property_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcular ingresos y métricas financieras de una propiedad
        """
        property = crud_property.get(db, id=property_id)
        if not property:
            return None
        
        # Obtener unidades y contratos asociados
        units = db.query(Unit).filter(Unit.property_id == property_id).all()
        unit_ids = [unit.id for unit in units]
        
        contracts = db.query(Contract).filter(Contract.unit_id.in_(unit_ids)).all()
        contract_ids = [contract.id for contract in contracts]
        
        # Base query para pagos
        query = db.query(Payment).filter(Payment.contract_id.in_(contract_ids))
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        payments = query.all()
        
        # Calcular métricas
        total_income = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
        pending_income = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
        late_payments = sum(p.amount for p in payments if p.status == PaymentStatus.LATE)
        late_fees = sum(p.late_fee for p in payments)
        
        # Calcular ocupación
        total_units = len(units)
        occupied_units = len([c for c in contracts if c.is_active])
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        # Calcular ingresos por unidad
        unit_income = {}
        for unit in units:
            unit_contracts = [c for c in contracts if c.unit_id == unit.id]
            unit_payments = [
                p for p in payments 
                if p.contract_id in [c.id for c in unit_contracts]
                and p.status == PaymentStatus.PAID
            ]
            unit_income[unit.unit_number] = sum(p.amount for p in unit_payments)
        
        return {
            "property_id": property_id,
            "property_name": property.name,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "financial_metrics": {
                "total_income": total_income,
                "pending_income": pending_income,
                "late_payments": late_payments,
                "late_fees_collected": late_fees,
                "total_revenue": total_income + late_fees
            },
            "occupancy_metrics": {
                "total_units": total_units,
                "occupied_units": occupied_units,
                "occupancy_rate": occupancy_rate
            },
            "unit_performance": unit_income,
            "income_per_unit": total_income / total_units if total_units > 0 else 0
        }
