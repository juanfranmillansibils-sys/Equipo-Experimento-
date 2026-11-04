"""Paso 1 - Importar los datos crudos.

Lee los CSV de datos/crudos/ sin modificarlos y deja registro de cada archivo:
tamaño, huella digital (SHA-256), filas, columnas y problemas de lectura.
La huella permite comprobar después que el crudo no cambió.

Uso (desde la raíz del repo):
    python codigo/01_importacion.py
"""
import hashlib
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos"
TABLAS = RAIZ / "resultados" / "tablas"

ARCHIVOS = [
    "resultado_encuesta.csv",
    "resultado_juego.csv",
]


def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def registrar(ruta):
    # Se lee como texto para no transformar nada
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8")
    return {
        "archivo": ruta.name,
        "ruta": str(ruta.relative_to(RAIZ)),
        "bytes": ruta.stat().st_size,
        "sha256": huella(ruta),
        "filas": len(df),
        "columnas": df.shape[1],
        "nombres_de_columnas": " | ".join(df.columns),
        "fecha_importacion": date.today().isoformat(),
    }


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    registros = []
    for nombre in ARCHIVOS:
        ruta = CRUDOS / nombre
        if not ruta.exists():
            raise SystemExit(f"No encuentro {ruta}")
        r = registrar(ruta)
        print(f"{r['archivo']}: {r['filas']} filas, {r['columnas']} columnas, sha256 {r['sha256'][:12]}...")
        registros.append(r)
    destino = TABLAS / "importacion_registro.csv"
    pd.DataFrame(registros).to_csv(destino, index=False, encoding="utf-8")
    print("Guardado:", destino)


if __name__ == "__main__":
    main()