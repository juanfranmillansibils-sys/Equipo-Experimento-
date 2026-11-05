# Metodología

## Paso 1 – Importar los datos crudos

**Encuesta.** Google Forms enviada a todos los alumnos de ambos grupos. Exportación en PDF de la hoja de respuestas (`datos/crudos/encuesta_export_google_sheets.pdf`), 34 respuestas, marcas temporales desde el 24/9/2026. Variables en `documentos/diccionario_variables.csv`.
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
Pendiente.

## Paso 6 – Explorar: visualizar y modelar
Pendiente. Incluir también los gráficos que no confirmaron nada y las idas y vueltas con el paso 5.

## Paso 7 – Comunicar
Pendiente.
