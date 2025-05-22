import pytest
from decimal import Decimal
from datetime import datetime
import uuid
import os
import tempfile

from src.models.models import Bill, Item, Diner
from src.services.share_service import ShareService

@pytest.fixture
def temp_dir():
    """Fixture para crear un directorio temporal."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    os.rmdir(temp_dir)

@pytest.fixture
def sample_bill():
    """Fixture para crear una cuenta de ejemplo."""
    items = [
        Item(description="Hamburguesa", price=Decimal("10.99")),
        Item(description="Refresco", price=Decimal("2.50")),
        Item(description="Papas fritas", price=Decimal("3.99"))
    ]
    
    diners = [
        Diner(
            id=str(uuid.uuid4()),
            name="Juan",
            items=[items[0], items[1]],
            tip_percentage=Decimal("15")
        ),
        Diner(
            id=str(uuid.uuid4()),
            name="María",
            items=[items[2]],
            tip_percentage=Decimal("15")
        )
    ]
    
    return Bill(
        id=str(uuid.uuid4()),
        date=datetime.now(),
        items=items,
        diners=diners,
        total_amount=Decimal("17.48"),
        tip_percentage=Decimal("15")
    )

def test_generate_text_summary(temp_dir, sample_bill):
    """Prueba la generación de resumen en texto."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # Generar resumen para el primer comensal
    text = service.generate_text_summary(sample_bill, sample_bill.diners[0].id)
    
    # Verificar contenido
    assert "Resumen de cuenta para Juan" in text
    assert "Hamburguesa" in text
    assert "Refresco" in text
    assert "10.99" in text
    assert "2.50" in text
    assert "Subtotal" in text
    assert "Propina" in text
    assert "Total" in text

def test_generate_pdf_summary(temp_dir, sample_bill):
    """Prueba la generación de resumen en PDF."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # Generar PDF para el primer comensal
    pdf_path = service.generate_pdf_summary(sample_bill, sample_bill.diners[0].id)
    
    # Verificar que se generó el archivo
    assert pdf_path is not None
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith('.pdf')
    
    # Limpiar
    os.remove(pdf_path)

def test_generate_summary_nonexistent_diner(temp_dir, sample_bill):
    """Prueba generar resumen para un comensal que no existe."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # Intentar generar resumen para un ID inexistente
    text = service.generate_text_summary(sample_bill, str(uuid.uuid4()))
    assert text == ""
    
    pdf_path = service.generate_pdf_summary(sample_bill, str(uuid.uuid4()))
    assert pdf_path is None

def test_share_summary_invalid_method(temp_dir, sample_bill):
    """Prueba compartir resumen con método inválido."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # Intentar compartir con método inválido
    with pytest.raises(ValueError):
        service.share_summary(sample_bill, sample_bill.diners[0].id, "invalid_method")

def test_share_summary_clipboard(temp_dir, sample_bill):
    """Prueba compartir resumen al portapapeles."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # TODO: Implementar prueba de portapapeles cuando se implemente la funcionalidad
    pass

def test_share_summary_whatsapp(temp_dir, sample_bill):
    """Prueba compartir resumen por WhatsApp."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # TODO: Implementar prueba de WhatsApp cuando se implemente la funcionalidad
    pass

def test_share_summary_imessage(temp_dir, sample_bill):
    """Prueba compartir resumen por iMessage."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # TODO: Implementar prueba de iMessage cuando se implemente la funcionalidad
    pass

def test_share_summary_email(temp_dir, sample_bill):
    """Prueba compartir resumen por email."""
    service = ShareService()
    service.temp_dir = temp_dir
    
    # TODO: Implementar prueba de email cuando se implemente la funcionalidad
    pass 