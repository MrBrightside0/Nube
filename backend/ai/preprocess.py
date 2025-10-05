#!/usr/bin/env python3
"""
build_dataset.py
Preprocesa automáticamente todos los archivos .nc en ./data
y genera un dataset final para modelos de predicción de calidad del aire.

Autor: Mario | Hackathon NASA 2025
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "dataset_final.csv"

# Bounding box de Monterrey
BBOX = (-100.9, 25.3, -99.8, 26.1)


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def _log(msg):
    print(f"[INFO] {msg}")

def clip_region(ds):
    """Recorta el dataset a la región de interés."""
    lon_min, lat_min, lon_max, lat_max = BBOX
    try:
        return ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    except Exception:
        return ds


def load_merra2_file(file_path: Path):
    """Procesa un archivo MERRA-2 individual (SLV o AER)."""
    ds = xr.open_dataset(file_path)
    ds = clip_region(ds)

    if "M2T1NXSLV" in file_path.name:
        vars_to_keep = ["T2M", "QV2M", "U10M", "V10M", "PS"]
    elif "M2T1NXAER" in file_path.name:
        vars_to_keep = ["BCSMASS", "OCSMASS", "SO4SMASS", "DUSMASS", "TOTEXTTAU"]
    else:
        return None

    ds = ds[vars_to_keep].to_dataframe().reset_index()
    ds["datetime"] = pd.to_datetime(ds["time"], errors="coerce")
    ds = ds.drop(columns=["time"], errors="ignore")

    # Calcular derivados meteorológicos si aplica
    if "U10M" in ds and "V10M" in ds:
        ds["wind_speed"] = np.sqrt(ds["U10M"]**2 + ds["V10M"]**2)
        ds["wind_dir"] = np.degrees(np.arctan2(ds["V10M"], ds["U10M"]))

    # Calcular PM2.5 y PM10 si tiene aerosoles
    if all(v in ds for v in ["BCSMASS", "OCSMASS", "SO4SMASS", "DUSMASS"]):
        ds["PM25_est"] = (ds["BCSMASS"] + ds["OCSMASS"] + ds["SO4SMASS"] + ds["DUSMASS"]) * 1e9
        ds["PM10_est"] = ds["PM25_est"] * 1.8

    return ds


def load_tempo_file(file_path: Path):
    """Procesa un archivo TEMPO (NO2 u O3)."""
    ds = xr.open_dataset(file_path)
    ds = clip_region(ds)

    if "NO2" in file_path.name:
        vars_to_keep = ["vertical_column_troposphere"]
        name_map = {"vertical_column_troposphere": "NO2_tropo"}
    elif "O3" in file_path.name:
        vars_to_keep = ["column_amount_o3"]
        name_map = {"column_amount_o3": "O3_total"}
    else:
        return None

    df = ds[vars_to_keep].to_dataframe().reset_index()
    df.rename(columns=name_map, inplace=True)
    df["datetime"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.drop(columns=["time"], errors="ignore")
    return df


def aggregate_hourly(df):
    """Promedia espacialmente y agrupa por hora."""
    if "datetime" not in df:
        return df
    df = df.groupby("datetime").mean(numeric_only=True).reset_index()
    return df


def add_time_features(df):
    """Agrega columnas temporales para modelado."""
    df["hour"] = df["datetime"].dt.hour
    df["dayofweek"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24)
    return df


# ============================================
# PIPELINE PRINCIPAL
# ============================================

def main():
    _log("Iniciando preprocesamiento global")
    if not DATA_DIR.exists():
        raise FileNotFoundError("No existe carpeta ./data con los archivos descargados")

    all_nc = list(DATA_DIR.rglob("*.nc"))
    if not all_nc:
        raise FileNotFoundError("No se encontraron archivos .nc en ./data")

    tempo_dfs, merra_dfs = [], []

    for file in all_nc:
        if "TEMPO" in file.name.upper():
            df = load_tempo_file(file)
            if df is not None and len(df) > 0:
                tempo_dfs.append(df)
                _log(f"TEMPO procesado: {file.name} ({len(df)} registros)")
        elif "M2T1NX" in file.name.upper():
            df = load_merra2_file(file)
            if df is not None and len(df) > 0:
                merra_dfs.append(df)
                _log(f"MERRA-2 procesado: {file.name} ({len(df)} registros)")

    if not tempo_dfs and not merra_dfs:
        raise RuntimeError("No se pudieron procesar archivos válidos TEMPO o MERRA-2")

    # --- Combinar ---
    _log("Combinando datos TEMPO...")
    tempo_df = pd.concat(tempo_dfs, ignore_index=True) if tempo_dfs else pd.DataFrame()
    tempo_df = aggregate_hourly(tempo_df)

    _log("Combinando datos MERRA-2...")
    merra_df = pd.concat(merra_dfs, ignore_index=True) if merra_dfs else pd.DataFrame()
    merra_df = aggregate_hourly(merra_df)

    _log("Uniendo colecciones por fecha/hora...")
    df = pd.merge_asof(
        tempo_df.sort_values("datetime"),
        merra_df.sort_values("datetime"),
        on="datetime",
        direction="nearest",
        tolerance=pd.Timedelta("30min"),
    )

    # --- Features temporales ---
    df = add_time_features(df)

    # --- Limpieza final ---
    df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    # --- Guardado ---
    OUTPUT_FILE.parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(OUTPUT_FILE, index=False)

    _log(f"✅ Dataset final generado: {OUTPUT_FILE.resolve()}")
    _log(f"Filas totales: {len(df):,}")
    _log(f"Columnas: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()

