"""Paso 6 - Explorar: visualizar y modelar.

Usa solo las filas con incluir_analisis = 1: la segunda respuesta de una persona
duplicada queda afuera. Los jugadores son 16, así que los resultados son
exploratorios: muestran patrones, no los demuestran, y no permiten inferir causalidad.
Se reportan también los resultados que no muestran nada.

Uso (desde la raíz del repo):
    python codigo/06_analisis.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
FINALES = RAIZ / "datos" / "finales"
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICOS = RAIZ / "resultados" / "graficos"

VARS = ["edad", "indice_social", "indice_competitivo", "generosidad", "justicia",
        "consideracion_otros", "beneficio_propio", "competitividad", "influencia_social",
        "grado_conocimiento"]
MONTOS = ["entregado_anonimo", "entregado_visible", "diferencia"]


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(FINALES / "analisis.csv", dtype={"alias": str})
    df = df[df["incluir_analisis"] == 1].copy()
    jug = df[df["entregado_visible"].notna()].copy()
    print(f"Personas en el análisis: {len(df)}. Jugadores: {len(jug)}.")

    # 1. Descriptivos (encuesta para todos; juego solo para jugadores)
    cols = ["edad", "indice_social", "indice_competitivo"] + MONTOS + ["grado_conocimiento"]
    desc = df[cols].describe().T.round(2).reset_index().rename(columns={"index": "variable"})
    desc.to_csv(TABLAS / "exp_descriptivos.csv", index=False, encoding="utf-8")

    # 2. Ronda anónima vs cara a cara (prueba pareada, solo jugadores)
    w = stats.wilcoxon(jug["entregado_visible"], jug["entregado_anonimo"])
    comparacion = pd.DataFrame([{
        "n_jugadores": len(jug),
        "media_anonimo": round(jug["entregado_anonimo"].mean(), 1),
        "media_visible": round(jug["entregado_visible"].mean(), 1),
        "diferencia_media": round(jug["diferencia"].mean(), 1),
        "aumenta": int((jug["diferencia"] > 0).sum()),
        "igual": int((jug["diferencia"] == 0).sum()),
        "disminuye": int((jug["diferencia"] < 0).sum()),
        "p_wilcoxon": round(w.pvalue, 3),
    }])
    comparacion.to_csv(TABLAS / "exp_anonimo_vs_visible.csv", index=False, encoding="utf-8")

    # 3. Correlaciones de Spearman (solo jugadores). Exploratorio: sin corregir por pruebas múltiples.
    filas = []
    for v in VARS:
        for y in MONTOS:
            r, p = stats.spearmanr(jug[v], jug[y])
            filas.append({"variable": v, "monto": y, "rho": round(r, 2), "p": round(p, 3)})
    corr = pd.DataFrame(filas)
    corr.to_csv(TABLAS / "exp_correlaciones.csv", index=False, encoding="utf-8")

    # 4. Modelo lineal simple (mínimos cuadrados): diferencia ~ índice social + índice competitivo
    X = np.column_stack([np.ones(len(jug)), jug["indice_social"], jug["indice_competitivo"]])
    y = jug["diferencia"].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    modelo = pd.DataFrame([
        {"termino": "constante", "coeficiente": round(beta[0], 2)},
        {"termino": "indice_social", "coeficiente": round(beta[1], 2)},
        {"termino": "indice_competitivo", "coeficiente": round(beta[2], 2)},
        {"termino": "R2", "coeficiente": round(r2, 2)},
    ])
    modelo.to_csv(TABLAS / "exp_modelo_diferencia.csv", index=False, encoding="utf-8")

    # 5. Diferencias por grupo (solo jugadores)
    partes = []
    for var in ["sexo", "grupo_edad", "grado_conocimiento"]:
        g = jug.groupby(var).agg(
            n=("alias", "count"),
            anonimo_media=("entregado_anonimo", "mean"),
            visible_media=("entregado_visible", "mean"),
            diferencia_media=("diferencia", "mean"),
        ).round(1).reset_index().rename(columns={var: "grupo"})
        g.insert(0, "variable", var)
        partes.append(g)
    pd.concat(partes, ignore_index=True).to_csv(TABLAS / "exp_por_grupo.csv", index=False, encoding="utf-8")

    # 6. Casos extremos (solo jugadores): los tres mayores y menores cambios
    extremos = pd.concat([jug.nlargest(3, "diferencia"), jug.nsmallest(3, "diferencia")])
    extremos[["alias", "receptor_anonimo", "entregado_anonimo", "receptor_visible",
              "entregado_visible", "diferencia", "observaciones"]].to_csv(
        TABLAS / "exp_extremos.csv", index=False, encoding="utf-8")

    # 7. Gráficos
    fig, ax = plt.subplots(figsize=(6, 4))
    for _, r in jug.iterrows():
        ax.plot([0, 1], [r["entregado_anonimo"], r["entregado_visible"]], color="gray", alpha=0.6)
    ax.set_xticks([0, 1], ["Anónimo (R1)", "Cara a cara"])
    ax.set_ylabel("Monto entregado")
    ax.set_title("Monto entregado por jugador (16)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "exp_anonimo_vs_visible.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(jug["indice_social"], jug["entregado_anonimo"], label="Anónimo (R1)")
    ax.scatter(jug["indice_social"], jug["entregado_visible"], label="Cara a cara")
    ax.set_xlabel("Índice social (1 a 5)")
    ax.set_ylabel("Monto entregado")
    ax.legend()
    ax.set_title("Índice social y monto entregado")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "exp_indice_social_vs_monto.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(jug["diferencia"], bins=range(-30, 65, 10), edgecolor="black")
    ax.set_xlabel("Cara a cara − anónimo")
    ax.set_ylabel("Jugadores")
    ax.set_title("Diferencia entre rondas")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "exp_diferencia_hist.png", dpi=150)
    plt.close(fig)

    print(comparacion.to_string(index=False))
    print(f"R2 del modelo: {r2:.2f}")


if __name__ == "__main__":
    main()
