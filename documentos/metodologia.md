# Metodología

## Paso 1 – Importar los datos crudos

**Encuesta.** Google Forms enviada a todos los alumnos de ambos grupos. Exportación en PDF de la hoja de respuestas (`datos/crudos/Encuesta Equipo _Experimento_ CdD (Respuestas).pdf`), 34 respuestas, marcas temporales desde el 24/9/2026. Variables en `documentos/diccionario_variables.csv`.
- Población invitada: Ambos grupos.

**Juego del Dictador.** Fichas en papel (`documentos/ficha_juego.pdf`), 16 participantes. Transcritas a la plantilla de carga por dos integrantes del equipo para mejorar validación. Ronda 1 asignada por sorteo anónimo, Rondas 2 y 3 (cara a cara) sorteo en la clase.

## Paso 2 – Perfilar el dato crudo
**Método.** `codigo/02_perfilado.py` lee los dos CSV sin modificarlos y genera `resultados/tablas/perfilado_crudo.csv`, con una fila por variable. Registra tipo, valores distintos, faltantes, mínimo y máximo, valores fuera de rango, espacios irregulares y variantes de escritura. Para los alias del juego, cuenta cuántos no coinciden exactamente con los códigos de la encuesta. Reglas de rango: edad 17 a 99, escalas 1 a 5, montos 0 a 100, conocimiento 1 a 5, ronda 2 o 3.

**Resultados.**
- Encuesta: 34 respuestas, 10 variables. Sin faltantes ni valores fuera de rango. Edad entre 19 y 40 años.
- Juego: 16 participantes, 14 variables. Sin faltantes, salvo Observaciones (8 de 16 vacías). Montos entre 0 y 100. Ronda cara a cara: 8 participantes en la ronda 2 y 8 en la 3.
- Alias: 14 de 16 dictadores no coinciden exactamente con la encuesta, por espacios y mayúsculas. Normalizados, todos coinciden.
- Verificaciones adicionales: las columnas derivadas son consistentes en las 16 filas, y las parejas de las rondas 2 y 3 coinciden con el sorteo.

**Problemas que se tratan en el paso 3.** Espacios y mayúsculas en los alias. Receptores con errores de escritura corregidos por suposición (ID 2, 4, 8, 10, 14 y 15). Dos montos poco legibles (ID 6 y 16). Una ronda no marcada (ID 4). Columnas que repiten información (monto conservado, diferencia y etiqueta de conocimiento).

## Paso 3 – Ordenar y limpiar
Se hizo en `codigo/03_limpieza.py`, sin modificar el crudo. Se documenta en dos partes.

**Ordenar (estructura, sin cambiar valores):**

- Las columnas tienen nombres cortos sin tildes. El nombre original de cada una figura en `documentos/diccionario_variables.csv`.
- Edad, escalas, montos y rondas quedan como números.
- Conteo de filas: encuesta 34 → 34; juego 16 → 16. No se eliminó ninguna fila.

**Limpiar (cambios de valor, registrados en `resultados/tablas/limpieza_cambios.csv`):**

- Alias: 41 celdas del juego se llevaron al código exacto de la encuesta. Eran diferencias de espacios o mayúsculas, por ejemplo “Cami 555” → “Cami555”.
- Duplicado: una persona respondió dos veces (pechu y pechu542). Se conserva la primera respuesta (24/9) y la segunda queda marcada en posible_doble. En el análisis se usa solo la primera.
- Pares verificados como personas distintas: 5 pares con edad, sexo y respuestas parecidas. El equipo confirmó que son personas distintas.
- Correcciones de escritura de receptores: 6, ya aplicadas en la transcripción.
- Ronda del ID 4: no estaba marcada. Se infirió ronda 3 y se confirma con el sorteo.
- Montos dudosos: ID 6 (90 o 40) y ID 16 (20). Se dejan como están y se mencionan como limitación.
- Observaciones: se mantienen en la tabla limpia.

**Controles:**
En las 16 filas, la diferencia CC − R1 y el monto conservado (100 − entregado) son correctos.
Quedan 8 filas con observaciones de transcripción, detalladas arriba.

## Paso 4 – Unir tablas
Se hizo en `codigo/04_union.py`. La tabla base es la encuesta, la clave es alias y el tipo de unión es left.

- Filas de la encuesta: 34 (33 personas, por el duplicado).
- Filas del juego: 16.
- Encuesta con juego: 16.
- Encuesta sin juego: 18 filas (17 personas).
- Juego sin encuesta: 0. Todos los dictadores tienen respuesta en la encuesta.
- Filas en la unión: 34.

**Limitaciones de la unión**

Los receptores no se unen a la encuesta, porque la unión es por dictador.
Las 17 personas que no jugaron tienen vacías las columnas del juego.

## Paso 5 – Generar nueva información
Se hizo en `codigo/05_variables_nuevas.py`, a partir de `datos/finales/union.csv`. Cada variable nueva es una columna adicional: no se modifica ningún dato original. Todas quedan documentadas en `documentos/diccionario_variables.csv`.

- `incluir_analisis`: 1 si la respuesta entra en el análisis, 0 si es la segunda respuesta de una persona duplicada. Quedan 33 de 34.
- `indice_social`: promedio simple de generosidad, justicia y consideración hacia los demás (escalas de 1 a 5).
- `indice_competitivo`: promedio simple de competitividad y beneficio propio (escalas de 1 a 5).
- `cambio_monto`: aumenta, igual o disminuye, según la diferencia entre la ronda cara a cara y la anónima. Para quienes no jugaron, "sin juego".
- `grupo_edad`: 19-20, 21-22 y 23 o más.

Los índices son promedios simples, sin ponderar. Los cortes de edad se eligieron para tener grupos de tamaño razonable. Ambas decisiones se tomaron antes de explorar los datos.

**Modelo de simulación** (`codigo/05b_aumentacion.py`, salida en `datos/finales/simulados.csv`). Siguiendo el modelo que explicó la profesora, se generan filas simuladas a partir de las 33 personas del análisis.
- Muestreo: se eligen filas de `analisis.csv` con reemplazo, hasta completar 200 filas.
- Innovación: a cada variable numérica se le suma ruido normal con desvío igual al 10% del desvío de esa variable.
- Ajustes: los valores se redondean y se ajustan a los rangos válidos (escalas de 1 a 5, montos de 0 a 100, edad de 17 a 99). Las columnas derivadas (monto conservado, diferencia, índices, grupo de edad y cambio de monto) se recalculan a partir de los valores ajustados.
- Rotulado: cada fila tiene `origen = "simulado"`. El archivo no incluye alias, marca temporal ni receptores, así que no se puede vincular con personas reales.
- Control: `resultados/tablas/aumentacion_control_medias.csv` compara medias reales y simuladas. Son parecidas: por ejemplo, edad 21.00 real y 20.73 simulada; índice social 4.20 y 4.22.

La aumentación no agrega información: las filas simuladas son copias perturbadas de las reales. Por eso el modelo se usa para probar el código y como referencia, y no para inferencia. Las conclusiones del paso 6 se sacan de los datos reales.

**Idas y vueltas.** Durante el paso 6 se agregaron la caracterización de la población y la prueba de asociación entre variables categóricas. Siguiendo la explicación de la profesora, se agregó el modelo de simulación (05b). No se cambió ninguna variable del paso 5.


## Paso 6 – Explorar: visualizar y modelar
Se hizo en `codigo/06_analisis.py`, a partir de `datos/finales/analisis.csv`, con las filas `incluir_analisis = 1` (33 personas, 16 jugadores). Los resultados son exploratorios: con 16 jugadores no se puede demostrar causalidad.

**Caracterización de la población** (`resultados/tablas/exp_caracterizacion.csv`).
- 33 personas: 52% masculino y 48% femenino. Edad media de 21 años (rango de 19 a 40).
- 16 jugadores: 69% femenino y 31% masculino.

**Ronda anónima frente a cara a cara** (prueba de Wilcoxon pareada, 16 jugadores).
- Monto medio: 37.8 en la ronda anónima y 46.9 cara a cara. Diferencia media de 9.1.
- 5 jugadores aumentaron, 10 se mantuvieron y 1 disminuyó.
- p = 0.074: no es significativo al 5%.

**Asociación.** Pruebas sobre los 33 datos reales (`resultados/tablas/exp_tests_asociacion.csv`), tomadas de la plantilla de la profesora:
- Sexo y grupo de edad (chi², orientativo por frecuencias bajas): p = 0.84, V de Cramér = 0.10.
- Edad por sexo (t de Welch): p = 0.43, d de Cohen = 0.29.
- Edad por sexo (Mann-Whitney): p = 0.90.
- Índice social por grupo de edad (Kruskal-Wallis): p = 0.66.
- Diferencia de monto por sexo (Mann-Whitney, 16 jugadores): p = 0.60.

Ninguna de estas pruebas es significativa. La misma tabla incluye los tests sobre las 200 filas simuladas, rotulados como referencia. Sus p-valores no se interpretan, porque la aumentación no agrega información.

**Correlaciones** (Spearman, 16 jugadores). Se hicieron 27 pruebas y no se corrigieron por comparaciones múltiples. Dos dan p < 0.05:
- Índice competitivo con monto anónimo: rho = −0.57, p = 0.02.
- Grado de conocimiento del receptor con la diferencia: rho = 0.57, p = 0.02.

Con tantas pruebas, es esperable que aparezcan resultados así por azar. Se presentan como hipótesis para estudiar con más datos.

**Modelo lineal** (mínimos cuadrados, 16 jugadores): diferencia en función del índice social y el índice competitivo. R² = 0.27, así que explica una parte chica de la variación. No se reportan p-valores por el tamaño de la muestra.

**Gráficos** (`resultados/graficos/`).
- `exp_anonimo_vs_visible.png`: monto de cada jugador en ambas rondas.
- `exp_indice_social_vs_monto.png`: índice social frente al monto.
- `exp_diferencia_hist.png`: distribución de la diferencia entre rondas.
- `exp_sexo_barras.png`: distribución por sexo (variable binaria).
- `exp_diferencia_por_sexo.png`: diferencia de monto por sexo.
- `exp_simulados_vs_reales_monto.png`: monto anónimo de los reales (16 jugadores) frente a las simuladas con monto (105 de 200), en densidad. Es solo de referencia, para ver si el modelo reproduce la forma de la distribución real.

**Lo que no apareció.** No hay diferencias claras por sexo ni por grupo de edad en el monto. Tampoco hay asociación entre sexo y grupo de edad. El índice social no muestra una relación significativa con el monto entregado, y el cambio entre rondas es pequeño y no significativo.

**Limitaciones del análisis.** Solo 16 jugadores. La encuesta fue anónima. El orden de las rondas fue fijo (primero anónima, después cara a cara). Los receptores no se unen a la encuesta.



