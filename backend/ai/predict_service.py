import joblib
import os
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Cargar modelos
try:
    rf_model = joblib.load(os.path.join(MODELS_DIR, "rf_model.pkl"))
    xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgb_model.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
except FileNotFoundError:
    print("⚠️ Modelos no encontrados. Se usarán predicciones simuladas.")
    rf_model = None
    xgb_model = None
    scaler = None

def predict_air_quality(features, model_type="xgb"):
    if not xgb_model or not scaler:
        # 🔹 Si no hay modelo, devolvemos valor simulado
        print("⚠️ Usando predicción simulada (sin modelo cargado).")
        return np.random.randint(50, 150)

    try:
        X = np.array([[features["pm25"], features["no2"], features["temperature"], features["humidity"], features["wind_speed"]]])
        X_scaled = scaler.transform(X)
        if model_type == "xgb":
            pred = xgb_model.predict(X_scaled)[0]
        else:
            pred = rf_model.predict(X_scaled)[0]
        if np.isnan(pred):  # Prevención de NaN
            pred = 0
        return float(pred)
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        return np.random.randint(50, 150)
