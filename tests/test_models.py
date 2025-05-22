import pytest
from decimal import Decimal
from datetime import datetime
import uuid

from src.models.models import Bill, Item, Diner

def test_item_creation():
    """Prueba la creación de un Item."""
    item = Item(
        description="Hamburguesa",
        price=Decimal("10.99"),
        assigned_to=None
    )
    
    assert item.description == "Hamburguesa"
    assert item.price == Decimal("10.99")
    assert item.assigned_to is None

def test_diner_creation():
    """Prueba la creación de un Diner."""
    items = [
        Item(description="Hamburguesa", price=Decimal("10.99")),
        Item(description="Refresco", price=Decimal("2.50"))
    ]
    
    diner = Diner(
        id=str(uuid.uuid4()),
        name="Juan",
        items=items,
        tip_percentage=Decimal("15")
    )
    
    assert diner.name == "Juan"
    assert len(diner.items) == 2
    assert diner.tip_percentage == Decimal("15")
    assert diner.subtotal == Decimal("13.49")
    assert diner.tip_amount == Decimal("2.02")
    assert diner.total == Decimal("15.51")

def test_bill_creation():
    """Prueba la creación de un Bill."""
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
    
    bill = Bill(
        id=str(uuid.uuid4()),
        date=datetime.now(),
        items=items,
        diners=diners,
        total_amount=Decimal("17.48"),
        tip_percentage=Decimal("15")
    )
    
    assert len(bill.items) == 3
    assert len(bill.diners) == 2
    assert bill.total_amount == Decimal("17.48")
    assert bill.tip_percentage == Decimal("15")
    assert bill.subtotal == Decimal("17.48")
    assert bill.tip_amount == Decimal("2.62")

def test_bill_assign_item():
    """Prueba la asignación de items a comensales."""
    items = [
        Item(description="Hamburguesa", price=Decimal("10.99")),
        Item(description="Refresco", price=Decimal("2.50"))
    ]
    
    diner = Diner(
        id=str(uuid.uuid4()),
        name="Juan",
        items=[],
        tip_percentage=Decimal("15")
    )
    
    bill = Bill(
        id=str(uuid.uuid4()),
        date=datetime.now(),
        items=items,
        diners=[diner],
        total_amount=Decimal("13.49"),
        tip_percentage=Decimal("15")
    )
    
    # Asignar items
    bill.assign_item(0, diner.id)  # Hamburguesa
    bill.assign_item(1, diner.id)  # Refresco
    
    assert len(diner.items) == 2
    assert items[0].assigned_to == diner.id
    assert items[1].assigned_to == diner.id

def test_bill_get_diner_summary():
    """Prueba la generación de resumen por comensal."""
    items = [
        Item(description="Hamburguesa", price=Decimal("10.99")),
        Item(description="Refresco", price=Decimal("2.50"))
    ]
    
    diner = Diner(
        id=str(uuid.uuid4()),
        name="Juan",
        items=items,
        tip_percentage=Decimal("15")
    )
    
    bill = Bill(
        id=str(uuid.uuid4()),
        date=datetime.now(),
        items=items,
        diners=[diner],
        total_amount=Decimal("13.49"),
        tip_percentage=Decimal("15")
    )
    
    summary = bill.get_diner_summary(diner.id)
    
    assert summary['name'] == "Juan"
    assert len(summary['items']) == 2
    assert summary['subtotal'] == Decimal("13.49")
    assert summary['tip_amount'] == Decimal("2.02")
    assert summary['total'] == Decimal("15.51") 