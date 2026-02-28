-- Creación de la base de datos
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'VuelosDB')
BEGIN
    CREATE DATABASE VuelosDB;
END
GO

USE VuelosDB;
GO

-- DIM_AEROLINEA
IF OBJECT_ID('dim_aerolinea', 'U') IS NOT NULL DROP TABLE dim_aerolinea;
CREATE TABLE dim_aerolinea (
    id_aerolinea  INT            NOT NULL PRIMARY KEY,
    airline_code  NVARCHAR(10)   NOT NULL,
    airline_name  NVARCHAR(100)  NOT NULL,
    CONSTRAINT uq_aerolinea_code UNIQUE (airline_code)
);
GO

-- DIM_AEROPUERTO
IF OBJECT_ID('dim_aeropuerto', 'U') IS NOT NULL DROP TABLE dim_aeropuerto;
CREATE TABLE dim_aeropuerto (
    id_aeropuerto INT           NOT NULL PRIMARY KEY,
    codigo_iata   NVARCHAR(10)  NOT NULL,
    CONSTRAINT uq_aeropuerto_iata UNIQUE (codigo_iata)
);
GO

-- DIM_AVION
IF OBJECT_ID('dim_avion', 'U') IS NOT NULL DROP TABLE dim_avion;
CREATE TABLE dim_avion (
    id_avion      INT           NOT NULL PRIMARY KEY,
    aircraft_type NVARCHAR(20)  NOT NULL,
    CONSTRAINT uq_avion_tipo UNIQUE (aircraft_type)
);
GO

-- DIM_FECHA
IF OBJECT_ID('dim_fecha', 'U') IS NOT NULL DROP TABLE dim_fecha;
CREATE TABLE dim_fecha (
    id_fecha      INT           NOT NULL PRIMARY KEY,
    fecha         DATE          NOT NULL,
    anio          INT           NOT NULL,
    mes           INT           NOT NULL,
    nombre_mes    NVARCHAR(15)  NOT NULL,
    trimestre     INT           NOT NULL,
    dia           INT           NOT NULL,
    dia_semana    NVARCHAR(15)  NOT NULL,
    es_fin_semana INT           NOT NULL DEFAULT 0,  -- 0 = entre semana, 1 = fin de semana
    CONSTRAINT uq_fecha UNIQUE (fecha)
);
GO

-- DIM_ESTADO
IF OBJECT_ID('dim_estado', 'U') IS NOT NULL DROP TABLE dim_estado;
CREATE TABLE dim_estado (
    id_estado   INT           NOT NULL PRIMARY KEY,
    codigo      NVARCHAR(15)  NOT NULL,
    descripcion NVARCHAR(30)  NOT NULL,
    CONSTRAINT uq_estado_codigo UNIQUE (codigo)
);
GO

-- DIM_PASAJERO 
IF OBJECT_ID('dim_pasajero', 'U') IS NOT NULL DROP TABLE dim_pasajero;
CREATE TABLE dim_pasajero (
    id_pasajero  NVARCHAR(50)  NOT NULL PRIMARY KEY,
    genero       NVARCHAR(10)  NOT NULL CHECK (genero IN ('M','F','X')),
    edad         INT           NOT NULL,
    nacionalidad NVARCHAR(30)  NOT NULL
);
GO

-- FACT_VUELO
IF OBJECT_ID('fact_vuelo', 'U') IS NOT NULL DROP TABLE fact_vuelo;
CREATE TABLE fact_vuelo (
    id_vuelo            INT           NOT NULL PRIMARY KEY,
    id_aerolinea        INT           NOT NULL,
    id_origen           INT           NOT NULL,
    id_destino          INT           NOT NULL,
    id_avion            INT           NOT NULL,
    id_estado           INT           NOT NULL,
    id_fecha            INT           NOT NULL,
    flight_number       NVARCHAR(10)  NOT NULL,
    cabin_class         NVARCHAR(20)  NULL,
    seat                NVARCHAR(10)  NULL,
    departure_datetime  DATETIME      NULL,
    arrival_datetime    DATETIME      NULL,
    duration_min        FLOAT         NULL,
    delay_min           FLOAT         NOT NULL DEFAULT 0,
    -- Claves foráneas
    CONSTRAINT fk_vuelo_aerolinea  FOREIGN KEY (id_aerolinea) REFERENCES dim_aerolinea(id_aerolinea),
    CONSTRAINT fk_vuelo_origen     FOREIGN KEY (id_origen)    REFERENCES dim_aeropuerto(id_aeropuerto),
    CONSTRAINT fk_vuelo_destino    FOREIGN KEY (id_destino)   REFERENCES dim_aeropuerto(id_aeropuerto),
    CONSTRAINT fk_vuelo_avion      FOREIGN KEY (id_avion)     REFERENCES dim_avion(id_avion),
    CONSTRAINT fk_vuelo_estado     FOREIGN KEY (id_estado)    REFERENCES dim_estado(id_estado),
    CONSTRAINT fk_vuelo_fecha      FOREIGN KEY (id_fecha)     REFERENCES dim_fecha(id_fecha)
);
GO

-- FACT_RESERVA 
IF OBJECT_ID('fact_reserva', 'U') IS NOT NULL DROP TABLE fact_reserva;
CREATE TABLE fact_reserva (
    id_reserva           INT           NOT NULL PRIMARY KEY,
    id_vuelo             INT           NOT NULL,
    id_pasajero          NVARCHAR(50)  NOT NULL,
    id_aerolinea         INT           NULL,
    id_fecha_reserva     INT           NULL,
    fecha_reserva        DATETIME      NULL,
    canal_venta          NVARCHAR(30)  NULL,
    metodo_pago          NVARCHAR(30)  NULL,
    precio_ticket        FLOAT         NULL,
    moneda               NVARCHAR(10)  NULL,
    precio_usd           FLOAT         NULL,
    total_maletas        INT           NOT NULL DEFAULT 0,
    maletas_documentadas INT           NOT NULL DEFAULT 0,
    -- Claves foráneas
    CONSTRAINT fk_reserva_pasajero  FOREIGN KEY (id_pasajero)      REFERENCES dim_pasajero(id_pasajero),
    CONSTRAINT fk_reserva_aerolinea FOREIGN KEY (id_aerolinea)     REFERENCES dim_aerolinea(id_aerolinea),
    CONSTRAINT fk_reserva_fecha     FOREIGN KEY (id_fecha_reserva) REFERENCES dim_fecha(id_fecha)
);
GO

-- Indices para consultas

CREATE INDEX ix_vuelo_fecha      ON fact_vuelo   (id_fecha);
CREATE INDEX ix_vuelo_destino    ON fact_vuelo   (id_destino);
CREATE INDEX ix_vuelo_aerolinea  ON fact_vuelo   (id_aerolinea);
CREATE INDEX ix_vuelo_estado     ON fact_vuelo   (id_estado);
CREATE INDEX ix_reserva_pasajero ON fact_reserva (id_pasajero);
CREATE INDEX ix_reserva_vuelo    ON fact_reserva (id_vuelo);
GO