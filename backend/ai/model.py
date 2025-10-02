import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# -----------------------------
# 1️⃣ Cargar dataset final
# -----------------------------
dataset_path = "dataset_final_2024.csv"
print(f"[INFO] Cargando dataset: {dataset_path}")
df = pd.read_csv(dataset_path)
print(f"[INFO] Dataset cargado: {df.shape}")

# -----------------------------
# 2️⃣ Filtrar filas con datos de aire (pm25)
# -----------------------------
print("[INFO] Filtrando filas con PM2.5")
df_air = df[df['parameter'] == 'pm25'].copy()
df_air = df_air.dropna(subset=['value'])
print(f"[INFO] Filas de aire (pm25) disponibles: {df_air.shape[0]}")

# -----------------------------
# 3️⃣ Preparar features y target
# -----------------------------
target = 'value'
features = [
    'speedLimit', 'distance', 'segmentProbeCounts_num', 'emissionProxy', 'isHighway',
    'temp', 'rhum', 'wspd', 'pres', 'cldc', 'coco',
    'hour', 'day', 'month'
]

print("[INFO] Preparando features")
df_air['isHighway'] = df_air['isHighway'].astype(int)
for col in features:
    if col in df_air.columns:
        df_air[col] = pd.to_numeric(df_air[col], errors='coerce')
        df_air[col] = df_air[col].fillna(df_air[col].median())

X = df_air[features]
y = df_air[target]

# -----------------------------
# 4️⃣ Dividir en entrenamiento y prueba
# -----------------------------
print("[INFO] Dividiendo datos en entrenamiento y prueba")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"[INFO] Datos de entrenamiento: {X_train.shape}, Datos de prueba: {X_test.shape}")

# -----------------------------
# 5️⃣ Entrenar modelo baseline
# -----------------------------
print("[INFO] Entrenando RandomForestRegressor")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# -----------------------------
# 6️⃣ Predecir y evaluar
# -----------------------------
print("[INFO] Realizando predicciones")
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)

print("[INFO] Evaluación del modelo:")
print(f"[INFO] MAE: {mae:.4f}")
print(f"[INFO] RMSE: {rmse:.4f}")

# -----------------------------
# 7️⃣ Guardar predicciones (opcional)
# -----------------------------
output_pred = "../ai/predicciones_baseline.csv"
df_results = X_test.copy()
df_results['y_true'] = y_test
df_results['y_pred'] = y_pred
df_results.to_csv(output_pred, index=False)
print(f"[INFO] Predicciones guardadas en: {output_pred}")

