from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)

# ---------------------------
# Health Check
# ---------------------------
@api_bp.route("/health", methods=["GET"])
def health():
    OK_RESULT = {"ok": True}
    return jsonify(OK_RESULT)


# ---------------------------
# Última medición (PM2.5, NO2, clima)
# ---------------------------
@api_bp.route("/aq/latest", methods=["GET"])
def get_latest():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    # TODO: llamar a tempo_client, openaq_client, weather_client
    data = {
        "lat": lat,
        "lon": lon,
        "aqi": None,       # calculado
        "pm25": None,      # de OpenAQ
        "no2": None,       # de TEMPO
        "weather": {},     # de OpenWeather
        "sources": []
    }
    return jsonify(data)


# ---------------------------
# Tendencias (últimos N días + correlación NO2 <-> PM2.5)
# ---------------------------
@api_bp.route("/aq/trends", methods=["GET"])
def get_trends():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    days = request.args.get("days", default=7, type=int)

    # TODO: query histórico en OpenAQ + TEMPO y calcular correlación
    data = {
        "lat": lat,
        "lon": lon,
        "days": days,
        "series": [],       # lista con timestamps y valores
        "correlation": None
    }
    return jsonify(data)


# ---------------------------
# Pronóstico (PM2.5 o AQI 24h con Prophet/ARIMA)
# ---------------------------
@api_bp.route("/aq/forecast", methods=["GET"])
def get_forecast():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    hours = request.args.get("h", default=24, type=int)

    # TODO: ejecutar modelo Prophet/ARIMA
    forecast = {
        "lat": lat,
        "lon": lon,
        "hours": hours,
        "predictions": [],   # lista con ts, yhat, pi_low, pi_high
        "model": "Prophet"
    }
    return jsonify(forecast)


# ---------------------------
# Fuentes / provenance (IDs de granules, estaciones, clima)
# ---------------------------
@api_bp.route("/aq/sources", methods=["GET"])
def get_sources():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    # TODO: devolver metadatos de origen de cada dataset
    data = {
        "lat": lat,
        "lon": lon,
        "tempo_granules": [],
        "stations": [],
        "weather_provider": "OpenWeather"
    }
    return jsonify(data)


# ---------------------------
# Suscripción a alertas
# ---------------------------
@api_bp.route("/alerts/subscribe", methods=["POST"])
def subscribe_alerts():
    payload = request.json  # { "contact": "email/phone", "preferences": {...} }

    # TODO: guardar en base de datos o archivo
    result = {
        "success": True,
        "contact": payload.get("contact"),
        "preferences": payload.get("preferences", {})
    }
    return jsonify(result)

# ---------------------------
# Tareas pendientes
# ---------------------------

# 1️⃣ Crear y mantener el backend
# - Inicializar FastAPI con CORS abierto para frontend
# - Configurar deploy en Railway o Render con Docker
# - Mantener variables de entorno seguras (EARTHDATA_USER/PASS, OWM_API_KEY)
# - Documentación automática con /docs

# 2️⃣ Endpoints principales
# - /health              -> estado del servidor
# - /aq/latest           -> último AQI + PM2.5 + NO₂ + clima + fuentes
# - /aq/trends           -> series históricas y correlación NO₂↔PM2.5
# - /aq/forecast         -> pronóstico 24h PM2.5 o AQI con Prophet/ARIMA
# - /aq/sources          -> metadata/provenance TEMPO, estaciones y clima
# - /alerts/subscribe    -> almacenar contactos para alertas (email/WhatsApp)

# 3️⃣ Integración con clientes de datos
# - tempo_client.py      -> autenticación EDL, búsqueda, subsetting con Harmony
# - openaq_client.py     -> consultas REST por bbox y parámetros
# - weather_client.py    -> One Call 3.0 de OpenWeather para features climáticas

# 4️⃣ Cache y optimización
# - Cachear respuestas por (lat, lon, var) 30–60 min
# - Opcional: Redis para cache más rápido

# 5️⃣ Soporte al equipo
# - Coordinar integración con frontend Next.js
# - Asegurar que endpoints entreguen el formato estándar:
#   source | var | lat | lon | ts_utc | value | unit | quality_flag
# - Facilitar datos limpios para ML baseline (Prophet/ARIMA)

