"""Ejecuta todos los pasos en orden, sin pasos manuales.

Uso (desde la raíz del repo):
    python codigo/run_all.py

Si un paso falla, se detiene y muestra qué paso falló.
"""
import subprocess
import sys
from pathlib import Path

CODIGO = Path(__file__).resolve().parent
RAIZ = CODIGO.parent
PASOS = sorted(CODIGO.glob("0[0-9]*_*.py"))  # incluye 05b_aumentacion.py


def main():
    print(f"Repo: {RAIZ}")
    for paso in PASOS:
        print(f"\n=== {paso.name} ===")
        r = subprocess.run([sys.executable, str(paso)], cwd=RAIZ)
        if r.returncode != 0:
            print(f"ERROR en {paso.name}. Se detiene la ejecución.")
            sys.exit(r.returncode)
    print("\nTodos los pasos corrieron sin errores.")


if __name__ == "__main__":
    main()