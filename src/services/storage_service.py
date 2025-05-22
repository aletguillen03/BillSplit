import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import sqlite3
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageService:
    """Servicio para manejar el almacenamiento de datos."""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_storage_dir()
        self.db_path = Path(self.storage_dir) / 'bills.db'
        self._init_storage()
    
    def _ensure_storage_dir(self):
        """Ensure the storage directory exists."""
        try:
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
        except Exception as e:
            self.logger.error(f"Error creating storage directory: {str(e)}")
            raise
    
    def _init_storage(self):
        """Inicializa el almacenamiento."""
        try:
            # Crear directorio de datos si no existe
            self.storage_dir.mkdir(exist_ok=True)
            
            # Inicializar base de datos
            with self._get_db() as (conn, cur):
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        total REAL NOT NULL,
                        items TEXT NOT NULL,
                        metadata TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando almacenamiento: {str(e)}")
            raise
    
    @contextmanager
    def _get_db(self):
        """Context manager para manejar conexiones a la base de datos."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            cur = conn.cursor()
            yield conn, cur
        finally:
            if conn:
                conn.close()
    
    def save_bill(self, bill_data: Dict[str, Any]) -> str:
        """Save bill data to a JSON file."""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bill_{timestamp}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Add metadata
            bill_data['timestamp'] = timestamp
            bill_data['created_at'] = datetime.now().isoformat()
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(bill_data, f, ensure_ascii=False, indent=2)
                
            return filename
        except Exception as e:
            self.logger.error(f"Error saving bill: {str(e)}")
            raise
    
    def load_bill(self, filename: str) -> Optional[Dict]:
        """Load bill data from a JSON file."""
        try:
            filepath = os.path.join(self.storage_dir, filename)
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading bill: {str(e)}")
            return None
    
    def list_bills(self) -> List[Dict]:
        """List all saved bills with their metadata."""
        try:
            bills = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        bill_data = json.load(f)
                        bills.append({
                            'filename': filename,
                            'timestamp': bill_data.get('timestamp'),
                            'created_at': bill_data.get('created_at'),
                            'total': sum(bill_data.get('items', {}).values())
                        })
            return sorted(bills, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            self.logger.error(f"Error listing bills: {str(e)}")
            return []
    
    def delete_bill(self, filename: str) -> bool:
        """Delete a bill file."""
        try:
            filepath = os.path.join(self.storage_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting bill: {str(e)}")
            return False
    
    def get_bill(self, bill_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una factura por su ID.
        
        Args:
            bill_id: ID de la factura
            
        Returns:
            Datos de la factura o None si no existe
        """
        try:
            with self._get_db() as (conn, cur):
                cur.execute('SELECT * FROM bills WHERE id = ?', (bill_id,))
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'date': row[1],
                        'total': row[2],
                        'items': json.loads(row[3]),
                        'metadata': json.loads(row[4]) if row[4] else {}
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo factura: {str(e)}")
            raise
    
    def get_all_bills(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las facturas.
        
        Returns:
            Lista de facturas
        """
        try:
            with self._get_db() as (conn, cur):
                cur.execute('SELECT * FROM bills ORDER BY date DESC')
                return [{
                    'id': row[0],
                    'date': row[1],
                    'total': row[2],
                    'items': json.loads(row[3]),
                    'metadata': json.loads(row[4]) if row[4] else {}
                } for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo facturas: {str(e)}")
            raise
    
    def clear_all_bills(self) -> None:
        """Elimina todas las facturas."""
        try:
            with self._get_db() as (conn, cur):
                cur.execute('DELETE FROM bills')
                conn.commit()
        except Exception as e:
            logger.error(f"Error limpiando facturas: {str(e)}")
            raise
    
    def backup_data(self, backup_path: Path) -> None:
        """
        Crea una copia de seguridad de los datos.
        
        Args:
            backup_path: Ruta donde guardar la copia
        """
        try:
            # Crear directorio de backup si no existe
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar base de datos
            with self._get_db() as (conn, _):
                conn.backup(sqlite3.connect(str(backup_path)))
        except Exception as e:
            logger.error(f"Error creando backup: {str(e)}")
            raise
    
    def restore_from_backup(self, backup_path: Path) -> None:
        """
        Restaura datos desde una copia de seguridad.
        
        Args:
            backup_path: Ruta de la copia de seguridad
        """
        try:
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
            
            # Restaurar base de datos
            with sqlite3.connect(str(backup_path)) as backup_conn:
                with self._get_db() as (conn, _):
                    backup_conn.backup(conn)
        except Exception as e:
            logger.error(f"Error restaurando backup: {str(e)}")
            raise 