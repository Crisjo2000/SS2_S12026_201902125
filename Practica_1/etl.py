import logging
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).parent
DATASET1 = BASE_DIR / "csvs" / "Dataset_1.csv"
DATASET2 = BASE_DIR / "csvs" / "Dataset_2.csv"

# ------------------------- Conexión con SQL Server

SQL_SERVER = "localhost"
SQL_DATABASE = "VuelosDB"
ENGINE_URL = (
    f"mssql+pyodbc://{SQL_SERVER}/{SQL_DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "etl.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

#----------------------------EXTRACCIÓN


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    log.info("FASE 1: Extracción")

    try:
        df_vuelos = pd.read_csv(DATASET1, encoding="utf-8-sig")
        log.info(f"Dataset 1 (vuelos)     → {len(df_vuelos):,} filas, {df_vuelos.shape[1]} columnas")

        df_pasajeros = pd.read_csv(DATASET2, sep=";", encoding="utf-8-sig")
        log.info(f"Dataset 2 (pasajeros)  → {len(df_pasajeros):,} filas, {df_pasajeros.shape[1]} columnas")

        return df_vuelos, df_pasajeros
    
    except FileNotFoundError as e:
        log.error(f"Archivo no encontrado: {e}")
        raise




#----------------------------TRANSFORMACIÓN

def parsear_datatime(series: pd.Series) -> pd.Series:

    formats = [
        "%d/%m/%Y %H:%M",
        "%m-%d-%Y %I:%M %p",
        "%Y-%m-%d %H:%M:%S",
    ]

    parsed = pd.Series(pd.NaT, index = series.index)
    mask_remaining = pd.Series(True, index=series.index)

    for fmt in formats:
        idx = series[mask_remaining].dropna().index

        try:
            resultado = pd.to_datetime(series[idx], format=fmt, errors="coerce")
            filled = resultado.notna()
            parsed[resultado[filled].index] = resultado[filled]
            mask_remaining[resultado[filled].index] = False
        
        except Exception:
            continue
    
    remaining_idx = series[mask_remaining & series.notna()].index
    if len(remaining_idx):
        parsed[remaining_idx] = pd.to_datetime(series[remaining_idx], errors="coerce", dayfirst=True)
    return parsed

def normalizar_genero(series: pd.Series) -> pd.Series:
    mapping = {
        "m": "M", "masculino": "M", "male": "M",
        "f": "F", "femenino": "F", "female": "F", "feminino": "F",
        "x": "X", "NoBinario": "X",
    }
    return series.str.strip().str.lower().map(mapping).fillna("X")


def normalizar_aeropuerto(series: pd.Series) -> pd.Series:
    return series.str.strip().str.upper()

def transformar_vuelos(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    log.info("FASE 2: Transformación (vuelos)")
    df = df.copy()

#Limpieza básica


    df["origin_airport"]      = normalizar_aeropuerto(df["origin_airport"])
    df["destination_airport"] = normalizar_aeropuerto(df["destination_airport"])
    df["airline_code"]        = df["airline_code"].str.strip().str.upper()
    df["airline_name"]        = df["airline_name"].str.strip()
    df["flight_number"]       = df["flight_number"].str.strip().str.upper()
    df["status"]              = df["status"].str.strip().str.upper()
    df["cabin_class"]         = df["cabin_class"].str.strip().str.upper()
    df["aircraft_type"]       = df["aircraft_type"].str.strip().str.upper()

#Fechas


    df["departure_datetime"] = parsear_datatime(df["departure_datetime"])
    df["arrival_datetime"]   = parsear_datatime(df["arrival_datetime"])

#Nulos Numéricos


    df["delay_min"]    = pd.to_numeric(df["delay_min"],    errors="coerce").fillna(0)
    df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")

    mask = df["duration_min"].isna() & df["departure_datetime"].notna() & df["arrival_datetime"].notna()
    df.loc[mask, "duration_min"] = (
        (df.loc[mask, "arrival_datetime"] - df.loc[mask, "departure_datetime"])
        .dt.total_seconds() / 60
    )

    log.info(f"  Nulos en duration_min tras imputación: {df['duration_min'].isna().sum()}")
    log.info(f"  Filas con status CANCELLED (sin asiento): {(df['status']=='CANCELLED').sum()}")

#Dimensional_aerolínea
    dim_aerolinea = (
        df[["airline_code", "airline_name"]]
        .drop_duplicates(subset="airline_code")
        .reset_index(drop=True)
    )
    dim_aerolinea.insert(0, "id_aerolinea", range(1, len(dim_aerolinea) + 1))
    log.info(f"  DIM_AEROLINEA → {len(dim_aerolinea)} registros")

#dimensional_aeropuerto
    aeropuertos = pd.concat([
        df["origin_airport"].rename("codigo_iata"),
        df["destination_airport"].rename("codigo_iata"),
    ]).drop_duplicates().dropna().sort_values().reset_index(drop=True)
    dim_aeropuerto = pd.DataFrame({"codigo_iata": aeropuertos})
    dim_aeropuerto.insert(0, "id_aeropuerto", range(1, len(dim_aeropuerto) + 1))
    log.info(f"  DIM_AEROPUERTO → {len(dim_aeropuerto)} registros")

#dimensional_avion
    dim_avion = (
        df[["aircraft_type"]].drop_duplicates().dropna()
        .sort_values("aircraft_type").reset_index(drop=True)
    )
    dim_avion.insert(0, "id_avion", range(1, len(dim_avion) + 1))
    log.info(f"  DIM_AVION → {len(dim_avion)} registros")

#dimensional_fecha
    fechas_unicas = df["departure_datetime"].dropna().dt.normalize().drop_duplicates().sort_values()
    dim_fecha = pd.DataFrame({
        "fecha":         fechas_unicas.values,
        "anio":          fechas_unicas.dt.year.values,
        "mes":           fechas_unicas.dt.month.values,
        "nombre_mes":    fechas_unicas.dt.strftime("%B").values,
        "trimestre":     fechas_unicas.dt.quarter.values,
        "dia":           fechas_unicas.dt.day.values,
        "dia_semana":    fechas_unicas.dt.day_name().values,
        "es_fin_semana": (fechas_unicas.dt.dayofweek >= 5).astype(int).values,
    })
    dim_fecha.insert(0, "id_fecha", range(1, len(dim_fecha) + 1))
    log.info(f"  DIM_FECHA → {len(dim_fecha)} registros")

#dimensional_estado
    dim_estado = pd.DataFrame({
        "id_estado":   [1, 2, 3, 4],
        "codigo":      ["ON_TIME", "DELAYED", "CANCELLED", "DIVERTED"],
        "descripcion": ["A tiempo", "Retrasado", "Cancelado", "Desviado"],
    })

# Hecho_vuelos
    aeropuerto_map = dim_aeropuerto.set_index("codigo_iata")["id_aeropuerto"]
    aerolinea_map  = dim_aerolinea.set_index("airline_code")["id_aerolinea"]
    avion_map      = dim_avion.set_index("aircraft_type")["id_avion"]
    fecha_map      = dim_fecha.set_index("fecha")["id_fecha"]
    estado_map     = dim_estado.set_index("codigo")["id_estado"]

    fact = df.copy()
    fact["id_aerolinea"]   = fact["airline_code"].map(aerolinea_map)
    fact["id_origen"]      = fact["origin_airport"].map(aeropuerto_map)
    fact["id_destino"]     = fact["destination_airport"].map(aeropuerto_map)
    fact["id_avion"]       = fact["aircraft_type"].map(avion_map)
    fact["id_estado"]      = fact["status"].map(estado_map)
    fact["id_fecha"]       = fact["departure_datetime"].dt.normalize().map(fecha_map)

    fact_vuelo = fact[[
        "record_id", "id_aerolinea", "id_origen", "id_destino",
        "id_avion", "id_estado", "id_fecha",
        "flight_number", "cabin_class", "seat",
        "departure_datetime", "arrival_datetime",
        "duration_min", "delay_min",
    ]].rename(columns={"record_id": "id_vuelo"})

    log.info(f"  FACT_VUELO → {len(fact_vuelo)} registros")

    return {
        "DIM_AEROLINEA":  dim_aerolinea,
        "DIM_AEROPUERTO": dim_aeropuerto,
        "DIM_AVION":      dim_avion,
        "DIM_FECHA":      dim_fecha,
        "DIM_ESTADO":     dim_estado,
        "FACT_VUELO":     fact_vuelo,
    }

def transformar_pasajeros(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    log.info("FASE 2: Trasformación (pasajeros)")
    df = df.copy()

#limpiar
    df["passenger_gender"]      = normalizar_genero(df["passenger_gender"])
    df["passenger_nationality"] = df["passenger_nationality"].str.strip().str.upper().fillna("DESCONOCIDO")
    df["sales_channel"]         = df["sales_channel"].str.strip().str.upper().fillna("DESCONOCIDO")
    df["payment_method"]        = df["payment_method"].str.strip().str.upper()
    df["currency"]              = df["currency"].str.strip().str.upper()
    df["booking_datetime"]      = parsear_datatime(df["booking_datetime"])

#precio de ticket comas -> puntos
    df["ticket_price"] = (
        df["ticket_price"].astype(str).str.replace(",", ".", regex=False)
    )
    df["ticket_price"]         = pd.to_numeric(df["ticket_price"],         errors="coerce")
    df["ticket_price_usd_est"] = pd.to_numeric(df["ticket_price_usd_est"], errors="coerce")


    mediana_edad = df["passenger_age"].median()
    df["passenger_age"] = df["passenger_age"].fillna(mediana_edad).astype(int)

    log.info(f"  Edad mediana imputada: {mediana_edad}")
    log.info(f"  Géneros normalizados: {df['passenger_gender'].value_counts().to_dict()}")

#dimensional_pasajero

    dim_pasajero = df[[
        "passenger_id", "passenger_gender", "passenger_age", "passenger_nationality",
    ]].copy()
    dim_pasajero.columns = ["id_pasajero", "genero", "edad", "nacionalidad"]
    log.info(f"  DIM_PASAJERO → {len(dim_pasajero)} registros")

#hecho_reserva

    fact_reserva = df[[
        "passenger_id", "booking_datetime", "sales_channel",
        "payment_method", "ticket_price", "currency",
        "ticket_price_usd_est", "bags_total", "bags_checked",
    ]].copy()
    fact_reserva.columns = [
        "id_pasajero", "fecha_reserva", "canal_venta",
        "metodo_pago", "precio_ticket", "moneda",
        "precio_usd", "total_maletas", "maletas_documentadas",
    ]

# La unión con FACT_VUELO se hace por posición (mismos 10 000 registros, mismo orden)

    fact_reserva.insert(0, "id_reserva", range(1, len(fact_reserva) + 1))
    fact_reserva.insert(1, "id_vuelo",   range(1, len(fact_reserva) + 1))

    log.info(f"  FACT_RESERVA → {len(fact_reserva)} registros")

    return {
        "DIM_PASAJERO": dim_pasajero,
        "FACT_RESERVA": fact_reserva,
    }

#-------------------------------- CARGA

def load(tables: dict[str, pd.DataFrame], engine) -> None:
    log.info("Fase 3: Carga")

    load_order = [
        "DIM_AEROLINEA", "DIM_AEROPUERTO", "DIM_AVION",
        "DIM_FECHA", "DIM_ESTADO", "DIM_PASAJERO",
        "FACT_VUELO", "FACT_RESERVA",
    ]

    with engine.begin() as conn:
        for table_name in load_order:
            if table_name not in tables:
                continue
            df = tables[table_name]
            try:
                df.to_sql(
                    name=table_name.lower(),
                    con=conn,
                    if_exists="append",
                    index=False,
                    chunksize=500,
                )
                log.info(f"{table_name:20s} → {len(df):,} filas cargadas")
            except Exception as e:
                log.error(f" Error Cargando{table_name}: {e}")
                raise
    log.info("Carga completada exitosamente!")



def main():
    start = datetime.now()
    log.info("══════════════════════════════════════════")
    log.info("  INICIO DEL PROCESO ETL")
    log.info(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("══════════════════════════════════════════")

    # EXTRACCIÓN
    df_flights, df_passengers = extract()

    # TRANSFORMACIÓN
    flight_tables    = transformar_vuelos(df_flights)
    passenger_tables = transformar_pasajeros(df_passengers)
    all_tables = {**flight_tables, **passenger_tables}

    log.info("\n── Vista previa de tablas transformadas ──")
    for name, df in all_tables.items():
        log.info(f"  {name:20s}: {df.shape[0]:,} filas × {df.shape[1]} columnas")

    # Exportar CSVs limpios (útil para revisión / importación manual)
    out_dir = BASE_DIR / "csvs_limpios"
    out_dir.mkdir(exist_ok=True)
    for name, df in all_tables.items():
        df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    log.info(f"\nCSVs limpios exportados en: {out_dir}")

    # CARGA A SQL SERVER
    try:
        engine = create_engine(ENGINE_URL, fast_executemany=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))   # prueba de conexión
        log.info("Conexión a SQL Server establecida.")
        load(all_tables, engine)
    except Exception as e:
        log.warning(f"No se pudo conectar a SQL Server: {e}")
        log.warning("Los datos transformados fueron exportados como CSV en /output/")

    elapsed = datetime.now() - start
    log.info(f"\nTiempo total: {elapsed}")
    log.info("══════════════════════════════════════════")
    log.info("  PROCESO ETL FINALIZADO")
    log.info("══════════════════════════════════════════")

    
if __name__ == "__main__":
    main()