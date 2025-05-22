from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
from decimal import Decimal, InvalidOperation
import uuid
from plyer import camera, filechooser
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models.models import Bill, Item, Diner
from services.ocr_service import OCRService
from services.storage_service import StorageService
from services.share_service import ShareService

class CameraScreen(Screen):
    """Pantalla para capturar la foto del ticket."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ocr_service = OCRService()
        self.storage_service = StorageService()
        self.share_service = ShareService()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Camera preview will be added here
        self.camera_preview = BoxLayout()
        layout.add_widget(self.camera_preview)
        
        # Capture button
        capture_btn = Button(
            text='Capture',
            size_hint_y=None,
            height=50
        )
        capture_btn.bind(on_press=self.capture)
        layout.add_widget(capture_btn)
        
        self.add_widget(layout)
    
    def capture(self, instance):
        # Capture image and process with OCR
        # This will be implemented with platform-specific camera code
        pass

class ItemsScreen(Screen):
    """Pantalla para revisar, editar y asignar items a comensales."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Lista de items
        self.items_grid = GridLayout(cols=4, spacing=5, size_hint_y=None)
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(self.items_grid)
        
        # Comensales
        self.comensales_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.comensales_inputs = []
        self.add_comensal_btn = Button(text='+ Comensal', size_hint_x=0.3, on_press=self.add_comensal)
        self.comensales_box.add_widget(self.add_comensal_btn)
        
        # Botones de control
        self.control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.add_item_btn = Button(text='+ Ítem', on_press=self.add_item)
        self.next_btn = Button(text='Siguiente', on_press=self.next_screen)
        self.back_btn = Button(text='Atrás', on_press=self.previous_screen)
        
        self.control_layout.add_widget(self.back_btn)
        self.control_layout.add_widget(self.add_item_btn)
        self.control_layout.add_widget(self.next_btn)
        
        self.layout.add_widget(Label(text='Revisa, edita y asigna cada ítem a un comensal:', size_hint=(1, 0.05)))
        self.layout.add_widget(scroll)
        self.layout.add_widget(Label(text='Comensales:', size_hint=(1, 0.05)))
        self.layout.add_widget(self.comensales_box)
        self.layout.add_widget(self.control_layout)
        self.add_widget(self.layout)
        
        self.items = []
        self.comensales = []
    
    def set_items(self, items):
        """Carga los items detectados en la interfaz."""
        self.items = [list(item) + [None] for item in items]  # [desc, price, comensal]
        if not self.comensales:
            self.comensales = [f'Comensal {i+1}' for i in range(len(items))]
        self.refresh()
    
    def refresh(self):
        self.items_grid.clear_widgets()
        self.items_grid.height = 40 * (len(self.items) + 1)
        # Cabecera
        self.items_grid.add_widget(Label(text='Descripción'))
        self.items_grid.add_widget(Label(text='Precio'))
        self.items_grid.add_widget(Label(text='Comensal'))
        self.items_grid.add_widget(Label(text=''))
        # Filas de ítems
        for idx, (desc, price, comensal) in enumerate(self.items):
            desc_input = TextInput(text=desc, multiline=False)
            price_input = TextInput(text=str(price), multiline=False, input_filter='float')
            spinner = Spinner(text=comensal or (self.comensales[0] if self.comensales else ''),
                              values=self.comensales, size_hint_x=0.7)
            del_btn = Button(text='X', size_hint_x=0.3, on_press=lambda x, i=idx: self.remove_item(i))
            desc_input.bind(text=lambda inst, val, i=idx: self.update_item(i, 0, val))
            price_input.bind(text=lambda inst, val, i=idx: self.update_item(i, 1, val))
            spinner.bind(text=lambda inst, val, i=idx: self.update_item(i, 2, val))
            self.items_grid.add_widget(desc_input)
            self.items_grid.add_widget(price_input)
            self.items_grid.add_widget(spinner)
            self.items_grid.add_widget(del_btn)
        # Comensales
        self.comensales_box.clear_widgets()
        for idx, name in enumerate(self.comensales):
            input_box = BoxLayout(size_hint_x=0.3)
            name_input = TextInput(text=name, multiline=False)
            name_input.bind(text=lambda inst, val, i=idx: self.update_comensal(i, val))
            del_btn = Button(text='-', size_hint_x=0.3, on_press=lambda x, i=idx: self.remove_comensal(i))
            input_box.add_widget(name_input)
            input_box.add_widget(del_btn)
            self.comensales_box.add_widget(input_box)
        self.comensales_box.add_widget(self.add_comensal_btn)
    
    def update_item(self, idx, field, value):
        if field == 1:
            try:
                value = str(float(value))
            except Exception:
                value = '0.0'
        self.items[idx][field] = value
        self.refresh()
    
    def update_comensal(self, idx, value):
        self.comensales[idx] = value
        self.refresh()
    
    def add_item(self, instance):
        self.items.append(['', '0.0', self.comensales[0] if self.comensales else ''])
        self.refresh()
    
    def remove_item(self, idx):
        if len(self.items) > 1:
            self.items.pop(idx)
            self.refresh()
    
    def add_comensal(self, instance):
        self.comensales.append(f'Comensal {len(self.comensales)+1}')
        self.refresh()
    
    def remove_comensal(self, idx):
        if len(self.comensales) > 1:
            name = self.comensales.pop(idx)
            # Desasignar ítems de ese comensal
            for item in self.items:
                if item[2] == name:
                    item[2] = self.comensales[0]
            self.refresh()
    
    def next_screen(self, instance):
        # Validar y construir objetos
        diners = [Diner(id=str(uuid.uuid4()), name=name, items=[], tip_percentage=Decimal('0')) for name in self.comensales]
        items = []
        for desc, price, comensal in self.items:
            try:
                price_val = Decimal(str(price))
            except InvalidOperation:
                price_val = Decimal('0.0')
            diner = next((d for d in diners if d.name == comensal), None)
            item = Item(description=desc, price=price_val, assigned_to=diner.id if diner else None)
            items.append(item)
            if diner:
                diner.items.append(item)
        bill = Bill(id=str(uuid.uuid4()), date=datetime.now(), items=items, diners=diners, total_amount=sum(i.price for i in items), tip_percentage=Decimal('0'))
        self.manager.get_screen('summary').show_summary(bill)
        self.manager.current = 'summary'
    
    def previous_screen(self, instance):
        self.manager.current = 'camera'

class DinersScreen(Screen):
    """Pantalla para asignar items a comensales."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Lista de comensales
        self.diners_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.diners_grid.bind(minimum_height=self.diners_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.diners_grid)
        
        # Botones de control
        control_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.add_diner_btn = Button(
            text='Agregar Comensal',
            on_press=self.add_diner
        )
        self.next_btn = Button(
            text='Siguiente',
            on_press=self.next_screen
        )
        self.back_btn = Button(
            text='Atrás',
            on_press=self.previous_screen
        )
        
        control_layout.add_widget(self.back_btn)
        control_layout.add_widget(self.add_diner_btn)
        control_layout.add_widget(self.next_btn)
        
        self.layout.add_widget(scroll)
        self.layout.add_widget(control_layout)
        self.add_widget(self.layout)
    
    def add_diner(self, instance):
        """Agrega un nuevo comensal a la lista."""
        diner_id = str(uuid.uuid4())
        diner_layout = BoxLayout(size_hint_y=None, height=50)
        
        name_input = TextInput(
            hint_text='Nombre del comensal',
            multiline=False,
            size_hint_x=0.7
        )
        
        delete_btn = Button(
            text='X',
            size_hint_x=0.3,
            on_press=lambda x: self.remove_diner(diner_id)
        )
        
        diner_layout.add_widget(name_input)
        diner_layout.add_widget(delete_btn)
        self.diners_grid.add_widget(diner_layout)
    
    def remove_diner(self, diner_id):
        """Elimina un comensal de la lista."""
        # TODO: Implementar eliminación de comensal
        pass
    
    def next_screen(self, instance):
        self.manager.current = 'summary'
    
    def previous_screen(self, instance):
        self.manager.current = 'items'

class SummaryScreen(Screen):
    """Pantalla para mostrar el resumen final."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_service = StorageService()
        self.share_service = ShareService()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='Bill Summary',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Items list
        scroll = ScrollView()
        self.items_layout = GridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None
        )
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        scroll.add_widget(self.items_layout)
        layout.add_widget(scroll)
        
        # Total
        self.total_label = Label(
            text='Total: $0.00',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.total_label)
        
        # Buttons
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        save_btn = Button(text='Save')
        save_btn.bind(on_press=self.save_bill)
        buttons_layout.add_widget(save_btn)
        
        share_btn = Button(text='Share')
        share_btn.bind(on_press=self.share_bill)
        buttons_layout.add_widget(share_btn)
        
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def show_summary(self, bill):
        """Muestra el resumen de la cuenta."""
        self.items_layout.clear_widgets()
        total = 0
        
        for item in bill.items:
            self.items_layout.add_widget(Label(text=item.description))
            self.items_layout.add_widget(Label(text=f'${item.price:.2f}'))
            total += item.price
            
        self.total_label.text = f'Total: ${total:.2f}'
        
    def save_bill(self, instance):
        # Save current bill
        pass
        
    def share_bill(self, instance):
        # Share current bill
        pass

class HistoryScreen(Screen):
    """Pantalla de historial de facturas."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_service = StorageService()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='Bill History',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Bills list
        scroll = ScrollView()
        self.bills_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )
        self.bills_layout.bind(minimum_height=self.bills_layout.setter('height'))
        scroll.add_widget(self.bills_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_bills(self):
        self.bills_layout.clear_widgets()
        bills = self.storage_service.list_bills()
        
        for bill in bills:
            btn = Button(
                text=f"{bill['timestamp']} - ${bill['total']:.2f}",
                size_hint_y=None,
                height=50
            )
            btn.bind(on_press=lambda x, b=bill: self.view_bill(b))
            self.bills_layout.add_widget(btn)
            
    def view_bill(self, bill):
        # View bill details
        pass

class BillSplitterApp(App):
    """Aplicación principal para dividir cuentas."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.current_bill = None
        self.storage_service = StorageService()
        self.bills_history = self.storage_service.get_all_bills()
        
    def build(self):
        """Construye la interfaz de la aplicación."""
        # Configurar tema y estilo
        self.setup_theme()
        
        # Agregar pantallas
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(HistoryScreen(name='history'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        
        return self.sm
    
    def setup_theme(self):
        """Configura el tema y estilo de la aplicación."""
        # Configurar colores
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        
        # Configurar tamaño de fuente
        self.theme_cls.font_styles["H1"] = ["Roboto", 96, False, -1.5]
        self.theme_cls.font_styles["H2"] = ["Roboto", 60, False, -0.5]
        self.theme_cls.font_styles["H6"] = ["Roboto", 20, True, 0.15]
        self.theme_cls.font_styles["Body1"] = ["Roboto", 16, False, 0.5]
        
        # Configurar espaciado
        self.theme_cls.spacing = dp(8)
        
    def _load_history(self):
        """Carga el historial de facturas desde el almacenamiento."""
        # La carga se realiza en __init__ usando StorageService
        pass
    
    def _save_history(self):
        """Guarda el historial de facturas en el almacenamiento."""
        # El guardado se realiza al crear/actualizar facturas a través de StorageService
        pass
    
    def on_stop(self):
        """Se llama cuando la aplicación se cierra."""
        # No es necesario guardar explícitamente aquí con StorageService basado en SQLite
        # self._save_history()
        # Limpiar recursos temporales si existen
        # if self.current_bill:
        #     self.current_bill.cleanup()
        pass

class MainScreen(Screen):
    """Pantalla principal de la aplicación."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        self.current_bill = None
        self._setup_keyboard()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        
        # Barra superior
        top_bar = BoxLayout(size_hint_y=None, height=dp(48))
        history_btn = Button(text='Historial', on_press=self.show_history)
        settings_btn = Button(text='Configuración', on_press=self.show_settings)
        top_bar.add_widget(history_btn)
        top_bar.add_widget(settings_btn)
        layout.add_widget(top_bar)
        
        # Contenido principal
        self.content = BoxLayout(orientation='vertical', spacing=dp(16))
        layout.add_widget(self.content)
        
        self.add_widget(layout)
    
    def _setup_keyboard(self):
        """Configura el manejo del teclado."""
        if platform == 'android':
            Window.softinput_mode = 'below_target'
    
    def show_history(self, *args):
        """Muestra la pantalla de historial."""
        self.manager.get_screen('history').update_bills()
        self.manager.current = 'history'
    
    def show_settings(self, *args):
        """Muestra la pantalla de configuración."""
        self.manager.current = 'settings'
    
    def on_leave(self):
        """Se llama cuando se abandona la pantalla."""
        if self.current_bill:
            self.current_bill.cleanup()

class SettingsScreen(Screen):
    """Pantalla de configuración."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        
        # Barra superior
        top_bar = BoxLayout(size_hint_y=None, height=dp(48))
        back_btn = Button(text='Volver', on_press=self.go_back)
        top_bar.add_widget(back_btn)
        layout.add_widget(top_bar)
        
        # Configuraciones
        settings = BoxLayout(orientation='vertical', spacing=dp(16))
        
        # Tema
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48))
        theme_layout.add_widget(Label(text='Tema:'))
        theme_btn = Button(text='Cambiar', on_press=self.change_theme)
        theme_layout.add_widget(theme_btn)
        settings.add_widget(theme_layout)
        
        # Idioma
        lang_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48))
        lang_layout.add_widget(Label(text='Idioma:'))
        lang_btn = Button(text='Cambiar', on_press=self.change_language)
        lang_layout.add_widget(lang_btn)
        settings.add_widget(lang_layout)
        
        layout.add_widget(settings)
        self.add_widget(layout)
    
    def go_back(self, *args):
        """Regresa a la pantalla principal."""
        self.manager.current = 'main'
    
    def change_theme(self, *args):
        """Cambia el tema de la aplicación."""
        # TODO: Implementar cambio de tema
        pass
    
    def change_language(self, *args):
        """Cambia el idioma de la aplicación."""
        # TODO: Implementar cambio de idioma
        pass

class HistoryItem(BoxLayout):
    """Widget para mostrar un item del historial."""
    
    def __init__(self, bill_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = dp(8)
        self.spacing = dp(8)
        
        # Fecha
        date = datetime.fromisoformat(bill_data['date'])
        date_str = date.strftime('%d/%m/%Y %H:%M')
        self.add_widget(Label(text=date_str))
        
        # Total
        total = Decimal(bill_data['total'])
        self.add_widget(Label(text=f'${total:.2f}'))
        
        # Botón para ver detalles
        details_btn = Button(text='Ver', size_hint_x=None, width=dp(64))
        details_btn.bind(on_press=lambda x: self.show_details(bill_data))
        self.add_widget(details_btn)
    
    def show_details(self, bill_data):
        """Muestra los detalles de la factura."""
        popup = Popup(
            title='Detalles de la Factura',
            content=BoxLayout(orientation='vertical'),
            size_hint=(None, None),
            size=(400, 600)
        )
        
        content = popup.content
        content.padding = dp(16)
        content.spacing = dp(8)
        
        # Fecha
        date = datetime.fromisoformat(bill_data['date'])
        date_str = date.strftime('%d/%m/%Y %H:%M')
        content.add_widget(Label(text=f'Fecha: {date_str}'))
        
        # Items
        items_layout = GridLayout(cols=2, spacing=dp(8))
        for item in bill_data['items']:
            items_layout.add_widget(Label(text=item['description']))
            items_layout.add_widget(Label(text=f'${item["price"]:.2f}'))
        content.add_widget(items_layout)
        
        # Total
        total = Decimal(bill_data['total'])
        content.add_widget(Label(text=f'Total: ${total:.2f}'))
        
        # Botón para cerrar
        close_btn = Button(text='Cerrar', size_hint_y=None, height=dp(48))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()

if __name__ == '__main__':
    BillSplitterApp().run() 