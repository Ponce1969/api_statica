# conftest.py
import sys
from pathlib import Path

# Añade el directorio raíz del proyecto al sys.path
# Esto permite que Pytest encuentre el módulo 'app'
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
