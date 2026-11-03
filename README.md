# Juego del Dictador – Proyecto de Ciencia de Datos

Trabajo de la materia **Introducción a la Ciencia de Datos**, Facultad de Ciencias Empresariales y Economía, Universidad de Montevideo.

## Pregunta y objetivo

¿Se relacionan las características que las personas declaran sobre sí mismas con cuánto entregan en el Juego del Dictador? ¿Cambia el monto entregado según el receptor sea anónimo o esté cara a cara?

El diseño experimental no permite demostrar causalidad en general; el análisis distingue correlación de causalidad.

## Datos

- **Encuesta** (Google Forms): 22 respuestas. Exportación en `datos/crudos/encuesta_export_google_sheets.pdf`.
- **Juego del Dictador** (presencial, 18 participantes): decisiones registradas en fichas de papel (`documentos/ficha_juego.pdf`), transcritas a planilla.
- **Unión** por alias: la encuesta es la tabla base. Los participantes sin registro de juego quedan con valores nulos.

## Estructura

```
├── README.md
├── requirements.txt
├── .gitignore
├── codigo/              scripts en orden, 01 a 06, y run_all.py
├── datos/
│   ├── crudos/          datos originales, sin modificar
│   └── finales/         tablas procesadas
├── resultados/
│   ├── tablas/
│   └── graficos/
└── documentos/          metodología, declaración de énfasis, ficha, diccionario
```

## Cómo reproducir

```bash
pip install -r requirements.txt
python codigo/run_all.py
```

## Limitaciones

- Muestra pequeña (22 encuestados, 18 jugadores).
- Todos los participantes tomaron primero la decisión anónima y después la cara a cara. El orden queda confundido con la experiencia previa.
- Cada jugador aporta dos decisiones, por lo que no son observaciones independientes.

## Integrantes

Vicente Alvarez, Facundo Botti, Ignacio Merli, Juan Millán y Luca Sonneveld
