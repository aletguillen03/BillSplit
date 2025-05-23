from kivy_ios.toolchain import ToolchainCL
import os

# Configuración del proyecto
project_name = 'BillSplitter'
bundle_id = 'com.yourdomain.billsplitter'
version = '1.0'

# Inicializar el toolchain
toolchain = ToolchainCL()

# Configurar el proyecto
toolchain.set_project_name(project_name)
toolchain.set_bundle_id(bundle_id)
toolchain.set_version(version)

# Configurar las dependencias
toolchain.add_recipe('python3')
toolchain.add_recipe('kivy')
toolchain.add_recipe('pillow')
toolchain.add_recipe('pytesseract')
toolchain.add_recipe('numpy')
toolchain.add_recipe('sqlalchemy')
toolchain.add_recipe('reportlab')
toolchain.add_recipe('opencv')

# Configurar opciones adicionales
toolchain.set_arch('arm64')  # Para dispositivos iOS modernos
toolchain.set_deployment_target('13.0')  # iOS 13.0 o superior

# Construir el proyecto
toolchain.build_all() 