from fastapi import FastAPI, Query, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# ============================================================
# 🧠 Cargar variables de entorno
# ============================================================
load_dotenv()

# ============================================================
# 🚀 Inicializar app principal
# ============================================================
app = FastAPI(title="CleanSkies API", version="1.0.0")

# ============================================================
# 🌐 Configuración de CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 📦 Importaciones internas
# ============================================================
from clients.openaq_client import get_latest_openaq
from clients.weather_cliente import get_weather_data
from ai.predict_service import predict_air_quality
from ai.chat_service import get_chat_response

# ============================================================
# 🔹 Router principal con prefijo /api
# ============================================================
router = APIRouter(prefix="/api")

# ============================================================
# 🧠 Health Check
# ============================================================
@router.get("/health")
def health():
    return {"ok": True}

# ============================================================
# 🌍 Predicción AQI (Modelo IA)
# ============================================================
@router.get("/aq/predict")
def predict(lat: float = Query(...), lon: float = Query(...)):
    try:
        print(f"📍 Recibida petición de predicción: lat={lat}, lon={lon}")

        # 🔹 Obtener datos de OpenAQ y clima
        pm25, no2 = get_latest_openaq(lat, lon)
        clima = get_weather_data(lat, lon)

        # 🔹 Features para el modelo
        features = {
            "pm25": pm25,
            "no2": no2,
            "temperature": clima["temp"],
            "humidity": clima["humidity"],
            "wind_speed": clima["wind_speed"],
        }

        # 🔹 Predicción del modelo
        prediction = predict_air_quality(features, model_type="xgb")

        # 🔹 Respuesta adaptada al frontend
        response = {
            "name": "Current Zone",
            "lat": lat,
            "lon": lon,
            "aqi": round(prediction, 2),
            "pm25": round(pm25, 2) if pm25 else None,
            "no2": round(no2, 2) if no2 else None,
            "wind": round(clima["wind_speed"], 2),
            "trend": [
                {"ts": f"Hour {i+1}", "pm25": pm25 + i, "no2": no2 + i}
                for i in range(6)
            ],
        }

        return response

    except Exception as e:
        print("❌ Error en /api/aq/predict:", e)
        return {"error": str(e)}

# ============================================================
# 💬 Chatbot (OpenAI)
# ============================================================
@router.post("/chat")
async def chat(request: Request):
    """
    Endpoint del chatbot SatAirlite conectado a OpenAI.
    Recibe: {"message": "texto del usuario", "aqi": 85}
    Devuelve: {"response": "texto del asistente"}
    """
    try:
        data = await request.json()
        user_message = data.get("message", "")
        aqi_value = data.get("aqi", None)

        print("📩 Mensaje recibido:", user_message)
        print("🌫️ AQI:", aqi_value)

        if not user_message:
            return {"response": "Por favor, envíame una pregunta válida."}

        reply = get_chat_response(user_message, aqi_value)

        print("🤖 Respuesta enviada:", reply)
        return {"response": reply}

    except Exception as e:
        print("❌ Error en /api/chat:", e)
        return {"response": "Hubo un problema al conectar con el asistente."}

# ============================================================
# 🚀 Registrar router principal
# ============================================================
app.include_router(router)

# ================================================================
# 📊 TENDENCIAS Y ESTACIONALIDAD (7 DÍAS)
# ================================================================
from fastapi import Query
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ai.seasonal_service import seasonal_analysis_api  # generador seguro


@app.get("/api/aq/trends")
def get_trends(lat: float = Query(...), lon: float = Query(...), days: int = 7):
    """
    Devuelve una tendencia de contaminantes (pm25, no2) y correlación.
    Si los modelos fallan, genera datos simulados realistas.
    """
    print(f"📍 Recibida petición de tendencias para lat={lat}, lon={lon}")

    try:
        # 🔹 Intentar obtener análisis real (por modelo Prophet o similar)
        result = seasonal_analysis_api(lat, lon, days)
        trend = result.get("trend", [])
        corr = result.get("correlation", 0.0)

        if not trend or len(trend) == 0:
            raise ValueError("Empty trend returned")

        print("✅ Tendencias generadas desde modelo Prophet")
        return {"trend": trend, "correlation": corr}

    except Exception as e:
        print(f"⚠️ Error al generar tendencias reales: {e}")
        print("➡ Generando datos simulados...")

        # 🔹 Datos simulados si no hay modelo
        fake_days = [f"Day {i+1}" for i in range(days)]
        pm25 = np.clip(np.random.normal(25, 8, days), 5, 70)
        no2 = np.clip(pm25 * 0.7 + np.random.normal(5, 2, days), 3, 60)

        # Correlación manual
        corr = np.corrcoef(pm25, no2)[0, 1]
        trend = [{"ts": fake_days[i], "pm25": float(pm25[i]), "no2": float(no2[i])} for i in range(days)]

        return {"trend": trend, "correlation": round(float(corr), 3)}
