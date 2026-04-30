# Proyecto 2: Procesamiento y Análisis Exploratorio de Datos Masivos en BigQuery

## Universidad de San Carlos de Guatemala
Facultad de Ingeniería  
Ingeniería en Ciencias y Sistemas  
Curso: Seminario de Sistemas 2  

## Integrantes
- Integrante 1: Luisa Daniela Velásquez Rodas
- Integrante 2: Christian Josué Hernández Juárez

---

## 1. Descripción del proyecto

Este proyecto consiste en realizar procesamiento y análisis exploratorio de datos masivos utilizando Google BigQuery.  
Se trabajó con el dataset público de viajes de taxi de Nueva York correspondiente al año 2022, aplicando consultas SQL, creación de tablas derivadas, limpieza de datos, análisis exploratorio, visualización de resultados y modelos predictivos mediante BigQuery ML.

El objetivo principal fue transformar datos masivos en información útil para identificar patrones relacionados con viajes, horarios, distancias, pagos, propinas y zonas de origen/destino.

---

## 2. Dataset utilizado

Dataset público:

bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022

Este dataset contiene registros de viajes de taxis amarillos en la ciudad de Nueva York durante el año 2022.

Campos principales utilizados:

- pickup_datetime
- dropoff_datetime
- passenger_count
- trip_distance
- fare_amount
- tip_amount
- total_amount
- pickup_location_id
- dropoff_location_id

---

## 3. Herramientas utilizadas

- Google Cloud Platform
- Google BigQuery
- BigQuery ML
- Google Sheets o Looker Studio
- GitHub

---

## 4. Creación de tabla derivada

Para reducir el costo de procesamiento y trabajar con datos útiles, se creó una tabla derivada llamada:

proyecto-bigquery-taxis.dataset_G22.taxis_base_1m

Esta tabla contiene 1,000,000 registros filtrados del dataset original.

Condiciones aplicadas:

- fare_amount > 0
- trip_distance > 0

Además, se seleccionaron únicamente las columnas necesarias para el análisis, evitando el uso de SELECT * sobre el dataset público completo.

---

## 5. Optimización aplicada

Se aplicó una optimización inicial mediante:

- Selección de columnas específicas.
- Filtros de limpieza.
- Creación de una tabla derivada con menor volumen de datos.
- Reducción de bytes procesados al consultar una tabla propia en lugar del dataset público completo.

También se intentó aplicar particionamiento por fecha y clustering por zonas de origen/destino:

- Partición: DATE(pickup_datetime)
- Clustering: pickup_location_id, dropoff_location_id

Durante la ejecución se identificaron limitaciones con la creación/llenado de la tabla particionada, por lo que el análisis principal se realizó sobre taxis_base_1m.

---

## 6. Consultas exploratorias realizadas

Se realizaron consultas para obtener:

- Total de viajes analizados.
- Distancia promedio.
- Pago promedio.
- Propina promedio.
- Viajes por hora del día.
- Viajes por cantidad de pasajeros.
- Top 10 zonas de origen.
- Top 10 rutas origen-destino.
- Relación entre distancia y pago.
- Porcentaje de viajes con propina.

Los scripts se encuentran en:

sql/consultas.sql

---

## 7. Visualizaciones

Se proponen las siguientes visualizaciones:

1. Viajes por hora del día.
2. Pago promedio por rango de distancia.
3. Top 10 zonas de origen.
4. Propinas altas vs propinas normales/bajas.

Estas visualizaciones permiten interpretar patrones temporales, económicos y geográficos del comportamiento de los viajes.

Enlace al dashboard:

PEGAR_AQUI_EL_LINK_DE_LOOKER_STUDIO_O_GOOGLE_SHEETS

---

## 8. Modelos de BigQuery ML

Se implementaron dos modelos:

### Modelo 1: Regresión lineal

Objetivo: predecir el valor de total_amount.

Variables de entrada:

- trip_distance
- passenger_count
- hora_viaje
- dia_semana
- pickup_location_id
- dropoff_location_id

Variable objetivo:

- total_amount

Métrica esperada:

- RMSE
- MAE
- R²

---

### Modelo 2: Clasificación logística

Objetivo: clasificar si un viaje tiene propina alta.

Variable objetivo:

- propina_alta

Definición:

- 1 si tip_amount >= 5
- 0 si tip_amount < 5

Variables de entrada:

- trip_distance
- passenger_count
- fare_amount
- hora_viaje
- dia_semana
- pickup_location_id
- dropoff_location_id

Métricas esperadas:

- Accuracy
- Precision
- Recall
- ROC-AUC
- Matriz de confusión

---

## 9. Manejo de Data Leakage

Para reducir el riesgo de data leakage:

- No se utilizó tip_amount como variable de entrada para predecir total_amount.
- Se separaron datos de entrenamiento y evaluación.
- En el modelo de regresión se utilizó división aleatoria con data_split_eval_fraction = 0.2.
- En el modelo de clasificación se utilizó una columna personalizada eval_split.

---

## 10. Hallazgos esperados

Algunos hallazgos esperados del análisis son:

- Existen horas del día con mayor demanda de viajes.
- Los viajes más largos presentan pagos promedio más altos.
- Algunas zonas concentran mayor cantidad de viajes.
- No todos los viajes incluyen propina, y las propinas altas representan una proporción menor del total.
- La distancia del viaje y la tarifa base influyen en el monto total cobrado.

---

## 11. Estructura del repositorio

text
Proyecto_2/
│
├── sql/
│   ├── creacion_tablas.sql
│   ├── consultas.sql
│   └── modelo_ml.sql
│
├── evidencias/
│   ├── consulta_total_registros.png
│   ├── creacion_tabla_base.png
│   ├── consultas_exploratorias.png
│   ├── modelo_ml_evaluacion.png
│   └── dashboard.png
│
├── graficas.md
└── README.md


---

## 12. Conclusiones

El proyecto permitió aplicar análisis exploratorio sobre datos masivos usando BigQuery.  
Se creó una tabla derivada de 1,000,000 registros para reducir el costo de consulta y facilitar el análisis.  
Las consultas SQL permitieron identificar patrones de demanda, distancia, pagos, zonas y propinas.  
Además, BigQuery ML permitió construir modelos predictivos para estimar pagos y clasificar propinas altas.

El uso de BigQuery facilitó el procesamiento de datos masivos sin necesidad de infraestructura local.