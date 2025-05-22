from setuptools import setup

setup(
    name='BillSplitter',
    version='1.0',
    description='App para dividir cuentas',
    author='Alejo Guillen',
    author_email='your.email@example.com',
    packages=['src'],
    install_requires=[
        'kivy==2.2.1',
        'pytesseract==0.3.10',
        'Pillow==10.0.0',
        'numpy==1.24.3',
        'python-dotenv==1.0.0',
        'SQLAlchemy==2.0.20',
        'reportlab==4.0.4',
        'plyer==2.1.0'
    ],
) 