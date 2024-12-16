from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os

from ....core.deps import get_db, get_current_active_user
from ....models.user import User
from ....crud import crud_payment
from ....services.receipts import ReceiptService

router = APIRouter()

@router.get("/{payment_id}")
async def generate_receipt(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Genera un recibo PDF para un pago específico
    """
    payment = crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Generar recibo
    receipt_path = await ReceiptService.generate_receipt_pdf(db, payment)
    
    # Enviar por email en segundo plano
    background_tasks.add_task(
        ReceiptService.send_receipt_email,
        db,
        payment,
        receipt_path
    )
    
    return FileResponse(
        receipt_path,
        media_type="application/pdf",
        filename=os.path.basename(receipt_path)
    )

@router.get("/{payment_id}/download")
async def download_receipt(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Descarga un recibo existente
    """
    payment = crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    receipt_number = ReceiptService.generate_receipt_number(payment)
    receipt_path = os.path.join(
        settings.STATIC_DIR,
        "receipts",
        f"{receipt_number}.pdf"
    )
    
    if not os.path.exists(receipt_path):
        # Si no existe, generarlo
        receipt_path = await ReceiptService.generate_receipt_pdf(db, payment)
    
    return FileResponse(
        receipt_path,
        media_type="application/pdf",
        filename=os.path.basename(receipt_path)
    )
