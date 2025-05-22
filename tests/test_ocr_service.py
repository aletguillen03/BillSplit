import pytest
from decimal import Decimal
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile

from src.services.ocr_service import OCRService

def create_test_image():
    """Crea una imagen de prueba con texto de ticket."""
    # Crear imagen en blanco
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Agregar texto de ticket
    text = [
        "RESTAURANTE EJEMPLO",
        "-------------------",
        "Hamburguesa    10.99",
        "Refresco       2.50",
        "Papas fritas   3.99",
        "-------------------",
        "Total:        17.48"
    ]
    
    # Dibujar texto
    y = 50
    for line in text:
        draw.text((50, y), line, fill='black')
        y += 30
    
    return img

def test_ocr_service_initialization():
    """Prueba la inicialización del servicio OCR."""
    service = OCRService()
    assert service.config == '--psm 6 --oem 3 -l spa'

def test_process_image():
    """Prueba el procesamiento de una imagen de ticket."""
    # Crear imagen de prueba
    img = create_test_image()
    
    # Guardar imagen temporalmente
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
        img.save(temp.name)
        temp_path = temp.name
    
    try:
        # Procesar imagen
        service = OCRService()
        items = service.process_image(temp_path)
        
        # Verificar resultados
        assert len(items) > 0
        
        # Verificar que se detectaron los items principales
        descriptions = [item[0].lower() for item in items]
        assert any('hamburguesa' in desc for desc in descriptions)
        assert any('refresco' in desc for desc in descriptions)
        assert any('papas' in desc for desc in descriptions)
        
        # Verificar precios
        prices = [item[1] for item in items]
        assert Decimal('10.99') in prices
        assert Decimal('2.50') in prices
        assert Decimal('3.99') in prices
        
    finally:
        # Limpiar archivo temporal
        os.unlink(temp_path)

def test_parse_text():
    """Prueba el parsing de texto de ticket."""
    service = OCRService()
    
    # Texto de ejemplo
    text = """
    RESTAURANTE EJEMPLO
    -------------------
    Hamburguesa    10.99
    Refresco       2.50
    Papas fritas   3.99
    -------------------
    Total:        17.48
    """
    
    items = service._parse_text(text)
    
    # Verificar resultados
    assert len(items) == 3
    
    # Verificar items y precios
    items_dict = {desc.lower(): price for desc, price in items}
    assert 'hamburguesa' in items_dict
    assert 'refresco' in items_dict
    assert 'papas fritas' in items_dict
    
    assert items_dict['hamburguesa'] == Decimal('10.99')
    assert items_dict['refresco'] == Decimal('2.50')
    assert items_dict['papas fritas'] == Decimal('3.99')

def test_validate_items():
    """Prueba la validación de items extraídos."""
    service = OCRService()
    
    # Items de ejemplo
    items = [
        ("Hamburguesa", Decimal('10.99')),
        ("Refresco", Decimal('2.50')),
        ("Papas fritas", Decimal('3.99'))
    ]
    
    # Validar sin total esperado
    assert service.validate_items(items) is True
    
    # Validar con total correcto
    assert service.validate_items(items, Decimal('17.48')) is True
    
    # Validar con total incorrecto
    assert service.validate_items(items, Decimal('20.00')) is False
    
    # Validar con lista vacía
    assert service.validate_items([]) is False 