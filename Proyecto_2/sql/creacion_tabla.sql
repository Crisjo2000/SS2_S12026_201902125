-- 1. Validar cantidad de registros útiles en el dataset público
SELECT COUNT(*) AS total_origen
FROM bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022
WHERE fare_amount > 0
  AND trip_distance > 0;

-- 2. Crear tabla base con 1,000,000 registros limpios
-- Esta tabla reduce costo porque selecciona solo columnas necesarias.
DROP TABLE IF EXISTS proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

CREATE TABLE proyecto-bigquery-taxis.dataset_G22.taxis_base_1m AS
SELECT
  pickup_datetime,
  dropoff_datetime,
  passenger_count,
  trip_distance,
  fare_amount,
  tip_amount,
  total_amount,
  pickup_location_id,
  dropoff_location_id
FROM bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022
WHERE fare_amount > 0
  AND trip_distance > 0
LIMIT 1000000;

-- 3. Verificar que la tabla se llenó correctamente
SELECT COUNT(*) AS total_registros
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

-- 4. Vista rápida de datos
SELECT *
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
LIMIT 10;

-- 5. Intento de tabla optimizada con partición y clustering
-- Nota: si esta parte falla en la cuenta de BigQuery, se puede trabajar
-- con la tabla base taxis_base_1m y documentar la limitación.
DROP TABLE IF EXISTS proyecto-bigquery-taxis.dataset_G22.taxi_optimizado_real;

CREATE TABLE proyecto-bigquery-taxis.dataset_G22.taxi_optimizado_real
PARTITION BY DATE(pickup_datetime)
CLUSTER BY pickup_location_id, dropoff_location_id
AS
SELECT *
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

-- 6. Verificar tabla optimizada
SELECT COUNT(*) AS total_optimizada
FROM proyecto-bigquery-taxis.dataset_G22.taxi_optimizado_real;