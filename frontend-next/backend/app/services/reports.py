from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pandas as pd
from io import BytesIO

from ..crud import payment as crud_payment
from ..crud import contract as crud_contract
from ..models.payment import Payment, PaymentStatus
from ..models.contract import Contract

class PaymentReportService:
    @staticmethod
    def generate_account_statement(
        db: Session,
        contract_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generar estado de cuenta para un contrato específico"""
        # Obtener todos los pagos del período
        payments = crud_payment.get_contract_payments(
            db,
            contract_id=contract_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Obtener información del contrato
        contract = crud_contract.get(db, id=contract_id)
        
        # Calcular totales
        total_paid = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
        total_pending = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
        total_late = sum(p.amount for p in payments if p.status == PaymentStatus.LATE)
        total_late_fees = sum(p.late_fee for p in payments)
        
        # Organizar pagos por estado
        payments_by_status = {
            "paid": [p for p in payments if p.status == PaymentStatus.PAID],
            "pending": [p for p in payments if p.status == PaymentStatus.PENDING],
            "late": [p for p in payments if p.status == PaymentStatus.LATE]
        }
        
        return {
            "contract_info": {
                "contract_number": contract.contract_number,
                "tenant_name": contract.tenant.full_name,
                "property": contract.unit.property.name,
                "unit": contract.unit.unit_number,
                "rent_amount": contract.rent_amount
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_paid": total_paid,
                "total_pending": total_pending,
                "total_late": total_late,
                "total_late_fees": total_late_fees,
                "total_balance": total_pending + total_late + total_late_fees
            },
            "payments": payments_by_status
        }

    @staticmethod
    def generate_payment_history(
        db: Session,
        contract_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Generar historial detallado de pagos"""
        payments = crud_payment.get_contract_payments(
            db,
            contract_id=contract_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [{
            "payment_id": p.id,
            "date": p.payment_date,
            "concept": p.concept.value,
            "amount": p.amount,
            "status": p.status.value,
            "payment_method": p.payment_method.value if p.payment_method else None,
            "reference": p.reference_number,
            "late_fee": p.late_fee,
            "processed_by": p.processed_by.full_name if p.processed_by else None
        } for p in payments]

    @staticmethod
    def generate_late_payments_report(
        db: Session,
        property_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generar reporte de pagos atrasados"""
        query = db.query(Payment).filter(Payment.status == PaymentStatus.LATE)
        
        if property_id:
            query = query.join(Contract).filter(Contract.property_id == property_id)
        
        late_payments = query.all()
        
        return [{
            "payment_id": p.id,
            "contract_number": p.contract.contract_number,
            "tenant_name": p.contract.tenant.full_name,
            "property": p.contract.unit.property.name,
            "unit": p.contract.unit.unit_number,
            "amount": p.amount,
            "due_date": p.due_date,
            "days_late": (date.today() - p.due_date).days,
            "late_fee": p.late_fee
        } for p in late_payments]

    @staticmethod
    def generate_payment_analytics(
        db: Session,
        property_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generar análisis de pagos y tendencias"""
        query = db.query(Payment)
        
        if property_id:
            query = query.join(Contract).filter(Contract.property_id == property_id)
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        payments = query.all()
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame([{
            "payment_date": p.payment_date,
            "amount": p.amount,
            "status": p.status.value,
            "late_fee": p.late_fee,
            "concept": p.concept.value
        } for p in payments])
        
        if df.empty:
            return {
                "total_payments": 0,
                "payment_trends": [],
                "status_distribution": {},
                "concept_distribution": {},
                "late_fee_analysis": {
                    "total": 0,
                    "average": 0
                }
            }
        
        # Análisis por mes
        df["month"] = pd.to_datetime(df["payment_date"]).dt.to_period("M")
        monthly_trends = df.groupby("month").agg({
            "amount": "sum",
            "payment_date": "count"
        }).reset_index()
        
        monthly_trends = [{
            "month": str(month),
            "total_amount": row["amount"],
            "payment_count": row["payment_date"]
        } for month, row in monthly_trends.iterrows()]
        
        # Distribución por estado
        status_dist = df["status"].value_counts().to_dict()
        
        # Distribución por concepto
        concept_dist = df["concept"].value_counts().to_dict()
        
        # Análisis de pagos tardíos
        late_payments = df[df["status"] == "late"]
        late_fee_total = late_payments["late_fee"].sum()
        late_fee_avg = late_payments["late_fee"].mean() if not late_payments.empty else 0
        
        return {
            "total_payments": len(payments),
            "payment_trends": monthly_trends,
            "status_distribution": status_dist,
            "concept_distribution": concept_dist,
            "late_fee_analysis": {
                "total": late_fee_total,
                "average": late_fee_avg
            }
        }

    @staticmethod
    def export_to_excel(
        db: Session,
        data: List[Dict[str, Any]],
        sheet_name: str = "Payments Report"
    ) -> BytesIO:
        """Exportar datos a Excel"""
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.set_column(i, i, max_length + 2)
        
        output.seek(0)
        return output
