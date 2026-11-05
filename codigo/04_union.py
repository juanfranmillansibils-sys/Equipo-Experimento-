"""Paso 4 - Unir tablas.

Une la encuesta (tabla base) con el juego por alias limpio. Reporta la
correspondencia en los dos sentidos: quién está en un lado y no en el otro.

Uso (desde la raíz del repo):
    python codigo/04_union.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FINALES = RAIZ / "datos" / "finales"
TABLAS = RAIZ / "resultados" / "tablas"

COD = "Código de participante"
ALIAS_JUEGO = "Alias dictador (limpio)"


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    enc = pd.read_csv(FINALES / "encuesta_limpia.csv", dtype={COD: str})
    jue = pd.read_csv(FINALES / "juego_limpio.csv", dtype={ALIAS_JUEGO: str})

    union = enc.merge(jue, how="left", left_on=COD, right_on=ALIAS_JUEGO, indicator=True,
                      validate="one_to_one")
    union["en_juego"] = union["_merge"].eq("both")
    union = union.drop(columns=["_merge"])

    solo_encuesta = int((~union["en_juego"]).sum())
    solo_juego = int((~jue[ALIAS_JUEGO].isin(enc[COD])).sum())
    conteos = pd.DataFrame([
        {"concepto": "tipo de unión", "valor": "left (encuesta como base)"},
        {"concepto": "clave", "valor": f"{COD} = {ALIAS_JUEGO}"},
        {"concepto": "filas encuesta", "valor": len(enc)},
        {"concepto": "filas juego", "valor": len(jue)},
        {"concepto": "encuesta con juego", "valor": int(union["en_juego"].sum())},
        {"concepto": "encuesta sin juego", "valor": solo_encuesta},
        {"concepto": "juego sin encuesta", "valor": solo_juego},
        {"concepto": "filas en la unión", "valor": len(union)},
    ])
    union.to_csv(FINALES / "union.csv", index=False, encoding="utf-8")
    conteos.to_csv(TABLAS / "union_conteos.csv", index=False, encoding="utf-8")
    print(conteos.to_string(index=False))


if __name__ == "__main__":
    main()