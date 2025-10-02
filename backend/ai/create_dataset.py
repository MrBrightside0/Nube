import pandas as pd
from pathlib import Path

# -----------------------------
# 1️⃣ Cargar datos de tráfico
# -----------------------------
traffic_file = "/home/mario/Downloads/segmentResults_for_model.csv"
df_traffic = pd.read_csv(traffic_file)
print(f"[INFO] Tráfico cargado: {df_traffic.shape}")

# -----------------------------
# 2️⃣ Cargar datos de clima (2024)
# -----------------------------
weather_folder = "../ai/weather_data"
df_weather_list = []

for path in Path(weather_folder).rglob("*.csv.gz"):
    df_tmp = pd.read_csv(path, compression='gzip')
    
    # Crear datetime
    df_tmp['datetime'] = pd.to_datetime(df_tmp[['year','month','day','hour']], errors='coerce', utc=True)
    df_tmp = df_tmp.dropna(subset=['datetime'])
    
    # Filtrar 2024
    df_tmp = df_tmp[df_tmp['datetime'].dt.year == 2024]
    
    # Convertir lat/lon a float si existen
    for col in ['lat', 'lon']:
        if col in df_tmp.columns:
            df_tmp[col] = pd.to_numeric(df_tmp[col], errors='coerce')
    
    df_weather_list.append(df_tmp)

df_weather = pd.concat(df_weather_list, ignore_index=True)
print(f"[INFO] Clima cargado: {df_weather.shape}")

# -----------------------------
# 3️⃣ Cargar datos de calidad del aire (2024)
# -----------------------------
air_folder = "../ai/air_data"
df_air_list = []

for path in Path(air_folder).rglob("*"):
    if path.suffix in [".csv", ".gz"]:
        df_tmp = pd.read_csv(path, compression='gzip' if path.suffix == ".gz" else None)
        
        if 'datetime' in df_tmp.columns:
            df_tmp['datetime'] = pd.to_datetime(df_tmp['datetime'], utc=True, errors='coerce')
            df_tmp = df_tmp.dropna(subset=['datetime'])
            df_tmp = df_tmp[df_tmp['datetime'].dt.year == 2024]
            
            # Convertir lat/lon a float si existen
            for col in ['lat', 'lon']:
                if col in df_tmp.columns:
                    df_tmp[col] = pd.to_numeric(df_tmp[col], errors='coerce')
            
            df_air_list.append(df_tmp)

df_air = pd.concat(df_air_list, ignore_index=True)
print(f"[INFO] Aire cargado: {df_air.shape}")

# -----------------------------
# 4️⃣ Preparar columnas de join
# -----------------------------
# Redondear lat/lon para merge aproximado
for df in [df_air, df_weather]:
    for col in ['lat', 'lon']:
        if col in df.columns:
            df[f"{col}_r"] = df[col].round(3)

# En tráfico, redondear lat_start/lon_start si existen
for col in ['lat_start', 'lon_start']:
    if col in df_traffic.columns:
        df_traffic[f"{col}_r"] = pd.to_numeric(df_traffic[col], errors='coerce').round(3)

# -----------------------------
# 5️⃣ Asegurar mismo tipo datetime (ns, UTC)
# -----------------------------
df_traffic['datetime'] = pd.to_datetime(df_traffic.get('datetime', pd.Timestamp('2024-01-01')), utc=True)
df_traffic['datetime'] = df_traffic['datetime'].astype('datetime64[ns, UTC]')
df_weather['datetime'] = df_weather['datetime'].astype('datetime64[ns, UTC]')
df_air['datetime'] = df_air['datetime'].astype('datetime64[ns, UTC]')

# -----------------------------
# 6️⃣ Merge tráfico con clima
# -----------------------------
df_traffic_weather = pd.merge_asof(
    df_traffic.sort_values('datetime'),
    df_weather.sort_values('datetime'),
    on='datetime',
    direction='nearest',
    tolerance=pd.Timedelta('1h')  # Ajusta según necesidad
)
print(f"[INFO] Merge tráfico-clima: {df_traffic_weather.shape}")

# -----------------------------
# 7️⃣ Merge con aire
# -----------------------------
df_final = pd.merge_asof(
    df_traffic_weather.sort_values('datetime'),
    df_air.sort_values('datetime'),
    on='datetime',
    direction='nearest',
    tolerance=pd.Timedelta('1h'),
    suffixes=('', '_air')
)
print(f"[INFO] Merge final con aire: {df_final.shape}")

# -----------------------------
# 8️⃣ Guardar dataset final
# -----------------------------
output_csv = "../ai/dataset_final_2024.csv"
df_final.to_csv(output_csv, index=False)
print(f"[INFO] Dataset final listo en: {output_csv}")

