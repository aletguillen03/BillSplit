import pytesseract
from PIL import Image, ImageEnhance
import re
from decimal import Decimal
from typing import List, Tuple, Optional, Dict
import logging
import numpy as np
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """Servicio para procesar imágenes de tickets usando OCR."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Configurar pytesseract para español
        self.config = '--psm 6 --oem 3 -l spa'
    
    def process_image(self, image: np.ndarray) -> Dict[str, float]:
        """
        Procesa una imagen de ticket y extrae los items y precios.
        
        Args:
            image: Imagen del ticket en formato numpy array
            
        Returns:
            Diccionario con los items y sus precios
        """
        try:
            text = self.extract_text(image)
            return self.parse_bill(text)
        except Exception as e:
            self.logger.error(f"Error procesando imagen: {str(e)}")
            return {}
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for better OCR results."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get a binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Noise removal
            denoised = cv2.fastNlMeansDenoising(binary)
            
            return denoised
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            return image

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from the preprocessed image."""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(pil_image, lang='eng')
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return ""

    def parse_bill(self, text: str) -> Dict[str, float]:
        """Parse the extracted text to identify items and prices."""
        try:
            items = {}
            lines = text.split('\n')
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Try to find price at the end of the line
                parts = line.rsplit(' ', 1)
                if len(parts) == 2:
                    item_name, price_str = parts
                    try:
                        # Remove currency symbols and convert to float
                        price = float(price_str.replace('$', '').replace(',', '').strip())
                        items[item_name.strip()] = price
                    except ValueError:
                        continue
            
            return items
        except Exception as e:
            self.logger.error(f"Error parsing bill: {str(e)}")
            return {}
    
    def _parse_text(self, text: str) -> List[Tuple[str, Decimal]]:
        """
        Parsea el texto extraído para identificar items y precios.
        
        Args:
            text: Texto extraído del OCR
            
        Returns:
            Lista de tuplas (descripción, precio)
        """
        items = []
        lines = text.split('\n')
        
        # Patrones para encontrar precios (múltiples formatos)
        price_patterns = [
            r'\d+[.,]\d{2}',  # Formato estándar (10.50)
            r'\d+[.,]\d{1}',  # Formato sin decimales (10.5)
            r'\d+',           # Solo números
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Intentar cada patrón de precio
            for pattern in price_patterns:
                price_match = re.search(pattern, line)
                if price_match:
                    price_str = price_match.group().replace(',', '.')
                    try:
                        price = Decimal(price_str)
                        # La descripción es todo lo que está antes del precio
                        description = line[:price_match.start()].strip()
                        if description:
                            items.append((description, price))
                            break  # Si encontramos un precio válido, pasamos a la siguiente línea
                    except (ValueError, decimal.InvalidOperation):
                        continue
        
        return items
    
    def _parse_text_alternative(self, text: str) -> List[Tuple[str, Decimal]]:
        """
        Método alternativo de parsing para cuando el método principal falla.
        
        Args:
            text: Texto extraído del OCR
            
        Returns:
            Lista de tuplas (descripción, precio)
        """
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Buscar números al final de la línea
            parts = re.split(r'(\d+[.,]?\d*)', line)
            if len(parts) >= 2:
                description = parts[0].strip()
                price_str = parts[1].replace(',', '.')
                try:
                    price = Decimal(price_str)
                    if description:
                        items.append((description, price))
                except (ValueError, decimal.InvalidOperation):
                    continue
        
        return items
    
    def validate_items(self, items: List[Tuple[str, Decimal]], 
                      expected_total: Optional[Decimal] = None) -> bool:
        """
        Valida que los items extraídos sean coherentes.
        
        Args:
            items: Lista de items extraídos
            expected_total: Total esperado del ticket (opcional)
            
        Returns:
            True si la validación es exitosa
        """
        if not items:
            return False
            
        # Calcular subtotal
        subtotal = sum(price for _, price in items)
        
        # Validar que no haya precios negativos o cero
        if any(price <= 0 for _, price in items):
            return False
        
        # Si tenemos un total esperado, verificar que coincida
        if expected_total:
            # Permitir una pequeña diferencia por errores de OCR
            tolerance = Decimal('0.01')
            return abs(subtotal - expected_total) <= tolerance
            
        return True 