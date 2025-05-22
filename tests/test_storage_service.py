import pytest
from decimal import Decimal
from datetime import datetime
import uuid
import os
import tempfile

from src.models.models import Bill, Item, Diner
from src.services.storage_service import StorageService

@pytest.fixture
def temp_db():
    """Fixture para crear una base de datos temporal."""
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Crear servicio con base de datos temporal
    service = StorageService()
    service.db_path = db_path
    service._init_db()
    
    yield service
    
    # Limpiar
    os.remove(db_path)
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

def test_save_bill(temp_db, sample_bill):
    """Prueba guardar una cuenta en la base de datos."""
    # Guardar cuenta
    assert temp_db.save_bill(sample_bill) is True
    
    # Verificar que se guardó
    saved_bill = temp_db.get_bill(sample_bill.id)
    assert saved_bill is not None
    assert saved_bill.id == sample_bill.id
    assert len(saved_bill.items) == len(sample_bill.items)
    assert len(saved_bill.diners) == len(sample_bill.diners)
    assert saved_bill.total_amount == sample_bill.total_amount

def test_get_bill(temp_db, sample_bill):
    """Prueba obtener una cuenta de la base de datos."""
    # Guardar cuenta
    temp_db.save_bill(sample_bill)
    
    # Obtener cuenta
    bill = temp_db.get_bill(sample_bill.id)
    
    # Verificar datos
    assert bill.id == sample_bill.id
    assert bill.date.date() == sample_bill.date.date()
    assert bill.total_amount == sample_bill.total_amount
    assert bill.tip_percentage == sample_bill.tip_percentage
    
    # Verificar items
    assert len(bill.items) == len(sample_bill.items)
    for saved_item, original_item in zip(bill.items, sample_bill.items):
        assert saved_item.description == original_item.description
        assert saved_item.price == original_item.price
    
    # Verificar comensales
    assert len(bill.diners) == len(sample_bill.diners)
    for saved_diner, original_diner in zip(bill.diners, sample_bill.diners):
        assert saved_diner.id == original_diner.id
        assert saved_diner.name == original_diner.name
        assert saved_diner.tip_percentage == original_diner.tip_percentage

def test_get_all_bills(temp_db, sample_bill):
    """Prueba obtener todas las cuentas de la base de datos."""
    # Guardar cuenta
    temp_db.save_bill(sample_bill)
    
    # Obtener todas las cuentas
    bills = temp_db.get_all_bills()
    
    # Verificar resultados
    assert len(bills) == 1
    assert bills[0].id == sample_bill.id

def test_delete_bill(temp_db, sample_bill):
    """Prueba eliminar una cuenta de la base de datos."""
    # Guardar cuenta
    temp_db.save_bill(sample_bill)
    
    # Eliminar cuenta
    assert temp_db.delete_bill(sample_bill.id) is True
    
    # Verificar que se eliminó
    assert temp_db.get_bill(sample_bill.id) is None
    assert len(temp_db.get_all_bills()) == 0

def test_get_nonexistent_bill(temp_db):
    """Prueba obtener una cuenta que no existe."""
    bill = temp_db.get_bill(str(uuid.uuid4()))
    assert bill is None

def test_delete_nonexistent_bill(temp_db):
    """Prueba eliminar una cuenta que no existe."""
    assert temp_db.delete_bill(str(uuid.uuid4())) is False 