from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
import json

from ....core.deps import get_db, get_current_user
from ....services.reports import PaymentReportService
from ....schemas.user import User

router = APIRouter()

@router.get("/payments/account-statement/{contract_id}")
def get_account_statement(
    contract_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener estado de cuenta detallado para un contrato específico.
    """
    return PaymentReportService.generate_account_statement(
        db,
        contract_id,
        start_date,
        end_date
    )

@router.get("/payments/history/{contract_id}")
def get_payment_history(
    contract_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener historial detallado de pagos para un contrato.
    """
    return PaymentReportService.generate_payment_history(
        db,
        contract_id,
        start_date,
        end_date
    )

@router.get("/payments/late")
def get_late_payments_report(
    property_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener reporte de pagos atrasados, opcionalmente filtrado por propiedad.
    """
    return PaymentReportService.generate_late_payments_report(
        db,
        property_id
    )

@router.get("/payments/analytics")
def get_payment_analytics(
    property_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Obtener análisis detallado de pagos y tendencias.
    """
    return PaymentReportService.generate_payment_analytics(
        db,
        property_id,
        start_date,
        end_date
    )

@router.get("/payments/export/{contract_id}")
def export_payment_history(
    contract_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Exportar historial de pagos a Excel.
    """
    # Obtener datos
    payment_history = PaymentReportService.generate_payment_history(
        db,
        contract_id,
        start_date,
        end_date
    )
    
    # Exportar a Excel
    excel_file = PaymentReportService.export_to_excel(
        db,
        payment_history,
        f"Payment History - Contract {contract_id}"
    )
    
    # Preparar respuesta
    headers = {
        "Content-Disposition": f"attachment; filename=payment_history_{contract_id}.xlsx"
    }
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@router.get("/payments/export-late")
def export_late_payments(
    property_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Exportar reporte de pagos atrasados a Excel.
    """
    # Obtener datos
    late_payments = PaymentReportService.generate_late_payments_report(
        db,
        property_id
    )
    
    # Exportar a Excel
    excel_file = PaymentReportService.export_to_excel(
        db,
        late_payments,
        "Late Payments Report"
    )
    
    # Preparar respuesta
    headers = {
        "Content-Disposition": "attachment; filename=late_payments_report.xlsx"
    }
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
