-- 1. Total de viajes analizados
SELECT COUNT(*) AS total_viajes
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

-- 2. Métricas generales del dataset
SELECT
  COUNT(*) AS total_viajes,
  ROUND(AVG(trip_distance), 2) AS distancia_promedio,
  ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
  ROUND(AVG(tip_amount), 2) AS propina_promedio,
  ROUND(AVG(total_amount), 2) AS total_promedio,
  ROUND(MAX(trip_distance), 2) AS distancia_maxima,
  ROUND(MAX(total_amount), 2) AS pago_maximo
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

-- 3. Viajes por cantidad de pasajeros
SELECT
  passenger_count,
  COUNT(*) AS total_viajes
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY passenger_count
ORDER BY total_viajes DESC;

-- 4. Viajes por hora del día
SELECT
  EXTRACT(HOUR FROM pickup_datetime) AS hora,
  COUNT(*) AS total_viajes,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY hora
ORDER BY hora;

-- 5. Viajes por día
SELECT
  DATE(pickup_datetime) AS fecha,
  COUNT(*) AS total_viajes,
  ROUND(AVG(trip_distance), 2) AS distancia_promedio,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY fecha
ORDER BY fecha;

-- 6. Top 10 zonas de origen con más viajes
SELECT
  pickup_location_id,
  COUNT(*) AS total_viajes
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY pickup_location_id
ORDER BY total_viajes DESC
LIMIT 10;

-- 7. Top 10 rutas origen-destino más frecuentes
SELECT
  pickup_location_id,
  dropoff_location_id,
  COUNT(*) AS total_viajes,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY pickup_location_id, dropoff_location_id
ORDER BY total_viajes DESC
LIMIT 10;

-- 8. Relación entre distancia y pago
SELECT
  CASE
    WHEN trip_distance < 1 THEN 'Menos de 1 milla'
    WHEN trip_distance BETWEEN 1 AND 3 THEN '1 a 3 millas'
    WHEN trip_distance BETWEEN 3 AND 7 THEN '3 a 7 millas'
    WHEN trip_distance BETWEEN 7 AND 15 THEN '7 a 15 millas'
    ELSE 'Más de 15 millas'
  END AS rango_distancia,
  COUNT(*) AS total_viajes,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
GROUP BY rango_distancia
ORDER BY pago_promedio DESC;

-- 9. Porcentaje de viajes con propina
SELECT
  COUNT(*) AS total_viajes,
  SUM(CASE WHEN tip_amount > 0 THEN 1 ELSE 0 END) AS viajes_con_propina,
  ROUND(SUM(CASE WHEN tip_amount > 0 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) AS porcentaje_con_propina
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m;

-- 10. Consulta filtrada por fecha para comparar costos/bytes
SELECT
  DATE(pickup_datetime) AS fecha,
  COUNT(*) AS total_viajes,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM proyecto-bigquery-taxis.dataset_G22.taxis_base_1m
WHERE DATE(pickup_datetime) BETWEEN '2022-03-01' AND '2022-03-31'
GROUP BY fecha
ORDER BY fecha;