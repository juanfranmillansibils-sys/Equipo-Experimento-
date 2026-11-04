"""Paso 2 - Perfilar el dato crudo.

Lee los CSV crudos sin modificarlos y genera una tabla de perfilado con una
fila por variable, para cada tabla. No limpia ni corrige nada.

Uso (desde la raíz del repo):
    python codigo/02_perfilado.py
"""
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos"
TABLAS = RAIZ / "resultados" / "tablas"

ARCHIVOS = {
    "encuesta": CRUDOS / "resultado_encuesta.csv",
    "juego": CRUDOS / "resultado_juego.csv",
}

# Reglas de rango para las variables que las tienen. Lo que cae fuera se cuenta.
RANGOS = {
    "edad": (17, 99),
    "escala": (1, 5),
    "monto": (0, 100),
    "conocimiento": (1, 5),
    "ronda": (2, 3),
}


def regla(nombre):
    n = nombre.lower()
    if "años" in n or "edad" in n:
        return RANGOS["edad"]
    if "monto" in n and "conservado" not in n and "diferencia" not in n:
        return RANGOS["monto"]
    if "conocimiento previo" in n:
        return RANGOS["conocimiento"]
    if "ronda cara a cara" in n:
        return RANGOS["ronda"]
    if "escala" in n or n.startswith("cuando") or "¿cuánto" in n or "¿qué tan" in n:
        return RANGOS["escala"]
    return None


def normalizar(s):
    return re.sub(r"\s+", "", str(s)).lower()


def perfilar(df, nombre_tabla, alias_referencia=None):
    filas = []
    for col in df.columns:
        serie = df[col].astype(str)
        vacios = serie.str.strip().eq("")
        valores = serie[~vacios]
        numericos = pd.to_numeric(valores, errors="coerce")
        es_numerica = len(valores) > 0 and numericos.notna().all()

        fuera_rango = ""
        rango = regla(col)
        if rango and es_numerica:
            lo, hi = rango
            fuera_rango = int(((numericos < lo) | (numericos > hi)).sum())

        espacios = int(valores.str.contains(r"^\s|\s$|\s{2,}").sum())

        # Variantes: valores distintos que son iguales al normalizar (mayúsculas y espacios)
        grupos = valores.groupby(valores.map(normalizar)).nunique()
        variantes = int((grupos > 1).sum())

        filas.append({
            "tabla": nombre_tabla,
            "variable": col,
            "tipo": "numerica" if es_numerica else "texto",
            "filas": len(df),
            "valores_distintos": int(valores.nunique()),
            "faltantes": int(vacios.sum()),
            "minimo": numericos.min() if es_numerica else "",
            "maximo": numericos.max() if es_numerica else "",
            "fuera_de_rango": fuera_rango,
            "con_espacios_irregulares": espacios,
            "variantes_de_escritura": variantes,
            "unico": bool(valores.is_unique) if len(valores) else "",
            "sin_coincidencia_exacta_con_encuesta": (
                int((~valores.isin(alias_referencia)).sum())
                if alias_referencia is not None and ("alias" in col.lower() or "receptor" in col.lower())
                else ""
            ),
        })
    return pd.DataFrame(filas)


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    perfiles = []
    alias_encuesta = None
    for nombre, ruta in ARCHIVOS.items():
        if not ruta.exists():
            raise SystemExit(f"No encuentro {ruta}")
        # dtype=str: se perfila el texto tal cual está en el archivo
        df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
        print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
        if nombre == "encuesta":
            alias_encuesta = set(df["Código de participante"])
        perfiles.append(perfilar(df, nombre, alias_encuesta if nombre == "juego" else None))
    salida = pd.concat(perfiles, ignore_index=True)
    destino = TABLAS / "perfilado_crudo.csv"
    salida.to_csv(destino, index=False, encoding="utf-8")
    print("Guardado:", destino)


if __name__ == "__main__":
    main()