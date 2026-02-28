USE VuelosDB;

-- Total de vuelos por estado
SELECT
    de.descripcion        AS estado,
    COUNT(*)              AS total_vuelos
FROM fact_vuelo fv
JOIN dim_estado de ON fv.id_estado = de.id_estado
GROUP BY de.descripcion
ORDER BY total_vuelos DESC;

-- Top 5 aerolíneas con más vuelos

SELECT TOP 5
    da.airline_name       AS aerolinea,
    COUNT(*)              AS total_vuelos
FROM fact_vuelo fv
JOIN dim_aerolinea da ON fv.id_aerolinea = da.id_aerolinea
GROUP BY da.airline_name
ORDER BY total_vuelos DESC;

-- Distribución de pasajeros por género

SELECT
    genero,
    COUNT(*)              AS total_pasajeros
FROM dim_pasajero
GROUP BY genero
ORDER BY total_pasajeros DESC;


-- Top 5 destinos más populares

SELECT TOP 5
    da.codigo_iata        AS destino,
    COUNT(*)              AS total_vuelos
FROM fact_vuelo fv
JOIN dim_aeropuerto da ON fv.id_destino = da.id_aeropuerto
GROUP BY da.codigo_iata
ORDER BY total_vuelos DESC;

-- Total de vuelos por mes

SELECT
    df.anio,
    df.nombre_mes,
    COUNT(*)        AS total_vuelos
FROM fact_vuelo fv
JOIN dim_fecha df ON fv.id_fecha = df.id_fecha
GROUP BY df.anio, df.mes, df.nombre_mes
ORDER BY total_vuelos DESC;