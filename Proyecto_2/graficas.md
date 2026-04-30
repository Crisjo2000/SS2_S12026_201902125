# Gráficas sugeridas para Looker Studio o Google Sheets

Usar como fuente la tabla:

proyecto-bigquery-taxis.dataset_G22.taxis_base_1m

## Gráfica 1: Viajes por hora del día
Consulta base:

sql
SELECT
  EXTRACT(HOUR FROM pickup_datetime) AS hora,
  COUNT(*) AS total_viajes
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
GROUP BY hora
ORDER BY hora;


Tipo recomendado: gráfico de barras o líneas.

Interpretación:
Permite identificar las horas con mayor demanda de taxis.

---

## Gráfica 2: Pago promedio por rango de distancia
Consulta base:

sql
SELECT
  CASE
    WHEN trip_distance < 1 THEN 'Menos de 1 milla'
    WHEN trip_distance BETWEEN 1 AND 3 THEN '1 a 3 millas'
    WHEN trip_distance BETWEEN 3 AND 7 THEN '3 a 7 millas'
    WHEN trip_distance BETWEEN 7 AND 15 THEN '7 a 15 millas'
    ELSE 'Más de 15 millas'
  END AS rango_distancia,
  ROUND(AVG(total_amount), 2) AS pago_promedio
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
GROUP BY rango_distancia
ORDER BY pago_promedio DESC;


Tipo recomendado: gráfico de barras.

Interpretación:
Muestra cómo aumenta el pago promedio según la distancia recorrida.

---

## Gráfica 3: Top 10 zonas de origen
Consulta base:

sql
SELECT
  pickup_location_id,
  COUNT(*) AS total_viajes
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
GROUP BY pickup_location_id
ORDER BY total_viajes DESC
LIMIT 10;


Tipo recomendado: gráfico de barras.

Interpretación:
Identifica las zonas donde se originan más viajes.

---

## Gráfica 4 opcional: Propinas altas vs normales
Consulta base:

sql
SELECT
  CASE WHEN tip_amount >= 5 THEN 'Propina alta' ELSE 'Propina normal/baja' END AS categoria_propina,
  COUNT(*) AS total_viajes
FROM `proyecto-bigquery-taxis.dataset_G22.taxis_base_1m`
GROUP BY categoria_propina;


Tipo recomendado: pastel o barras.

Interpretación:
Permite analizar la proporción de viajes con propinas altas.