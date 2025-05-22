# Bill Splitter

Aplicación móvil para dividir cuentas de restaurante usando OCR y procesamiento de imágenes.

## Características

- Captura de tickets mediante cámara
- Procesamiento OCR de tickets
- Asignación de ítems a comensales
- Cálculo automático de propinas
- Generación de resúmenes individuales
- Historial de cuentas
- Compartir resúmenes por diferentes medios

## Requisitos

- Python 3.11+
- Tesseract OCR
- Dependencias listadas en requirements.txt

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Unix/macOS
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Instalar Tesseract OCR:
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Estructura del Proyecto

```
bill_splitter/
├── src/
│   ├── models/      # Clases de datos
│   ├── services/    # Lógica de negocio
│   ├── ui/          # Interfaz de usuario
│   └── utils/       # Utilidades
├── tests/           # Tests unitarios
└── resources/       # Recursos estáticos
```

## Uso

1. Ejecutar la aplicación:
   ```bash
   python src/main.py
   ```
2. Tomar foto del ticket
3. Revisar y corregir items detectados
4. Asignar items a comensales
5. Generar y compartir resúmenes

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request 