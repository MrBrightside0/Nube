import glob
import os
from pathlib import Path

import pandas as pd
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Monterrey")
WEATHER_COLS = ["temp", "rhum", "prcp", "wdir", "wspd", "pres", "cldc", "coco"]
AIR_PARAMETERS = ["co", "no", "no2", "nox", "o3", "pm10", "pm25", "so2"]


def _read_weather_file(path: str) -> tuple[str, pd.DataFrame] | None:
    """Carga un archivo de Meteostat y regresa un dataframe con sufijo por estación."""
    station_id = Path(path).stem.split("_")[0]
    df = pd.read_csv(path)

    if not {"year", "month", "day", "hour"}.issubset(df.columns):
        return None

    df = df[(df["year"] >= 2021) & (df["year"] <= 2025)]
    if df.empty:
        return None

    datetimes = pd.to_datetime(
        df[["year", "month", "day", "hour"]], errors="coerce"
    )
    datetimes = datetimes.dt.tz_localize(
        LOCAL_TZ,
        nonexistent="shift_forward",
        ambiguous="NaT",
    ).dt.tz_convert("UTC")
    df["datetime"] = datetimes

    cols_present = [col for col in WEATHER_COLS if col in df.columns]
    if not cols_present:
        return None

    df = df.dropna(subset=["datetime"])[["datetime", *cols_present]]
    df = df.groupby("datetime", as_index=False).mean(numeric_only=True)

    rename_map = {col: f"{col}_{station_id}" for col in cols_present}
    df = df.rename(columns=rename_map)
    return station_id, df


def load_weather_frames(base_path: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(base_path, "*.csv")) + glob.glob(
        os.path.join(base_path, "*.csv.gz")
    )

    station_frames: dict[str, list[pd.DataFrame]] = {}
    for file in files:
        wf = _read_weather_file(file)
        if wf is None:
            continue
        station_id, frame = wf
        station_frames.setdefault(station_id, []).append(frame)

    if not station_frames:
        raise ValueError("[ERROR] No se encontraron datos de clima válidos")

    frames: list[pd.DataFrame] = []
    for station_id, partials in station_frames.items():
        station_df = pd.concat(partials, ignore_index=True)
        station_df = station_df.groupby("datetime", as_index=False).mean(numeric_only=True)
        frames.append(station_df)

    weather = frames[0]
    for frame in frames[1:]:
        weather = pd.merge(weather, frame, on="datetime", how="outer")
    weather.sort_values("datetime", inplace=True)
    weather.reset_index(drop=True, inplace=True)

    temp_cols = [col for col in weather.columns if col.startswith("temp_")]
    if temp_cols:
        weather["temp_mean"] = weather[temp_cols].mean(axis=1)
    hum_cols = [col for col in weather.columns if col.startswith("rhum_")]
    if hum_cols:
        weather["rhum_mean"] = weather[hum_cols].mean(axis=1)
    wind_cols = [col for col in weather.columns if col.startswith("wspd_")]
    if wind_cols:
        weather["wspd_mean"] = weather[wind_cols].mean(axis=1)

    print(f"[INFO] Clima cargado. Filas: {weather.shape[0]}, Columnas: {weather.shape[1]}")
    return weather


def load_air_data(base_path: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for location_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, location_folder)
        if not os.path.isdir(folder_path):
            continue

        files = glob.glob(os.path.join(folder_path, "*.csv")) + glob.glob(
            os.path.join(folder_path, "*.csv.gz")
        )

        for file in files:
            df = pd.read_csv(file)

            if "parameter" not in df.columns and "pollutant" in df.columns:
                df = df.rename(columns={"pollutant": "parameter"})
            if "value" not in df.columns and "measurement" in df.columns:
                df = df.rename(columns={"measurement": "value"})

            dt = pd.to_datetime(df.get("datetime"), errors="coerce", utc=True)
            df["datetime"] = dt
            df = df.dropna(subset=["datetime", "parameter", "value"])

            df = df[(df["datetime"].dt.year >= 2021) & (df["datetime"].dt.year <= 2025)]
            if df.empty:
                continue

            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df.dropna(subset=["value"])

            df["location_id"] = pd.to_numeric(df.get("location_id"), errors="coerce")
            df = df.dropna(subset=["location_id"])

            df["location_id"] = df["location_id"].astype(int)
            frames.append(df)

    if not frames:
        raise ValueError("[ERROR] No se encontraron datos de calidad del aire válidos")

    air = pd.concat(frames, ignore_index=True)
    meta_cols = [col for col in ["location", "lat", "lon"] if col in air.columns]

    pivot_index = ["datetime", "location_id", *meta_cols]
    air_pivot = (
        air.pivot_table(
            index=pivot_index,
            columns="parameter",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
        .sort_values(["location_id", "datetime"])
    )

    air_pivot.columns = [
        "location_name" if col == "location" else col for col in air_pivot.columns
    ]

    print(f"[INFO] Aire cargado. Filas: {air_pivot.shape[0]}, Columnas: {air_pivot.shape[1]}")
    return air_pivot


def enrich_air_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.sort_values(["location_id", "datetime"], inplace=True)

    pollutant_cols = [col for col in AIR_PARAMETERS if col in df.columns]

    for col in pollutant_cols:
        group = df.groupby("location_id")[col]
        df[f"{col}_roll6"] = group.transform(lambda s: s.rolling(window=6, min_periods=1).mean())
        df[f"{col}_roll24"] = group.transform(lambda s: s.rolling(window=24, min_periods=1).mean())
        df[f"{col}_diff1"] = group.transform(lambda s: s.diff())

    if {"pm10", "pm25"}.issubset(df.columns):
        df["pm_ratio"] = df["pm10"] / df["pm25"].replace(0, pd.NA)

    local_dt = df["datetime"].dt.tz_convert(LOCAL_TZ)
    df["hour"] = local_dt.dt.hour
    df["day_of_week"] = local_dt.dt.dayofweek
    df["month"] = local_dt.dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    return df


def build_dataset() -> pd.DataFrame:
    weather = load_weather_frames("weather_data")
    air = load_air_data("air_data")

    dataset = pd.merge(air, weather, on="datetime", how="inner")
    dataset = enrich_air_metrics(dataset)
    dataset.sort_values(["datetime", "location_id"], inplace=True)
    dataset.reset_index(drop=True, inplace=True)

    print(f"[INFO] Dataset unido. Filas: {dataset.shape[0]}, Columnas: {dataset.shape[1]}")
    return dataset


def main() -> None:
    dataset = build_dataset()

    os.makedirs("output", exist_ok=True)
    dataset.to_csv("output/dataset_final.csv", index=False)
    print("[INFO] Dataset creado: output/dataset_final.csv")


if __name__ == "__main__":
    main()
