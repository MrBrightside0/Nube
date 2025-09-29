import os 
import pandas as pd
import matplotlib.pyplot as plt
import glob
from prophet import Prophet
from statsmodels.tsa.seasonal import seasonal_decompose

def predict_pollutant(location: str = "Universidad", pollutant: str = "pm10", days_ahead: int = 30):
    path = f"data/{location}/*.csv"
    files = glob.glob(path)
    if not files:
        print(f"[WARN] No se encontraron archivos CSV en {path}")
        return

    print(f"[INFO] Leyendo {len(files)} archivos CSV de {location}")

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.columns = ["station_id", "sensor_id", "station_name", "datetime", 
                  "lat", "lon", "pollutant", "unit", "value"]

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert(None)

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["datetime", "value"])
    df = df[df["pollutant"] == pollutant]

    if df.empty:
        print(f"[WARN] No hay datos para el contaminante {pollutant}")
        return

    # Promedio diario
    daily = df.set_index("datetime").resample("D")["value"].mean().reset_index()
    daily = daily.rename(columns={"datetime": "ds", "value": "y"})

    model = Prophet()
    model.fit(daily)

    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)

    # Graficar
    fig1 = model.plot(forecast)
    plt.title(f"Predicción de {pollutant} para {location}")
    plt.xlabel("Fecha")
    plt.ylabel("Concentración")
    plt.show()

    fig2 = model.plot_components(forecast)
    plt.show()

    return forecast


def graph_data(location: str = "Universidad", fill_method: str = "interpolate") -> None:
    path = f"data/{location}/*.csv"
    files = glob.glob(path)

    if not files:
        print(f"[ERROR] No se encontraron archivos CSV en {path}")
        return
    
    print(f"[INFO] Leyendo {len(files)} archivos CSV de {location}")

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.columns = ["station_id", "sensor_id", "station_name", "datetime", 
                  "lat", "lon", "pollutant", "unit", "value"]

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert(None)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["datetime", "value"])

    pivot = df.pivot_table(index="datetime", columns="pollutant", values="value")
    pivot_daily = pivot.resample("D").mean()

    if fill_method == "zero":
        pivot_filled = pivot_daily.fillna(0)
    elif fill_method == "ffill":
        pivot_filled = pivot_daily.ffill()
    elif fill_method == "bfill":
        pivot_filled = pivot_daily.bfill()
    elif fill_method == "interpolate":
        pivot_filled = pivot_daily.interpolate(method="time")
    else:
        pivot_filled = pivot_daily

    pivot_filled.plot(figsize=(12,6))
    plt.title(f"Promedio diario de contaminantes en {location}")
    plt.xlabel("Fecha")
    plt.ylabel("Concentración")
    plt.legend(title="Contaminante")
    plt.grid(True)
    plt.show()


def seasonal_analysis(location: str = "Universidad", pollutant: str = "pm10") -> None:
    path = f"data/{location}/*.csv"
    files = glob.glob(path)
    if not files:
        print(f"[WARN] No se encontraron archivos CSV en {path}")
        return

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.columns = ["station_id", "sensor_id", "station_name", "datetime", 
                  "lat", "lon", "pollutant", "unit", "value"]

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert(None)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["datetime", "value"])
    df = df[df["pollutant"] == pollutant]

    if df.empty:
        print(f"[WARN] No hay datos para {pollutant}")
        return

    daily = df.set_index("datetime").resample("D")["value"].mean()
    daily_df = daily.to_frame().reset_index()
    daily_df["month"] = daily_df["datetime"].dt.month
    daily_df["weekday"] = daily_df["datetime"].dt.day_name()

    monthly_avg = daily_df.groupby("month")["value"].mean()
    monthly_avg.plot(kind="bar", figsize=(10,5), color="skyblue")
    plt.title(f"Promedio mensual de {pollutant} ({location})")
    plt.xlabel("Mes")
    plt.ylabel("Concentración")
    plt.show()

    # Estacionalidad semanal
    weekday_avg = daily_df.groupby("weekday")["value"].mean()
    weekday_avg = weekday_avg.reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    weekday_avg.plot(kind="bar", figsize=(10,5), color="salmon")
    plt.title(f"Promedio por día de la semana de {pollutant} ({location})")
    plt.xlabel("Día de la semana")
    plt.ylabel("Concentración")
    plt.show()

    result = seasonal_decompose(daily, model='additive', period=365)
    result.plot()
    plt.show()


if __name__ == "__main__":
    seasonal_analysis(pollutant="pm10")

