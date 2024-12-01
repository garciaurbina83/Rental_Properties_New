from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.loan_report_service import LoanReportService
from datetime import date
import os
from app.core.config import settings

router = APIRouter()

@router.get("/loans/monthly/{year}/{month}")
async def get_monthly_loan_report(
    year: int,
    month: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener reporte mensual de préstamos.
    Si el reporte no existe, se generará uno nuevo.
    """
    # Validar mes y año
    try:
        date(year, month, 1)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Mes o año inválido"
        )

    # Verificar si existe el reporte
    report_path = os.path.join(
        settings.REPORTS_DIR,
        str(year),
        f"loan_report_{year}_{month:02d}.json"
    )

    if not os.path.exists(report_path):
        # Generar nuevo reporte
        report = await LoanReportService.generate_monthly_report(db, month, year)
    else:
        # Leer reporte existente
        import json
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

    return report

@router.get("/loans/{loan_id}/metrics")
async def get_loan_metrics(
    loan_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener métricas de rendimiento para un préstamo específico
    """
    try:
        return await LoanReportService.generate_loan_performance_metrics(db, loan_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.get("/loans/summary")
async def get_loans_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener resumen general de préstamos para un período específico
    """
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()

    report = await LoanReportService.generate_monthly_report(
        db,
        month=start_date.month,
        year=start_date.year
    )

    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": report["loan_summary"],
        "financial": report["financial_summary"],
        "projections": report["next_month_projection"]
    }
