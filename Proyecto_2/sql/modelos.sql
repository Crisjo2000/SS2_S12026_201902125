-- ============================================================
-- MODELO 1: REGRESIÓN LINEAL
-- Propósito: predecir total_amount usando características del viaje.
-- ============================================================

CREATE OR REPLACE MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_regresion_total`
OPTIONS(
  model_type = 'linear_reg',
  input_label_cols = ['total_amount'],
  data_split_method = 'RANDOM',
  data_split_eval_fraction = 0.2
) AS
SELECT
  total_amount,
  trip_distance,
  passenger_count,
  EXTRACT(HOUR FROM pickup_datetime) AS hora_viaje,
  EXTRACT(DAYOFWEEK FROM pickup_datetime) AS dia_semana,
  pickup_location_id,
  dropoff_location_id
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
WHERE total_amount > 0
  AND trip_distance > 0
  AND passenger_count IS NOT NULL;

-- Evaluar modelo de regresión
SELECT *
FROM ML.EVALUATE(MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_regresion_total`);

-- Predicciones con modelo de regresión
SELECT *
FROM ML.PREDICT(
  MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_regresion_total`,
  (
    SELECT
      trip_distance,
      passenger_count,
      EXTRACT(HOUR FROM pickup_datetime) AS hora_viaje,
      EXTRACT(DAYOFWEEK FROM pickup_datetime) AS dia_semana,
      pickup_location_id,
      dropoff_location_id
    FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
    LIMIT 20
  )
);

-- ============================================================
-- MODELO 2: CLASIFICACIÓN LOGÍSTICA
-- Propósito: clasificar si un viaje tendrá propina alta.
-- Se usa split personalizado para manejar separación train/eval.
-- ============================================================

CREATE OR REPLACE TABLE `proyecto-bigquery-taxis.dataset_G22.dataset_ml_clasificacion` AS
SELECT
  CASE WHEN tip_amount >= 5 THEN 1 ELSE 0 END AS propina_alta,
  trip_distance,
  passenger_count,
  fare_amount,
  EXTRACT(HOUR FROM pickup_datetime) AS hora_viaje,
  EXTRACT(DAYOFWEEK FROM pickup_datetime) AS dia_semana,
  pickup_location_id,
  dropoff_location_id,
  CASE
    WHEN MOD(ABS(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING))), 10) < 8 THEN FALSE
    ELSE TRUE
  END AS eval_split
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
WHERE tip_amount IS NOT NULL
  AND fare_amount > 0
  AND trip_distance > 0
  AND passenger_count IS NOT NULL;

CREATE OR REPLACE MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_clasificacion_propina`
OPTIONS(
  model_type = 'logistic_reg',
  input_label_cols = ['propina_alta'],
  data_split_method = 'CUSTOM',
  data_split_col = 'eval_split'
) AS
SELECT
  propina_alta,
  trip_distance,
  passenger_count,
  fare_amount,
  hora_viaje,
  dia_semana,
  pickup_location_id,
  dropoff_location_id,
  eval_split
FROM `proyecto-bigquery-taxis.dataset_G22.dataset_ml_clasificacion`;

-- Evaluar modelo de clasificación
SELECT *
FROM ML.EVALUATE(MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_clasificacion_propina`);

-- Matriz de confusión
SELECT *
FROM ML.CONFUSION_MATRIX(MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_clasificacion_propina`);

-- Predicciones con modelo de clasificación
SELECT *
FROM ML.PREDICT(
  MODEL `proyecto-bigquery-taxis.dataset_G22.modelo_clasificacion_propina`,
  (
    SELECT
      trip_distance,
      passenger_count,
      fare_amount,
      EXTRACT(HOUR FROM pickup_datetime) AS hora_viaje,
      EXTRACT(DAYOFWEEK FROM pickup_datetime) AS dia_semana,
      pickup_location_id,
      dropoff_location_id
    FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
    LIMIT 20
  )
);