"""Paso 3 - Ordenar y limpiar.

Lee los CSV crudos sin modificarlos y genera tablas limpias en datos/finales/.

Reglas:
- Alias: se comparan sin espacios y sin mayúsculas, y se reemplazan por el código
  exacto de la encuesta. Cada reemplazo queda en limpieza_cambios.csv.
- Lo que no se puede resolver con certeza NO se cambia: se marca para que el equipo decida.
- No se borra ninguna fila. Los posibles duplicados se marcan, no se eliminan.
- Antes y después: el conteo de filas queda en limpieza_conteos.csv.

Uso (desde la raíz del repo):
    python codigo/03_limpieza.py
"""
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos"
FINALES = RAIZ / "datos" / "finales"
TABLAS = RAIZ / "resultados" / "tablas"

COD = "Código de participante"

# Verificados por el equipo. La encuesta es anónima, así que esto no se puede
# detectar solo con los datos. Se conserva la primera respuesta de cada par.
DOBLES_CONFIRMADOS = [("pechu", "pechu542")]
DISTINTAS_VERIFICADAS = [("Cami555", "leon695"), ("superatomnicoto585", "Trader22"),
                         ("superatomnicoto585", "Pato363"), ("Fabri Valverde", "TyrionL"),
                         ("Trader22", "Pato363")]

ENC_NUM = ["¿Cuántos años tenés?"] + [c for c in [
    "En una escala de 1 a 5, ¿qué tan generoso/a te considerás con otras personas?",
    "En una escala de 1 a 5, ¿qué tan importante es para vos actuar de forma justa cuando una decisión también afecta a otra persona?",
    "Cuando tomás una decisión que también afecta a otra persona, ¿cuánto tenés en cuenta cómo puede afectarla?",
    "Cuando tomás una decisión, ¿qué tan importante es para vos obtener el mejor resultado posible para vos mismo/a?",
    "En una escala de 1 a 5, ¿qué tan competitivo/a te considerás frente a otras personas?",
    "¿Cuánto considerás que influye la opinión de otras personas en las decisiones que tomás?",
]]
JUE_ALIAS = ["Alias dictador", "R1 - Receptor anónimo", "CC - Receptor"]
JUE_NUM = ["ID", "R1 - Monto entregado (anónimo)", "R1 - Monto conservado", "Ronda cara a cara",
           "CC - Monto entregado", "CC - Monto conservado", "Conocimiento previo (1-5)",
           "Diferencia CC - R1"]


# Nombres finales (ver documentos/diccionario_variables.csv). Se aplican al final.
ENC_RENOMBRAR = {
    COD: "alias",
    "Marca temporal": "marca_temporal",
    "¿Cuántos años tenés?": "edad",
    "Sexo Biológico": "sexo",
    ENC_NUM[1]: "generosidad",
    ENC_NUM[2]: "justicia",
    ENC_NUM[3]: "consideracion_otros",
    ENC_NUM[4]: "beneficio_propio",
    ENC_NUM[5]: "competitividad",
    ENC_NUM[6]: "influencia_social",
}
JUE_RENOMBRAR = {
    "ID": "id_ficha",
    "Alias dictador (limpio)": "alias",
    "R1 - Monto entregado (anónimo)": "entregado_anonimo",
    "R1 - Monto conservado": "conservado_anonimo",
    "R1 - Receptor anónimo (limpio)": "receptor_anonimo",
    "Ronda cara a cara": "ronda",
    "Ronda inferida": "ronda_inferida",
    "CC - Receptor (limpio)": "receptor_visible",
    "CC - Monto entregado": "entregado_visible",
    "CC - Monto conservado": "conservado_visible",
    "Conocimiento previo (1-5)": "grado_conocimiento",
    "Conocimiento (etiqueta)": "conocimiento_etiqueta",
    "Diferencia CC - R1": "diferencia",
    "Observaciones": "observaciones",
}


def norm(s):
    return re.sub(r"\s+", "", str(s)).lower()


def emparejar_dobles(enc, jugo_codigos):
    """Pares con misma edad y sexo y al menos 7 de 8 respuestas iguales.
    No se marca el par si los dos jugaron, porque son personas distintas."""
    cols = ["¿Cuántos años tenés?", "Sexo Biológico"] + ENC_NUM[1:]
    filas = enc.to_dict("records")
    pares = []
    for i in range(len(filas)):
        for j in range(i + 1, len(filas)):
            a, b = filas[i], filas[j]
            if a["¿Cuántos años tenés?"] != b["¿Cuántos años tenés?"] or a["Sexo Biológico"] != b["Sexo Biológico"]:
                continue
            iguales = sum(a[c] == b[c] for c in cols)
            if iguales < 7:
                continue
            if a["clave"] in jugo_codigos and b["clave"] in jugo_codigos:
                continue
            pares.append({"codigo_1": a[COD], "marca_1": a["Marca temporal"],
                          "codigo_2": b[COD], "marca_2": b["Marca temporal"],
                          "respuestas_iguales": f"{iguales}/{len(cols)}"})
    return pd.DataFrame(pares)


def main():
    FINALES.mkdir(parents=True, exist_ok=True)
    TABLAS.mkdir(parents=True, exist_ok=True)
    enc = pd.read_csv(CRUDOS / "resultado_encuesta.csv", dtype=str, keep_default_na=False)
    jue = pd.read_csv(CRUDOS / "resultado_juego.csv", dtype=str, keep_default_na=False)
    conteos = {"encuesta_antes": len(enc), "juego_antes": len(jue)}
    cambios = []

    # 1. Alias: reemplazo por el código exacto de la encuesta
    canon = {norm(c): c for c in enc[COD]}
    enc["clave"] = enc[COD].map(norm)
    for col in JUE_ALIAS:
        nuevo = []
        for _, r in jue.iterrows():
            original = r[col]
            limpio = canon.get(norm(original), original)
            if limpio != original:
                cambios.append({"tabla": "juego", "ID": r["ID"], "columna": col,
                                "original": original, "limpio": limpio,
                                "motivo": "alias normalizado al código de la encuesta"})
            nuevo.append(limpio)
        jue[col + " (limpio)"] = nuevo

    # 2. Filas con observaciones de transcripción: se revisan, no se cambian aquí
    revisar = jue[jue["Observaciones"].str.strip() != ""]
    for _, r in revisar.iterrows():
        cambios.append({"tabla": "juego", "ID": r["ID"], "columna": "Observaciones",
                        "original": r["Observaciones"], "limpio": "",
                        "motivo": "revisar: corrección o dato dudoso de transcripción (decide el equipo)"})

    # 3. Columnas derivadas: se verifican, no se modifican
    dif_mal = jue[jue["Diferencia CC - R1"].astype(int) != (
        jue["CC - Monto entregado"].astype(int) - jue["R1 - Monto entregado (anónimo)"].astype(int))]
    cons_mal = jue[jue["R1 - Monto conservado"].astype(int) != (
        100 - jue["R1 - Monto entregado (anónimo)"].astype(int))]
    conteos["diferencias_CC_R1_incorrectas"] = len(dif_mal)
    conteos["monto_conservado_R1_incorrecto"] = len(cons_mal)

    # 4. Dobles: la detección automática solo propone candidatos. La decisión
    # la toma el equipo y queda en DOBLES_CONFIRMADOS. No se borra ninguna fila.
    jugo_claves = set(jue["Alias dictador (limpio)"].map(norm))
    candidatos = emparejar_dobles(enc, jugo_claves)
    candidatos["estado"] = [
        "verificado: personas distintas"
        if (p1, p2) in DISTINTAS_VERIFICADAS or (p2, p1) in DISTINTAS_VERIFICADAS
        else "pendiente"
        for p1, p2 in zip(candidatos["codigo_1"], candidatos["codigo_2"])]
    marca = dict(zip(enc[COD], enc["Marca temporal"]))
    confirmados = []
    for a, b in DOBLES_CONFIRMADOS:
        primera, segunda = sorted([a, b], key=lambda c: marca[c])
        confirmados.append({"codigo_1": primera, "marca_1": marca[primera],
                            "codigo_2": segunda, "marca_2": marca[segunda],
                            "respuestas_iguales": "",
                            "estado": "verificado: misma persona (se conserva la primera)"})
    dobles = pd.concat([pd.DataFrame(confirmados), candidatos], ignore_index=True)
    enc["posible_doble"] = ""
    for a, b in DOBLES_CONFIRMADOS:
        segunda = sorted([a, b], key=lambda c: marca[c])[1]
        enc.loc[enc[COD] == segunda, "posible_doble"] = sorted([a, b], key=lambda c: marca[c])[0]
    dobles.to_csv(TABLAS / "posibles_dobles.csv", index=False, encoding="utf-8")

    # 5. Tipos numéricos en las tablas finales (el crudo sigue igual)
    for c in ENC_NUM:
        enc[c] = pd.to_numeric(enc[c], errors="coerce")
    for c in JUE_NUM:
        jue[c] = pd.to_numeric(jue[c], errors="coerce")

    # 6. Nombres finales. Se quitan las columnas de alias originales (quedan las limpias).
    enc = enc.drop(columns=["clave"]).rename(columns=ENC_RENOMBRAR)
    jue = jue.drop(columns=JUE_ALIAS).rename(columns=JUE_RENOMBRAR)
    enc.to_csv(FINALES / "encuesta_limpia.csv", index=False, encoding="utf-8")
    jue.to_csv(FINALES / "juego_limpio.csv", index=False, encoding="utf-8")

    conteos["encuesta_despues"] = len(enc)
    conteos["juego_despues"] = len(jue)
    conteos["cambios_de_valor"] = sum(1 for c in cambios if c["motivo"].startswith("alias"))
    conteos["filas_a_revisar_juego"] = len(revisar)
    conteos["posibles_dobles_encuesta"] = len(dobles)
    pd.DataFrame(cambios).to_csv(TABLAS / "limpieza_cambios.csv", index=False, encoding="utf-8")
    pd.DataFrame([conteos]).T.reset_index().rename(
        columns={"index": "concepto", 0: "valor"}).to_csv(
        TABLAS / "limpieza_conteos.csv", index=False, encoding="utf-8")
    print("Limpieza lista:", conteos)


if __name__ == "__main__":
    main()