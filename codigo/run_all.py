"""Ejecuta los pasos en orden, desde el crudo hasta el análisis."""
import subprocess
import sys
from pathlib import Path

PASOS = sorted(Path(__file__).parent.glob("0*.py"))

for paso in PASOS:
    print(f"--> {paso.name}")
    subprocess.run([sys.executable, str(paso)], check=True)
