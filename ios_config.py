from kivy_ios.toolchain import ToolchainCL
import os

# Configuración del proyecto
project_name = 'BillSplitter'
bundle_id = 'com.yourdomain.billsplitter'
version = '1.0'

# Configuración específica para iOS
ios_config = {
    'name': project_name,
    'version': version,
    'bundle_id': bundle_id,
    'orientation': 'portrait',
    'icon': 'resources/icon.png',
    'splash': 'resources/splash.png',
    'permissions': [
        'camera',
        'photo_library'
    ],
    'requirements': [
        'kivy',
        'pillow',
        'pytesseract'
    ],
    'source_dir': 'src',
    'main_file': 'main.py'
}

# Inicializar el toolchain
toolchain = ToolchainCL()

# Configurar el proyecto
toolchain.set_project_name(project_name)
toolchain.set_bundle_id(bundle_id)
toolchain.set_version(version)

# Configurar las dependencias
for req in ios_config['requirements']:
    toolchain.add_recipe(req)

# Construir el proyecto
toolchain.build_all() 