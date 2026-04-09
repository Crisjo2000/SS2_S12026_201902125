CREATE DATABASE SGFood;
GO

USE SGFood;
GO

USE SGFood;
GO

CREATE TABLE dim_tiempo (
    id_tiempo INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    dia INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    trimestre INT NOT NULL,
    anio INT NOT NULL,
    dia_semana VARCHAR(20) NOT NULL
);
GO

CREATE TABLE dim_sucursal (
    id_sucursal INT IDENTITY(1,1) PRIMARY KEY,
    cod_sucursal VARCHAR(20) NOT NULL UNIQUE,
    nombre_sucursal VARCHAR(150) NOT NULL,
    region VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL
);
GO

CREATE TABLE dim_producto (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    cod_producto VARCHAR(20) NOT NULL UNIQUE,
    nombre_producto VARCHAR(150) NOT NULL,
    marca_producto VARCHAR(100) NOT NULL,
    categoria VARCHAR(100) NOT NULL
);
GO

CREATE TABLE dim_cliente (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    cod_cliente VARCHAR(20) NOT NULL UNIQUE,
    nombre_cliente VARCHAR(150) NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL
);
GO

CREATE TABLE dim_vendedor (
    id_vendedor INT IDENTITY(1,1) PRIMARY KEY,
    cod_vendedor VARCHAR(20) NOT NULL UNIQUE,
    nombre_vendedor VARCHAR(150) NOT NULL
);
GO

CREATE TABLE dim_proveedor (
    id_proveedor INT IDENTITY(1,1) PRIMARY KEY,
    cod_proveedor VARCHAR(20) NOT NULL UNIQUE,
    nombre_proveedor VARCHAR(150) NOT NULL
);
GO

CREATE TABLE fact_ventas (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    id_tiempo INT NOT NULL,
    id_cliente INT NOT NULL,
    id_vendedor INT NOT NULL,
    id_producto INT NOT NULL,
    id_sucursal INT NOT NULL,
    unidades INT NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    total_venta DECIMAL(14,2) NOT NULL,

    CONSTRAINT fk_fact_ventas_tiempo
        FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),

    CONSTRAINT fk_fact_ventas_cliente
        FOREIGN KEY (id_cliente) REFERENCES dim_cliente(id_cliente),

    CONSTRAINT fk_fact_ventas_vendedor
        FOREIGN KEY (id_vendedor) REFERENCES dim_vendedor(id_vendedor),

    CONSTRAINT fk_fact_ventas_producto
        FOREIGN KEY (id_producto) REFERENCES dim_producto(id_producto),

    CONSTRAINT fk_fact_ventas_sucursal
        FOREIGN KEY (id_sucursal) REFERENCES dim_sucursal(id_sucursal)
);
GO

CREATE TABLE fact_compras (
    id_compra INT IDENTITY(1,1) PRIMARY KEY,
    id_tiempo INT NOT NULL,
    id_proveedor INT NOT NULL,
    id_producto INT NOT NULL,
    id_sucursal INT NOT NULL,
    unidades INT NOT NULL,
    costo_unitario DECIMAL(12,2) NOT NULL,
    total_compra DECIMAL(14,2) NOT NULL,

    CONSTRAINT fk_fact_compras_tiempo
        FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),

    CONSTRAINT fk_fact_compras_proveedor
        FOREIGN KEY (id_proveedor) REFERENCES dim_proveedor(id_proveedor),

    CONSTRAINT fk_fact_compras_producto
        FOREIGN KEY (id_producto) REFERENCES dim_producto(id_producto),

    CONSTRAINT fk_fact_compras_sucursal
        FOREIGN KEY (id_sucursal) REFERENCES dim_sucursal(id_sucursal)
);
GO