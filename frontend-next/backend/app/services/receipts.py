from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import qrcode
from io import BytesIO

from ..models.payment import Payment
from ..models.contract import Contract
from ..models.tenant import Tenant
from ..core.config import settings

class ReceiptService:
    @staticmethod
    def generate_receipt_number(payment: Payment) -> str:
        """Genera un número único de recibo"""
        timestamp = int(datetime.timestamp(payment.created_at))
        return f"REC-{payment.id}-{timestamp}"

    @staticmethod
    def generate_receipt_qr(payment: Payment, receipt_number: str) -> bytes:
        """Genera un código QR con la información del pago"""
        qr_data = (
            f"Receipt: {receipt_number}\n"
            f"Date: {payment.payment_date}\n"
            f"Amount: ${payment.amount}\n"
            f"Status: {payment.status}"
        )
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer)
        return img_buffer.getvalue()

    @staticmethod
    def format_currency(amount: float) -> str:
        """Formatea cantidades monetarias"""
        return "${:,.2f}".format(amount)

    @staticmethod
    async def generate_receipt_pdf(
        db: Session,
        payment: Payment,
        output_path: Optional[str] = None
    ) -> str:
        """Genera un PDF con el recibo de pago"""
        # Obtener datos relacionados
        contract = db.query(Contract).filter(Contract.id == payment.contract_id).first()
        tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
        
        if not contract or not tenant:
            raise HTTPException(status_code=404, detail="Contract or tenant not found")
        
        # Generar número de recibo
        receipt_number = ReceiptService.generate_receipt_number(payment)
        
        # Configurar el documento PDF
        if output_path is None:
            output_dir = os.path.join(settings.STATIC_DIR, "receipts")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{receipt_number}.pdf")
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        normal_style = styles["Normal"]
        
        # Contenido
        story = []
        
        # Título
        story.append(Paragraph("RECIBO DE PAGO", title_style))
        story.append(Spacer(1, 12))
        
        # Información del recibo
        receipt_info = [
            ["Número de Recibo:", receipt_number],
            ["Fecha:", payment.payment_date.strftime("%d/%m/%Y")],
            ["Estado:", payment.status.value],
            ["Concepto:", payment.concept.value]
        ]
        
        # Información del inquilino
        tenant_info = [
            ["Inquilino:", f"{tenant.first_name} {tenant.last_name}"],
            ["Email:", tenant.email],
            ["Teléfono:", tenant.phone_number or "N/A"]
        ]
        
        # Información del contrato
        contract_info = [
            ["Contrato:", f"#{contract.id}"],
            ["Propiedad:", contract.property_id],
            ["Inicio:", contract.start_date.strftime("%d/%m/%Y")],
            ["Fin:", contract.end_date.strftime("%d/%m/%Y")]
        ]
        
        # Información del pago
        payment_info = [
            ["Monto:", ReceiptService.format_currency(payment.amount)],
            ["Método de Pago:", "Transfer"],  # TODO: Agregar método de pago al modelo
            ["Descripción:", payment.description or "N/A"]
        ]
        
        # Crear tablas
        for info, title in [
            (receipt_info, "Información del Recibo"),
            (tenant_info, "Información del Inquilino"),
            (contract_info, "Información del Contrato"),
            (payment_info, "Información del Pago")
        ]:
            story.append(Paragraph(title, styles["Heading2"]))
            story.append(Spacer(1, 12))
            
            t = Table(info, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
        
        # Agregar código QR
        qr_data = ReceiptService.generate_receipt_qr(payment, receipt_number)
        # TODO: Agregar código QR al PDF
        
        # Generar PDF
        doc.build(story)
        
        return output_path

    @staticmethod
    async def send_receipt_email(
        db: Session,
        payment: Payment,
        receipt_path: str
    ) -> None:
        """Envía el recibo por email al inquilino"""
        tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # TODO: Implementar envío de email con el recibo adjunto
        pass
