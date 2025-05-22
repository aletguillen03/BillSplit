import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import platform

from ..models.models import Bill
from ..utils.config import TEMP_DIR, SHARE_OPTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShareService:
    """Servicio para compartir facturas."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except Exception as e:
            self.logger.error(f"Error creating output directory: {str(e)}")
            raise
    
    def generate_pdf(self, bill_data: Dict, filename: Optional[str] = None) -> str:
        """Generate a PDF file from bill data."""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bill_{timestamp}.pdf"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Bill Splitter - Receipt")
            
            # Add date
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Add items
            y = height - 120
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Items:")
            
            y -= 20
            c.setFont("Helvetica", 10)
            total = 0
            for item, price in bill_data.get('items', {}).items():
                c.drawString(50, y, f"{item}")
                c.drawString(width - 100, y, f"${price:.2f}")
                total += price
                y -= 15
                
                # Check if we need a new page
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 10)
            
            # Add total
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Total:")
            c.drawString(width - 100, y, f"${total:.2f}")
            
            # Save PDF
            c.save()
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def generate_json(self, bill_data: Dict[str, Any]) -> Path:
        """
        Genera un archivo JSON con los datos de la factura.
        
        Args:
            bill_data: Datos de la factura
            
        Returns:
            Ruta al archivo JSON generado
        """
        try:
            # Crear archivo temporal
            json_path = self.output_dir / f'bill_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            # Guardar datos
            with open(json_path, 'w') as f:
                json.dump(bill_data, f, indent=2)
            
            return json_path
            
        except Exception as e:
            logger.error(f"Error generando JSON: {str(e)}")
            raise
    
    def share_bill(self, bill_data: Dict[str, Any], format: str = 'pdf') -> Optional[Path]:
        """
        Comparte una factura en el formato especificado.
        
        Args:
            bill_data: Datos de la factura
            format: Formato de salida ('pdf' o 'json')
            
        Returns:
            Ruta al archivo generado
        """
        try:
            if format.lower() == 'pdf':
                return self.generate_pdf(bill_data)
            elif format.lower() == 'json':
                return self.generate_json(bill_data)
            else:
                raise ValueError(f"Formato no soportado: {format}")
            
        except Exception as e:
            logger.error(f"Error compartiendo factura: {str(e)}")
            raise
    
    def cleanup(self):
        """Limpia los archivos temporales."""
        try:
            for file in self.output_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Error eliminando archivo temporal {file}: {str(e)}")
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {str(e)}")
    
    def __del__(self):
        """Destructor que limpia los archivos temporales."""
        self.cleanup()

    def generate_summary(self, bill_data: Dict) -> str:
        """Generate a text summary of the bill."""
        try:
            summary = []
            summary.append("Bill Summary")
            summary.append("=" * 50)
            summary.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            summary.append("\nItems:")
            
            total = 0
            for item, price in bill_data.get('items', {}).items():
                summary.append(f"{item}: ${price:.2f}")
                total += price
                
            summary.append("\nTotal: ${:.2f}".format(total))
            
            return "\n".join(summary)
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            raise 