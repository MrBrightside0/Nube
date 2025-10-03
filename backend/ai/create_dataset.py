import pandas as pd
import glob
import os

def encontrar_archivos(base_path):
    """Encuentra todos los CSV y CSV.GZ en carpetas y subcarpetas"""
    return glob.glob(os.path.join(base_path, '**', '*.csv'), recursive=True) + \
           glob.glob(os.path.join(base_path, '**', '*.csv.gz'), recursive=True)

# -----------------------------
# Cargar y procesar clima
# -----------------------------
weather_files = encontrar_archivos("weather_data")
weather_dfs = []

for file in weather_files:
    df = pd.read_csv(file)
    
    # Filtrar solo años 2023 a 2025 si existe columna 'year'
    if 'year' in df.columns:
        df = df[df['year'].between(2023, 2025)]
    
    # Crear columna datetime
    df['datetime'] = pd.to_datetime(df[['year','month','day','hour']], errors='coerce')
    df = df.dropna(subset=['datetime'])
    
    # Seleccionar solo columnas presentes
    cols = ['datetime', 'temp', 'rhum', 'prcp', 'wdir', 'wspd', 'wpgt', 'pres', 'cldc', 'coco']
    cols_presentes = [c for c in cols if c in df.columns]
    df = df[cols_presentes]
    
    weather_dfs.append(df)

if not weather_dfs:
    raise ValueError("[INFO] No se encontraron archivos de clima entre 2023 y 2025")

weather = pd.concat(weather_dfs, ignore_index=True)
weather = weather.groupby('datetime').mean().reset_index()
# Convertir a UTC
weather['datetime'] = pd.to_datetime(weather['datetime'], errors='coerce').dt.tz_localize('UTC', ambiguous='NaT')
print(f"[INFO] Clima cargado. Filas: {weather.shape[0]}, Columnas: {weather.shape[1]}")

# -----------------------------
# Cargar y procesar aire
# -----------------------------
air_base = "air_data"
air_dfs = []

for loc_folder in os.listdir(air_base):
    loc_path = os.path.join(air_base, loc_folder)
    if os.path.isdir(loc_path):
        files = glob.glob(os.path.join(loc_path, '*.csv')) + glob.glob(os.path.join(loc_path, '*.csv.gz'))
        for file in files:
            df = pd.read_csv(file)
            
            # Convertir datetime de manera robusta
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', utc=True)
            df = df.dropna(subset=['datetime'])
            
            # Filtrar solo años 2023 a 2025
            df = df[(df['datetime'].dt.year >= 2023) & (df['datetime'].dt.year <= 2025)]
            
            air_dfs.append(df)

if not air_dfs:
    raise ValueError("[INFO] No se encontraron archivos de aire entre 2023 y 2025")

air = pd.concat(air_dfs, ignore_index=True)

# Pivotar: filas = datetime, columnas = cada contaminante
air_pivot = air.pivot_table(index='datetime',
                            columns='parameter',
                            values='value',
                            aggfunc='mean').reset_index()

# Normalizar datetime a UTC para merge
air_pivot['datetime'] = pd.to_datetime(air_pivot['datetime'], errors='coerce').dt.tz_convert('UTC')
print(f"[INFO] Aire cargado. Filas: {air_pivot.shape[0]}, Columnas: {air_pivot.shape[1]}")

# -----------------------------
# Unir clima y contaminación
# -----------------------------
dataset = pd.merge(air_pivot, weather, on='datetime', how='inner')
print(f"[INFO] Dataset unido. Filas: {dataset.shape[0]}, Columnas: {dataset.shape[1]}")

# -----------------------------
# Guardar dataset final
# -----------------------------
os.makedirs("output", exist_ok=True)
dataset.to_csv("output/dataset_final.csv", index=False)
print(f"[INFO] Dataset creado: output/dataset_final.csv")

