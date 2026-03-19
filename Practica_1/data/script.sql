CREATE DATABASE airline;
GO

USE airline;
GO

/* =========================
   DIMENSIÓN PASAJERO
   ========================= */
CREATE TABLE dim_pasajero (
    id_pasajero      INT PRIMARY KEY,
    passenger_id     VARCHAR(50) NOT NULL,
    genero           VARCHAR(20) NOT NULL,
    edad             INT NULL,
    rango_edad       VARCHAR(20) NOT NULL,
    nacionalidad     VARCHAR(100) NOT NULL
);
GO

/* =========================
   DIMENSIÓN AEROLÍNEA
   ========================= */
CREATE TABLE dim_aerolinea (
    id_aerolinea     INT PRIMARY KEY,
    airline_code     VARCHAR(10) NOT NULL,
    airline_name     VARCHAR(100) NOT NULL
);
GO

/* =========================
   DIMENSIÓN AEROPUERTO
   ========================= */
CREATE TABLE dim_aeropuerto (
    id_aeropuerto    INT PRIMARY KEY,
    codigo_iata      VARCHAR(10) NOT NULL
);
GO

/* =========================
   DIMENSIÓN FECHA
   ========================= */
CREATE TABLE dim_fecha (
    id_fecha         INT PRIMARY KEY,   -- formato YYYYMMDD
    fecha            DATE NOT NULL,
    dia              INT NOT NULL,
    mes              INT NOT NULL,
    nombre_mes       VARCHAR(20) NOT NULL,
    trimestre        INT NOT NULL,
    anio             INT NOT NULL,
    dia_semana       VARCHAR(20) NOT NULL,
    es_fin_semana    BIT NOT NULL
);
GO

/* =========================
   DIMENSIÓN VUELO
   ========================= */
CREATE TABLE dim_vuelo (
    id_vuelo         INT PRIMARY KEY,
    flight_number    VARCHAR(20) NOT NULL,
    aircraft_type    VARCHAR(30) NOT NULL,
    cabin_class      VARCHAR(30) NOT NULL,
    status           VARCHAR(20) NOT NULL
);
GO

/* =========================
   DIMENSIÓN VENTA
   ========================= */
CREATE TABLE dim_venta (
    id_venta         INT PRIMARY KEY,
    canal_venta      VARCHAR(50) NOT NULL,
    metodo_pago      VARCHAR(50) NOT NULL,
    currency         VARCHAR(10) NOT NULL
);
GO

/* =========================
   TABLA DE HECHOS
   ========================= */
CREATE TABLE fact_booking_flight (
    id_fact                  BIGINT IDENTITY(1,1) PRIMARY KEY,
    booking_id               INT NOT NULL,
    record_id                INT NOT NULL,

    id_pasajero              INT NOT NULL,
    id_aerolinea             INT NOT NULL,
    id_aeropuerto_origen     INT NOT NULL,
    id_aeropuerto_destino    INT NOT NULL,
    id_fecha_reserva         INT NOT NULL,
    id_fecha_salida          INT NOT NULL,
    id_vuelo                 INT NOT NULL,
    id_venta                 INT NOT NULL,

    ticket_price_usd         DECIMAL(12,2) NOT NULL,
    duration_min             INT NULL,
    delay_min                INT NULL,
    bags_total               INT NOT NULL,
    bags_checked             INT NOT NULL,
    flight_count             INT NOT NULL DEFAULT 1,

    CONSTRAINT FK_fact_pasajero
        FOREIGN KEY (id_pasajero)
        REFERENCES dim_pasajero(id_pasajero),

    CONSTRAINT FK_fact_aerolinea
        FOREIGN KEY (id_aerolinea)
        REFERENCES dim_aerolinea(id_aerolinea),

    CONSTRAINT FK_fact_aeropuerto_origen
        FOREIGN KEY (id_aeropuerto_origen)
        REFERENCES dim_aeropuerto(id_aeropuerto),

    CONSTRAINT FK_fact_aeropuerto_destino
        FOREIGN KEY (id_aeropuerto_destino)
        REFERENCES dim_aeropuerto(id_aeropuerto),

    CONSTRAINT FK_fact_fecha_reserva
        FOREIGN KEY (id_fecha_reserva)
        REFERENCES dim_fecha(id_fecha),

    CONSTRAINT FK_fact_fecha_salida
        FOREIGN KEY (id_fecha_salida)
        REFERENCES dim_fecha(id_fecha),

    CONSTRAINT FK_fact_vuelo
        FOREIGN KEY (id_vuelo)
        REFERENCES dim_vuelo(id_vuelo),

    CONSTRAINT FK_fact_venta
        FOREIGN KEY (id_venta)
        REFERENCES dim_venta(id_venta)
);
GO