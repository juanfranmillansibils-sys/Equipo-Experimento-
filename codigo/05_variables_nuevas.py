"""Paso 5 - Generar nueva información.

Crea variables nuevas a partir de la unión, con reglas explícitas. Cada variable
queda documentada en documentos/diccionario_variables.csv. No se modifica ningún
dato original: las variables nuevas se agregan como columnas.

Uso (desde la raíz del repo):
    python codigo/05_variables_nuevas.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FINALES = RAIZ / "datos" / "finales"
TABLAS = RAIZ / "resultados" / "tablas"


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(FINALES / "union.csv", dtype={"alias": str})

    # Solo la primera respuesta de cada persona entra en el análisis (decisión del equipo)
    df["incluir_analisis"] = df["posible_doble"].isna().astype(int)

    # Índice social: promedio simple de tres escalas de 1 a 5
    df["indice_social"] = df[["generosidad", "justicia", "consideracion_otros"]].mean(axis=1).round(2)

    # Índice competitivo: promedio simple de competitividad y beneficio propio (1 a 5)
    df["indice_competitivo"] = df[["competitividad", "beneficio_propio"]].mean(axis=1).round(2)

    # Cambio del monto entre la ronda anónima y la cara a cara (solo quienes jugaron)
    jugo = df["entregado_visible"].notna()
    cambio = pd.Series("sin juego", index=df.index)
    cambio[jugo & (df["diferencia"] > 0)] = "aumenta"
    cambio[jugo & (df["diferencia"] == 0)] = "igual"
    cambio[jugo & (df["diferencia"] < 0)] = "disminuye"
    df["cambio_monto"] = cambio

    # Grupo de edad
    df["grupo_edad"] = pd.cut(df["edad"], bins=[18, 20, 22, 100],
                              labels=["19-20", "21-22", "23 o más"]).astype(str)

    filas = []
    for var in ["incluir_analisis", "cambio_monto", "grupo_edad"]:
        for valor, n in df[var].value_counts(dropna=False).items():
            filas.append({"variable": var, "valor": valor, "filas": int(n)})
    pd.DataFrame(filas).to_csv(TABLAS / "variables_nuevas_conteos.csv", index=False, encoding="utf-8")
    df.to_csv(FINALES / "analisis.csv", index=False, encoding="utf-8")
    print(f"Variables nuevas creadas. Filas: {len(df)}, incluidas en el análisis: {int(df['incluir_analisis'].sum())}")


if __name__ == "__main__":
    main()
