"""Paso 5 (aumentación) - Generar filas simuladas.

Crea 200 filas simuladas a partir de las personas del análisis reales: remuestreo
con reemplazo de filas completas y ruido gaussiano pequeño en las variables
numéricas. Después se ajustan a los rangos válidos y se recalculan las
columnas derivadas.

ADVERTENCIA: la aumentación no agrega información. Las filas simuladas son copias
perturbadas de las reales. Sirve para probar el código y el modelo, no para
inferencia. La inferencia se hace con los datos reales (ver 06_analisis.py).
Las filas simuladas se marcan con origen = "simulado".

Uso (desde la raíz del repo):
    python codigo/05b_aumentacion.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FINALES = RAIZ / "datos" / "finales"
TABLAS = RAIZ / "resultados" / "tablas"

N_SIMULADAS = 200
RUIDO = 0.1          # ruido = 10% del desvío de cada variable
SEMILLA = 20261112   # reproducible

ESCALAS = ["generosidad", "justicia", "consideracion_otros", "beneficio_propio",
           "competitividad", "influencia_social", "grado_conocimiento"]
MONTOS = ["entregado_anonimo", "entregado_visible", "conservado_anonimo", "conservado_visible"]
NUMERICAS = ["edad"] + ESCALAS + MONTOS
RANGOS = {**{e: (1, 5) for e in ESCALAS}, **{m: (0, 100) for m in MONTOS}, "edad": (17, 99)}


def aumentar(real, n, rng):
    idx = rng.integers(0, len(real), n)
    sim = real.iloc[idx].reset_index(drop=True).copy()
    for v in NUMERICAS:
        desvio = real[v].std()
        sim[v] = sim[v] + rng.normal(0, RUIDO * desvio, n)
        lo, hi = RANGOS[v]
        sim[v] = sim[v].round().clip(lo, hi)
    # columnas derivadas, recalculadas para que sean coherentes
    sim["conservado_anonimo"] = 100 - sim["entregado_anonimo"]
    sim["conservado_visible"] = 100 - sim["entregado_visible"]
    sim["diferencia"] = sim["entregado_visible"] - sim["entregado_anonimo"]
    sim["indice_social"] = sim[["generosidad", "justicia", "consideracion_otros"]].mean(axis=1).round(2)
    sim["indice_competitivo"] = sim[["competitividad", "beneficio_propio"]].mean(axis=1).round(2)
    sim["grupo_edad"] = pd.cut(sim["edad"], bins=[18, 20, 22, 100],
                               labels=["19-20", "21-22", "23 o más"]).astype(str)
    jugo = sim["entregado_visible"].notna()
    cambio = pd.Series("sin juego", index=sim.index)
    cambio[jugo & (sim["diferencia"] > 0)] = "aumenta"
    cambio[jugo & (sim["diferencia"] == 0)] = "igual"
    cambio[jugo & (sim["diferencia"] < 0)] = "disminuye"
    sim["cambio_monto"] = cambio
    sim["incluir_analisis"] = 1
    sim["origen"] = "simulado"
    return sim


def main():
    FINALES.mkdir(parents=True, exist_ok=True)
    TABLAS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(FINALES / "analisis.csv", dtype={"alias": str})
    real = df[df["incluir_analisis"] == 1].copy()
    rng = np.random.default_rng(SEMILLA)

    sim = aumentar(real, N_SIMULADAS, rng)
    sim = sim.drop(columns=["alias", "posible_doble", "receptor_anonimo", "receptor_visible",
                            "observaciones", "id_ficha", "marca_temporal"], errors="ignore")
    sim.to_csv(FINALES / "simulados.csv", index=False, encoding="utf-8")

    # Control: las medias de las simuladas tienen que parecerse a las reales
    variables = ["edad", "indice_social", "indice_competitivo", "entregado_anonimo", "diferencia"]
    control = pd.DataFrame({
        "variable": variables,
        "media_real": [round(real[v].mean(), 2) for v in variables],
        "media_simulada": [round(sim[v].mean(), 2) for v in variables],
    })
    control.to_csv(TABLAS / "aumentacion_control_medias.csv", index=False, encoding="utf-8")
    print(f"Filas reales: {len(real)}. Filas simuladas: {len(sim)}.")
    print(control.to_string(index=False))


if __name__ == "__main__":
    main()