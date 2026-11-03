import pandas as pd
import numpy as np

# Definicion del diccionario crudo recabado en la dinamica
datos_objetos = {
    "objeto_id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
    "objeto": [
        "cubo rubik", "peluche", "hexagono", "libro", "cable",
        "lapicera", "caja plastica", "tapa plastico", "lentes",
    ],
    "forma": [
        "cuadrado", np.nan, "hexagonal", "rectangular", "cilindrico",
        "cilindrico", np.nan, "cilindrico", np.nan,
    ],
    "textura": [
        "liso", "liso", "liso", "liso", np.nan,
        np.nan, np.nan, np.nan, "liso",
    ],
    "rigidez": [
        np.nan, "blando", "rigido", np.nan, "rigido",
        "rigido", "blando", "rigido", np.nan,
    ],
    "movimiento": [True, False, False, False, False, False, False, False, False],
    "movil": [False, False, False, False, False, False, True, False, False],
    "ruidoso": [False, False, False, False, False, False, True, False, False],
    "elastico": [False, False, False, False, False, False, False, False, True],
}

# transformacion a dataframe
df_objetos = pd.DataFrame(datos_objetos)

# Convertir tipos categoricos y ordinales
df_objetos["forma"] = df_objetos["forma"].astype("category")
df_objetos["textura"] = df_objetos["textura"].astype("category")
df_objetos["rigidez"] = pd.Categorical(
    df_objetos["rigidez"],
    categories=["blando", "medio", "rigido"],
    ordered=True,
)

# Mostrar la tabla completa, sin cortar columnas
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
print(df_objetos.to_string(index=False))
