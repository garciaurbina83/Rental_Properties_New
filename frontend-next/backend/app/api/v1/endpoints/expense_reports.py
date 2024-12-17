from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
import os

from app import models, schemas
from app.api import deps
from app.core.security import get_current_active_user
from app.services.expense_report_service import expense_report_service
from app.core.config import settings

router = APIRouter()

@router.get("/summary")
async def get_expense_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(...),
    end_date: date = Query(...),
    property_id: int = Query(None),
    category_id: int = Query(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get expense summary report.
    """
    return await expense_report_service.generate_summary_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        property_id=property_id,
        category_id=category_id
    )

@router.get("/trends")
async def get_expense_trends(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(...),
    end_date: date = Query(...),
    group_by: str = Query("month", regex="^(day|week|month|year)$"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get expense trends over time.
    """
    return await expense_report_service.generate_trend_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )

@router.get("/category-distribution")
async def get_category_distribution(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get expense distribution by category.
    """
    return await expense_report_service.generate_category_distribution(
        db=db,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/property-comparison")
async def get_property_comparison(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get expense comparison across properties.
    """
    return await expense_report_service.generate_property_comparison(
        db=db,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/export")
async def export_expenses(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Export expenses to Excel file.
    """
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"expenses_{timestamp}.xlsx"
    file_path = os.path.join(reports_dir, filename)

    await expense_report_service.export_to_excel(
        db=db,
        start_date=start_date,
        end_date=end_date,
        file_path=file_path
    )

    return {
        "filename": filename,
        "file_path": file_path
    }
