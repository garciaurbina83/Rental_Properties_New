"""
Módulo para la generación de reportes en diferentes formatos.
"""

from typing import Dict, List, Any
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io
import json
from fastapi.responses import StreamingResponse
from app.core.i18n import i18n

class ReportGenerator:
    def __init__(self):
        self.supported_formats = ["pdf", "excel", "csv"]
        
    def _prepare_data(self, data: List[Dict], report_type: str) -> pd.DataFrame:
        """
        Prepara los datos para el reporte.
        
        Args:
            data (List[Dict]): Datos crudos
            report_type (str): Tipo de reporte
            
        Returns:
            pd.DataFrame: DataFrame con los datos procesados
        """
        df = pd.DataFrame(data)
        
        # Aplica transformaciones específicas según el tipo de reporte
        if report_type == "property_summary":
            # Calcula métricas adicionales
            df["occupancy_rate"] = df["occupied_months"] / 12 * 100
            df["revenue_per_sqm"] = df["total_revenue"] / df["square_meters"]
            
        elif report_type == "maintenance_summary":
            # Agrega columnas de costos y duración
            df["total_cost"] = df["labor_cost"] + df["materials_cost"]
            df["duration_days"] = (pd.to_datetime(df["end_date"]) - 
                                 pd.to_datetime(df["start_date"])).dt.days
            
        return df
        
    def generate_pdf(self, data: List[Dict], report_type: str, lang: str = "es") -> bytes:
        """
        Genera un reporte en formato PDF.
        
        Args:
            data (List[Dict]): Datos para el reporte
            report_type (str): Tipo de reporte
            lang (str, optional): Idioma del reporte. Defaults to "es".
            
        Returns:
            bytes: PDF generado
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Configura el título
        pdf.set_font("Arial", "B", 16)
        title = i18n.get_text(f"reports.{report_type}.title", lang)
        pdf.cell(0, 10, title, ln=True, align="C")
        
        # Agrega la fecha del reporte
        pdf.set_font("Arial", "", 10)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.cell(0, 10, f"{i18n.get_text('reports.generated_at', lang)}: {date_str}", ln=True)
        
        # Procesa los datos
        df = self._prepare_data(data, report_type)
        
        # Agrega la tabla de datos
        pdf.set_font("Arial", "B", 12)
        for column in df.columns:
            pdf.cell(40, 10, i18n.get_text(f"reports.columns.{column}", lang), 1)
        pdf.ln()
        
        pdf.set_font("Arial", "", 12)
        for _, row in df.iterrows():
            for value in row:
                pdf.cell(40, 10, str(value), 1)
            pdf.ln()
            
        return pdf.output(dest="S").encode("latin1")
        
    def generate_excel(self, data: List[Dict], report_type: str, lang: str = "es") -> bytes:
        """
        Genera un reporte en formato Excel.
        
        Args:
            data (List[Dict]): Datos para el reporte
            report_type (str): Tipo de reporte
            lang (str, optional): Idioma del reporte. Defaults to "es".
            
        Returns:
            bytes: Archivo Excel generado
        """
        df = self._prepare_data(data, report_type)
        
        # Traduce los nombres de las columnas
        translated_columns = {
            col: i18n.get_text(f"reports.columns.{col}", lang)
            for col in df.columns
        }
        df = df.rename(columns=translated_columns)
        
        # Crea el archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=i18n.get_text(f"reports.{report_type}.title", lang))
            
        return output.getvalue()
        
    def generate_csv(self, data: List[Dict], report_type: str, lang: str = "es") -> bytes:
        """
        Genera un reporte en formato CSV.
        
        Args:
            data (List[Dict]): Datos para el reporte
            report_type (str): Tipo de reporte
            lang (str, optional): Idioma del reporte. Defaults to "es".
            
        Returns:
            bytes: Archivo CSV generado
        """
        df = self._prepare_data(data, report_type)
        
        # Traduce los nombres de las columnas
        translated_columns = {
            col: i18n.get_text(f"reports.columns.{col}", lang)
            for col in df.columns
        }
        df = df.rename(columns=translated_columns)
        
        return df.to_csv(index=False).encode("utf-8")
        
    def generate_report(self, data: List[Dict], report_type: str, 
                       format: str = "pdf", lang: str = "es") -> StreamingResponse:
        """
        Genera un reporte en el formato especificado.
        
        Args:
            data (List[Dict]): Datos para el reporte
            report_type (str): Tipo de reporte
            format (str, optional): Formato del reporte. Defaults to "pdf".
            lang (str, optional): Idioma del reporte. Defaults to "es".
            
        Returns:
            StreamingResponse: Respuesta con el archivo generado
        """
        if format not in self.supported_formats:
            raise ValueError(f"Formato no soportado: {format}")
            
        # Genera el reporte en el formato solicitado
        if format == "pdf":
            content = self.generate_pdf(data, report_type, lang)
            media_type = "application/pdf"
        elif format == "excel":
            content = self.generate_excel(data, report_type, lang)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:  # csv
            content = self.generate_csv(data, report_type, lang)
            media_type = "text/csv"
            
        # Prepara el nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.{format}"
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

# Instancia global del generador de reportes
report_generator = ReportGenerator()

# Tipos de reportes disponibles
REPORT_TYPES = {
    "PROPERTY_SUMMARY": "property_summary",
    "MAINTENANCE_SUMMARY": "maintenance_summary",
    "TENANT_SUMMARY": "tenant_summary",
    "PAYMENT_SUMMARY": "payment_summary",
    "OCCUPANCY_REPORT": "occupancy_report"
}
