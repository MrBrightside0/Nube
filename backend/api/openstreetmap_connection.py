import osmnx as ox
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ----------------------------
# 1️⃣ Descargar la red de carreteras
# ----------------------------
city = "Monterrey, Mexico"
print("[INFO] Descargando la red de carreteras de Monterrey desde OpenStreetMap...")
G = ox.graph_from_place(city, network_type='drive')

print("[INFO] Convirtiendo la red a GeoDataFrame (segmentos de vía)...")
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

print("[INFO] Seleccionando columnas relevantes y rellenando valores faltantes...")
edges = edges[['name', 'highway', 'length', 'lanes']].fillna('desconocido')
print(f"[INFO] Total de segmentos de carretera cargados: {len(edges)}")

# Normalizar highway (si es lista -> tomar el primero)
edges['highway'] = edges['highway'].apply(lambda x: x[0] if isinstance(x, list) else x)

# ----------------------------
# 2️⃣ Definir volúmenes estimados por tipo de vía
# ----------------------------
road_volumes = {
    'motorway': 15000,
    'primary': 5000,
    'secondary': 2000,
    'residential': 200
}
print("[INFO] Se definieron los volúmenes estimados de tráfico por tipo de vía.")

# ----------------------------
# 3️⃣ Definir factores horarios (rush hours)
# ----------------------------
hour_factors = {
    (0, 5): 0.2,
    (6, 8): 1.0,
    (9, 15): 0.5,
    (16, 19): 1.0,
    (20, 23): 0.3
}

def get_hour_factor(hour):
    return next(v for k, v in hour_factors.items() if k[0] <= hour <= k[1])

print("[INFO] Se definieron los factores horarios de tráfico (horas pico).")

# ----------------------------
# 4️⃣ Generar dataset por hora
# ----------------------------
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 1, 2)  # se puede cambiar el rango
hours = pd.date_range(start_date, end_date, freq='h')[:-1]  # corregido: 'h' en vez de 'H'
print(f"[INFO] Generando dataset para {len(hours)} horas...")

data = []

for dt in hours:
    factor = get_hour_factor(dt.hour)
    
    for _, row in edges.iterrows():
        base_volume = road_volumes.get(row['highway'], 500)  # valor por defecto si no está definido
        traffic = base_volume * factor * np.random.normal(1.0, 0.1)  # añadir variabilidad ±10%
        traffic = max(0, int(traffic))
        
        data.append({
            'datetime': dt,
            'road_name': row['name'],
            'road_type': row['highway'],
            'length_m': row['length'],
            'lanes': row['lanes'],
            'estimated_traffic': traffic
        })

print("[INFO] Creando dataframe final...")
df = pd.DataFrame(data)

print("[INFO] Guardando dataset comprimido en 'monterrey_traffic_estimated.csv.gz'...")
df.to_csv('monterrey_traffic_estimated.csv.gz', index=False, compression='gzip')

print("[INFO] Dataset listo y comprimido uwu")


print("[INFO] Dataset listo uwu")
print(df.head())

