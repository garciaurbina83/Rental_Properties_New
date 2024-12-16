from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import pandas as pd
from app.models import Loan, LoanPayment, PaymentStatus, LoanStatus
from app.core.exceptions import ValidationError
import json
import os
from app.core.config import settings

class LoanReportService:
    @staticmethod
    async def generate_monthly_report(
        db: Session,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generar reporte mensual de préstamos"""
        # Si no se especifica mes/año, usar el mes actual
        if not month or not year:
            today = date.today()
            month = today.month
            year = today.year

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Obtener todos los pagos del mes
        payments = await db.query(LoanPayment).filter(
            and_(
                LoanPayment.payment_date >= start_date,
                LoanPayment.payment_date < end_date
            )
        ).all()

        # Obtener todos los préstamos activos
        loans = await db.query(Loan).filter(
            or_(
                Loan.status == LoanStatus.ACTIVE,
                Loan.status == LoanStatus.DEFAULT
            )
        ).all()

        # Calcular estadísticas generales
        total_loans = len(loans)
        active_loans = len([l for l in loans if l.status == LoanStatus.ACTIVE])
        defaulted_loans = len([l for l in loans if l.status == LoanStatus.DEFAULT])
        
        # Análisis de pagos
        total_payments = len(payments)
        completed_payments = len([p for p in payments if p.status == PaymentStatus.COMPLETED])
        late_payments = len([p for p in payments if p.status == PaymentStatus.LATE])
        
        # Análisis financiero
        total_amount_paid = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
        total_principal_paid = sum(p.principal_amount for p in payments if p.status == PaymentStatus.COMPLETED)
        total_interest_paid = sum(p.interest_amount for p in payments if p.status == PaymentStatus.COMPLETED)
        total_late_fees = sum(p.late_fee for p in payments if p.status == PaymentStatus.COMPLETED)
        
        # Calcular morosidad
        total_overdue = sum(l.remaining_balance for l in loans if l.status == LoanStatus.DEFAULT)
        delinquency_rate = (defaulted_loans / total_loans * 100) if total_loans > 0 else 0
        
        # Proyección de pagos para el próximo mes
        next_month_payments = await LoanReportService.calculate_next_month_projection(db, loans)
        
        report = {
            "period": {
                "month": month,
                "year": year,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "loan_summary": {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "defaulted_loans": defaulted_loans,
                "delinquency_rate": round(delinquency_rate, 2)
            },
            "payment_analysis": {
                "total_payments": total_payments,
                "completed_payments": completed_payments,
                "late_payments": late_payments,
                "on_time_rate": round((completed_payments / total_payments * 100) if total_payments > 0 else 0, 2)
            },
            "financial_summary": {
                "total_amount_paid": round(total_amount_paid, 2),
                "total_principal_paid": round(total_principal_paid, 2),
                "total_interest_paid": round(total_interest_paid, 2),
                "total_late_fees": round(total_late_fees, 2),
                "total_overdue": round(total_overdue, 2)
            },
            "next_month_projection": next_month_payments,
            "top_defaulters": await LoanReportService.get_top_defaulters(db, limit=5)
        }

        # Guardar reporte en archivo
        await LoanReportService.save_report(report, month, year)
        
        return report

    @staticmethod
    async def calculate_next_month_projection(
        db: Session,
        loans: List[Loan]
    ) -> Dict[str, float]:
        """Calcular proyección de pagos para el próximo mes"""
        next_month = date.today().replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        
        expected_principal = 0
        expected_interest = 0
        expected_late_fees = 0
        
        for loan in loans:
            if loan.status != LoanStatus.PAID:
                # Calcular próximo pago basado en amortización
                r = loan.interest_rate / 12 / 100
                expected_interest += loan.remaining_balance * r
                expected_principal += loan.monthly_payment - (loan.remaining_balance * r)
                
                # Si está en default, agregar multas esperadas
                if loan.status == LoanStatus.DEFAULT:
                    expected_late_fees += loan.monthly_payment * 0.05  # 5% de multa base
        
        return {
            "expected_principal": round(expected_principal, 2),
            "expected_interest": round(expected_interest, 2),
            "expected_late_fees": round(expected_late_fees, 2),
            "total_expected": round(expected_principal + expected_interest + expected_late_fees, 2)
        }

    @staticmethod
    async def get_top_defaulters(
        db: Session,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Obtener los préstamos con mayor morosidad"""
        defaulted_loans = await db.query(Loan).filter(
            Loan.status == LoanStatus.DEFAULT
        ).order_by(Loan.remaining_balance.desc()).limit(limit).all()
        
        return [{
            "loan_id": loan.id,
            "remaining_balance": round(loan.remaining_balance, 2),
            "days_overdue": (date.today() - loan.last_payment_date).days if loan.last_payment_date else 0,
            "original_amount": loan.principal_amount
        } for loan in defaulted_loans]

    @staticmethod
    async def save_report(
        report: Dict[str, Any],
        month: int,
        year: int
    ) -> str:
        """Guardar reporte en archivo"""
        reports_dir = os.path.join(settings.REPORTS_DIR, str(year))
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"loan_report_{year}_{month:02d}.json"
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath

    @staticmethod
    async def generate_loan_performance_metrics(
        db: Session,
        loan_id: int
    ) -> Dict[str, Any]:
        """Generar métricas de rendimiento para un préstamo específico"""
        loan = await db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise ValidationError(f"Préstamo {loan_id} no encontrado")

        payments = await db.query(LoanPayment).filter(
            LoanPayment.loan_id == loan_id
        ).all()

        # Calcular métricas
        total_paid = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
        total_late_fees = sum(p.late_fee for p in payments if p.status == PaymentStatus.COMPLETED)
        completed_payments = len([p for p in payments if p.status == PaymentStatus.COMPLETED])
        late_payments = len([p for p in payments if p.status == PaymentStatus.LATE])
        
        # Calcular tasa de pagos a tiempo
        on_time_rate = (completed_payments - late_payments) / completed_payments * 100 if completed_payments > 0 else 0
        
        # Calcular progreso del préstamo
        progress = (loan.principal_amount - loan.remaining_balance) / loan.principal_amount * 100
        
        return {
            "loan_id": loan_id,
            "metrics": {
                "total_paid": round(total_paid, 2),
                "total_late_fees": round(total_late_fees, 2),
                "completed_payments": completed_payments,
                "late_payments": late_payments,
                "on_time_payment_rate": round(on_time_rate, 2),
                "loan_progress": round(progress, 2)
            },
            "status": {
                "current_status": loan.status.value,
                "remaining_balance": round(loan.remaining_balance, 2),
                "next_payment_date": loan.next_payment_date.isoformat() if loan.next_payment_date else None
            }
        }
