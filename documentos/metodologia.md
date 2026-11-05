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
Pendiente. Ordenar y limpiar se documentan por separado.

## Paso 4 – Unir tablas
Pendiente. Clave: alias. Encuesta como tabla base.

## Paso 5 – Generar nueva información
Pendiente.

## Paso 6 – Explorar: visualizar y modelar
Pendiente. Incluir también los gráficos que no confirmaron nada y las idas y vueltas con el paso 5.

## Paso 7 – Comunicar
Pendiente.
