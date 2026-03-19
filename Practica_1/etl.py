from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# =========================================================
# CONFIGURACIÓN
# =========================================================
BASE_DIR = Path(__file__).parent
DATASET_1 = BASE_DIR / "csvs" / "Dataset_1.csv"
DATASET_2 = BASE_DIR / "csvs" / "Dataset_2.csv"

SQL_SERVER = "localhost"
SQL_DATABASE = "airline"

ENGINE_URL = (
    f"mssql+pyodbc://{SQL_SERVER}/{SQL_DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

LOAD_TO_SQL = True
# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def normalize_upper(value, default="UNKNOWN"):
    if pd.isna(value):
        return default
    value = str(value).strip().upper()
    return value if value else default


def normalize_gender(value):
    if pd.isna(value):
        return "X"

    v = str(value).strip().lower()

    if v in ["m", "masculino", "male"]:
        return "M"
    if v in ["f", "femenino", "female"]:
        return "F"
    if v in ["x", "nobinario", "no binario", "non-binary", "other"]:
        return "X"

    return "X"


def normalize_airline_name(value):
    if pd.isna(value):
        return "UNKNOWN"

    v = str(value).strip().upper()

    mapping = {
        "DELTA": "DELTA",
        "AVIANCA": "AVIANCA",
        "IBERIA": "IBERIA",
        "RYANAIR": "RYANAIR",
        "SOUTHWEST": "SOUTHWEST",
        "AMERICAN AIRLINES": "AMERICAN AIRLINES",
        "AMERICAN": "AMERICAN AIRLINES",
        "JETBLUE": "JETBLUE",
        "UNITED": "UNITED",
        "AEROMEXICO": "AEROMEXICO"
    }

    return mapping.get(v, v)


def parse_datetime_mixed(series):
    """
    Soporta formatos mixtos como:
    - 15/01/2024 10:09
    - 03-15-2025 01:58 PM
    """
    dt = pd.to_datetime(series, format="%d/%m/%Y %H:%M", errors="coerce")
    mask = dt.isna()

    if mask.any():
        dt2 = pd.to_datetime(series[mask], format="%m-%d-%Y %I:%M %p", errors="coerce")
        dt.loc[mask] = dt2

    return dt


def normalize_price(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return np.nan


def age_range(age):
    if pd.isna(age):
        return "UNKNOWN"

    age = int(age)

    if age < 18:
        return "0-17"
    if age <= 25:
        return "18-25"
    if age <= 40:
        return "26-40"
    if age <= 60:
        return "41-60"
    return "60+"


def build_dim_fecha(datetime_series):
    fechas = pd.Series(pd.to_datetime(datetime_series.dropna()).dt.date.unique())
    fechas = fechas.sort_values()

    dim_fecha = pd.DataFrame({"fecha": pd.to_datetime(fechas)})
    dim_fecha["id_fecha"] = dim_fecha["fecha"].dt.strftime("%Y%m%d").astype(int)
    dim_fecha["dia"] = dim_fecha["fecha"].dt.day
    dim_fecha["mes"] = dim_fecha["fecha"].dt.month
    dim_fecha["nombre_mes"] = dim_fecha["fecha"].dt.month_name()
    dim_fecha["trimestre"] = dim_fecha["fecha"].dt.quarter
    dim_fecha["anio"] = dim_fecha["fecha"].dt.year
    dim_fecha["dia_semana"] = dim_fecha["fecha"].dt.day_name()
    dim_fecha["es_fin_semana"] = dim_fecha["fecha"].dt.weekday.isin([5, 6]).astype(int)

    return dim_fecha[
        ["id_fecha", "fecha", "dia", "mes", "nombre_mes", "trimestre", "anio", "dia_semana", "es_fin_semana"]
    ]


def get_engine():
    return create_engine(ENGINE_URL)


# =========================================================
# EXTRACT
# =========================================================
def extract():
    df_vuelos = pd.read_csv(DATASET_1)
    df_reservas = pd.read_csv(DATASET_2, sep=";")
    return df_vuelos, df_reservas


# =========================================================
# TRANSFORM
# =========================================================
def transform(df_vuelos, df_reservas):
    df_vuelos = df_vuelos.copy()
    df_reservas = df_reservas.copy()

    # -----------------------------------------------------
    # 1. Crear booking_id para unir por posición
    # -----------------------------------------------------
    df_vuelos["booking_id"] = range(1, len(df_vuelos) + 1)
    df_reservas["booking_id"] = range(1, len(df_reservas) + 1)

    # -----------------------------------------------------
    # 2. Limpiar vuelos
    # -----------------------------------------------------
    df_vuelos["airline_code"] = df_vuelos["airline_code"].apply(normalize_upper)
    df_vuelos["airline_name"] = df_vuelos["airline_name"].apply(normalize_airline_name)
    df_vuelos["origin_airport"] = df_vuelos["origin_airport"].apply(normalize_upper)
    df_vuelos["destination_airport"] = df_vuelos["destination_airport"].apply(normalize_upper)
    df_vuelos["status"] = df_vuelos["status"].apply(normalize_upper)
    df_vuelos["aircraft_type"] = df_vuelos["aircraft_type"].apply(normalize_upper)
    df_vuelos["cabin_class"] = df_vuelos["cabin_class"].apply(normalize_upper)

    df_vuelos["departure_datetime"] = parse_datetime_mixed(df_vuelos["departure_datetime"])
    df_vuelos["arrival_datetime"] = parse_datetime_mixed(df_vuelos["arrival_datetime"])

    df_vuelos["duration_min"] = pd.to_numeric(df_vuelos["duration_min"], errors="coerce")
    df_vuelos["delay_min"] = pd.to_numeric(df_vuelos["delay_min"], errors="coerce")

    # Si está ON_TIME y delay viene nulo, se vuelve 0
    mask_on_time = df_vuelos["status"] == "ON_TIME"
    df_vuelos.loc[mask_on_time, "delay_min"] = df_vuelos.loc[mask_on_time, "delay_min"].fillna(0)

    # -----------------------------------------------------
    # 3. Limpiar reservas / pasajeros
    # -----------------------------------------------------
    df_reservas["passenger_gender"] = df_reservas["passenger_gender"].apply(normalize_gender)
    df_reservas["passenger_age"] = pd.to_numeric(df_reservas["passenger_age"], errors="coerce")
    df_reservas["rango_edad"] = df_reservas["passenger_age"].apply(age_range)

    df_reservas["passenger_nationality"] = df_reservas["passenger_nationality"].apply(
        lambda x: normalize_upper(x, "UNKNOWN")
    )
    df_reservas["sales_channel"] = df_reservas["sales_channel"].apply(
        lambda x: normalize_upper(x, "UNKNOWN")
    )
    df_reservas["payment_method"] = df_reservas["payment_method"].apply(
        lambda x: normalize_upper(x, "UNKNOWN")
    )
    df_reservas["currency"] = df_reservas["currency"].apply(
        lambda x: normalize_upper(x, "UNKNOWN")
    )

    df_reservas["booking_datetime"] = parse_datetime_mixed(df_reservas["booking_datetime"])
    df_reservas["ticket_price"] = df_reservas["ticket_price"].apply(normalize_price)
    df_reservas["ticket_price_usd_est"] = pd.to_numeric(df_reservas["ticket_price_usd_est"], errors="coerce")
    df_reservas["bags_total"] = pd.to_numeric(df_reservas["bags_total"], errors="coerce").fillna(0).astype(int)
    df_reservas["bags_checked"] = pd.to_numeric(df_reservas["bags_checked"], errors="coerce").fillna(0).astype(int)

    # -----------------------------------------------------
    # 4. Unir datasets
    # -----------------------------------------------------
    df = pd.merge(df_vuelos, df_reservas, on="booking_id", how="inner")

    # -----------------------------------------------------
    # 5. Crear dimensiones
    # -----------------------------------------------------
    dim_pasajero = (
        df[["passenger_id", "passenger_gender", "passenger_age", "rango_edad", "passenger_nationality"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_pasajero.insert(0, "id_pasajero", range(1, len(dim_pasajero) + 1))
    dim_pasajero = dim_pasajero.rename(columns={
        "passenger_gender": "genero",
        "passenger_age": "edad",
        "passenger_nationality": "nacionalidad"
    })

    dim_aerolinea = (
        df[["airline_code", "airline_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_aerolinea.insert(0, "id_aerolinea", range(1, len(dim_aerolinea) + 1))

    dim_aeropuerto = pd.DataFrame({
        "codigo_iata": pd.concat([df["origin_airport"], df["destination_airport"]], ignore_index=True)
    }).drop_duplicates().reset_index(drop=True)
    dim_aeropuerto.insert(0, "id_aeropuerto", range(1, len(dim_aeropuerto) + 1))

    dim_vuelo = (
        df[["flight_number", "aircraft_type", "cabin_class", "status"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_vuelo.insert(0, "id_vuelo", range(1, len(dim_vuelo) + 1))

    dim_venta = (
        df[["sales_channel", "payment_method", "currency"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_venta.insert(0, "id_venta", range(1, len(dim_venta) + 1))
    dim_venta = dim_venta.rename(columns={
        "sales_channel": "canal_venta",
        "payment_method": "metodo_pago"
    })

    dim_fecha = build_dim_fecha(
        pd.concat([df["booking_datetime"], df["departure_datetime"]], ignore_index=True)
    )

    # -----------------------------------------------------
    # 6. Asignar llaves sustitutas
    # -----------------------------------------------------
    df = df.merge(
        dim_pasajero,
        left_on=["passenger_id", "passenger_gender", "passenger_age", "rango_edad", "passenger_nationality"],
        right_on=["passenger_id", "genero", "edad", "rango_edad", "nacionalidad"],
        how="left"
    )

    df = df.merge(
        dim_aerolinea,
        on=["airline_code", "airline_name"],
        how="left"
    )

    df = df.merge(
        dim_aeropuerto.rename(columns={
            "id_aeropuerto": "id_aeropuerto_origen",
            "codigo_iata": "origin_airport"
        }),
        on="origin_airport",
        how="left"
    )

    df = df.merge(
        dim_aeropuerto.rename(columns={
            "id_aeropuerto": "id_aeropuerto_destino",
            "codigo_iata": "destination_airport"
        }),
        on="destination_airport",
        how="left"
    )

    df = df.merge(
        dim_vuelo,
        on=["flight_number", "aircraft_type", "cabin_class", "status"],
        how="left"
    )

    df = df.merge(
        dim_venta.rename(columns={
            "canal_venta": "sales_channel",
            "metodo_pago": "payment_method"
        }),
        on=["sales_channel", "payment_method", "currency"],
        how="left"
    )

    df["id_fecha_reserva"] = pd.to_datetime(df["booking_datetime"]).dt.strftime("%Y%m%d")
    df["id_fecha_salida"] = pd.to_datetime(df["departure_datetime"]).dt.strftime("%Y%m%d")

    df["id_fecha_reserva"] = pd.to_numeric(df["id_fecha_reserva"], errors="coerce").fillna(0).astype(int)
    df["id_fecha_salida"] = pd.to_numeric(df["id_fecha_salida"], errors="coerce").fillna(0).astype(int)

    # -----------------------------------------------------
    # 7. Crear tabla de hechos
    # -----------------------------------------------------
    fact_booking_flight = df[[
        "booking_id",
        "record_id",
        "id_pasajero",
        "id_aerolinea",
        "id_aeropuerto_origen",
        "id_aeropuerto_destino",
        "id_fecha_reserva",
        "id_fecha_salida",
        "id_vuelo",
        "id_venta",
        "ticket_price_usd_est",
        "duration_min",
        "delay_min",
        "bags_total",
        "bags_checked"
    ]].copy()

    fact_booking_flight = fact_booking_flight.rename(columns={
        "ticket_price_usd_est": "ticket_price_usd"
    })

    fact_booking_flight["ticket_price_usd"] = pd.to_numeric(
        fact_booking_flight["ticket_price_usd"], errors="coerce"
    ).fillna(0)

    fact_booking_flight["bags_total"] = fact_booking_flight["bags_total"].fillna(0).astype(int)
    fact_booking_flight["bags_checked"] = fact_booking_flight["bags_checked"].fillna(0).astype(int)
    fact_booking_flight["flight_count"] = 1

    # -----------------------------------------------------
    # 8. Orden final de columnas
    # -----------------------------------------------------
    dim_pasajero = dim_pasajero[
        ["id_pasajero", "passenger_id", "genero", "edad", "rango_edad", "nacionalidad"]
    ]

    dim_aerolinea = dim_aerolinea[
        ["id_aerolinea", "airline_code", "airline_name"]
    ]

    dim_aeropuerto = dim_aeropuerto[
        ["id_aeropuerto", "codigo_iata"]
    ]

    dim_vuelo = dim_vuelo[
        ["id_vuelo", "flight_number", "aircraft_type", "cabin_class", "status"]
    ]

    dim_venta = dim_venta[
        ["id_venta", "canal_venta", "metodo_pago", "currency"]
    ]

    fact_booking_flight = fact_booking_flight[
        [
            "booking_id",
            "record_id",
            "id_pasajero",
            "id_aerolinea",
            "id_aeropuerto_origen",
            "id_aeropuerto_destino",
            "id_fecha_reserva",
            "id_fecha_salida",
            "id_vuelo",
            "id_venta",
            "ticket_price_usd",
            "duration_min",
            "delay_min",
            "bags_total",
            "bags_checked",
            "flight_count"
        ]
    ]

    return {
        "dim_pasajero": dim_pasajero,
        "dim_aerolinea": dim_aerolinea,
        "dim_aeropuerto": dim_aeropuerto,
        "dim_fecha": dim_fecha,
        "dim_vuelo": dim_vuelo,
        "dim_venta": dim_venta,
        "fact_booking_flight": fact_booking_flight
    }


# =========================================================
# LOAD
# =========================================================
def load_to_sql(tables):
    engine = get_engine()

    with engine.begin() as conn:
        # Borrar primero hechos y luego dimensiones
        conn.exec_driver_sql("DELETE FROM fact_booking_flight")
        conn.exec_driver_sql("DELETE FROM dim_vuelo")
        conn.exec_driver_sql("DELETE FROM dim_venta")
        conn.exec_driver_sql("DELETE FROM dim_fecha")
        conn.exec_driver_sql("DELETE FROM dim_aeropuerto")
        conn.exec_driver_sql("DELETE FROM dim_aerolinea")
        conn.exec_driver_sql("DELETE FROM dim_pasajero")

        tables["dim_pasajero"].to_sql("dim_pasajero", conn, if_exists="append", index=False)
        tables["dim_aerolinea"].to_sql("dim_aerolinea", conn, if_exists="append", index=False)
        tables["dim_aeropuerto"].to_sql("dim_aeropuerto", conn, if_exists="append", index=False)
        tables["dim_fecha"].to_sql("dim_fecha", conn, if_exists="append", index=False)
        tables["dim_vuelo"].to_sql("dim_vuelo", conn, if_exists="append", index=False)
        tables["dim_venta"].to_sql("dim_venta", conn, if_exists="append", index=False)
        tables["fact_booking_flight"].to_sql("fact_booking_flight", conn, if_exists="append", index=False)


# =========================================================
# MAIN
# =========================================================
def main():
    df_vuelos, df_reservas = extract()
    tables = transform(df_vuelos, df_reservas)

    # Exportar CSV limpios
    for name, df in tables.items():
        df.to_csv(f"{name}.csv", index=False)

    if LOAD_TO_SQL:
        load_to_sql(tables)

    print("ETL completado.")
    for name, df in tables.items():
        print(f"{name}: {df.shape}")


if __name__ == "__main__":
    main()