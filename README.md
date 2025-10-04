# 🌍 CleanSkies  
**NASA Space Apps Challenge 2025**  
**Full-Stack Air Quality Platform**  

---

## 🎯 Project Overview  

**CleanSkies** is a full-stack platform that delivers **real-time air quality insights** and **short-term forecasts** by integrating:  

- 🛰️ **NASA TEMPO satellite data** (NO₂, HCHO).  
- 📊 **OpenAQ surface stations** (PM2.5, NO₂).  
- 🌤️ **OpenWeather One Call 3.0** (meteorological context).  
- ✅ **EPA AQI health categories** for actionable recommendations.  

The solution empowers **sensitive groups** (asthmatics, children, athletes, seniors) and schools to make **informed daily decisions** about outdoor activities.  

Developed during the **NASA Space Apps Challenge 2025**. 🚀  

---

## 📂 Repository Structure  

📁 CleanSkies  
│  
├── 📁 docs/                  # Documentation & pitch materials  
│   ├── ETL.md                # Data flow (extract, transform, load)  
│   ├── API.md                # Backend API endpoints  
│   └── PITCH.md              # Pitch script & demo guide  
│  
├── 📁 web/                   # Frontend (Next.js, deployed on Vercel)  
│   ├── app/                  # App Router pages  
│   │   ├── map/              # Interactive map  
│   │   ├── dashboard/        # AQI & forecast dashboard  
│   │   ├── trends/           # Historical trends & correlations  
│   │   └── alerts/           # Alerts subscription form  
│   ├── components/           # UI components (cards, toggles, legends)  
│   ├── public/               # Static assets (icons, images)  
│   ├── styles/               # Tailwind / CSS modules  
│   ├── package.json  
│   └── next.config.js  
│  
├── 📁 api/                   # Backend (FastAPI, deployed on Railway/Render)  
│   ├── main.py               # Main FastAPI app  
│   ├── clients/              # External API clients  
│   │   ├── tempo_client.py  
│   │   ├── openaq_client.py  
│   │   └── weather_client.py  
│   ├── routers/              # Organized routes  
│   │   ├── aq.py             # Air quality endpoints  
│   │   └── alerts.py         # Alerts subscription  
│   ├── models/               # Pydantic schemas & validation  
│   ├── core/                 # Config (CORS, settings)  
│   │   └── config.py  
│   ├── requirements.txt      # Python dependencies  
│   ├── Dockerfile            # Containerization  
│   └── .env.example          # Environment variables template  
│  
├── 📁 notebooks/             # Data exploration (Jupyter)  
│   ├── tempo.ipynb           # TEMPO data preprocessing  
│   ├── openaq.ipynb          # OpenAQ station queries  
│   ├── weather.ipynb         # OpenWeather integration  
│   └── tempo_vs_openaq.ipynb # Correlation analysis  
│  
├── 📁 data/                  # Small sample datasets  
│   ├── raw/                  # Raw files (CSV, NetCDF)  
│   └── processed/            # Harmonized (Parquet, CSV)  
│  
├── 📁 tests/                 # QA & unit tests  
│   ├── test_api.py  
│   ├── test_clients.py  
│   └── test_frontend.md  
│  
├── README.md                 # Project overview (this file)  
├── .gitignore                # Ignore rules  
└── LICENSE                   # MIT license  

---

## ⚡ Technology Stack  

- **Frontend:** Next.js · Recharts · Mapbox GL JS / React Leaflet  
- **Backend:** FastAPI · Railway / Render · Docker  
- **Data Sources:**  
  - 🛰️ NASA TEMPO (via **earthaccess** + **Harmony**)  
  - 📊 OpenAQ (PM2.5 / NO₂)  
  - 🌤️ OpenWeather One Call 3.0  
  - 🇺🇸 AirNow (optional, EPA AQI)  
- **Machine Learning:** Prophet baseline (PM2.5 forecast) · ARIMA fallback  

---

## 📡 Cómo consume datos el frontend

El frontend de Next.js espera que el backend exponga un API REST cuya URL base se define en la variable de entorno `NEXT_PUBLIC_API_URL`. A continuación se describen los contratos que usa cada pantalla interactiva:

### `/aq/latest`

- **Uso:** tarjetas principales del dashboard (`/dashboard`) y barra lateral del mapa (`/map`).
- **Método:** `GET`
- **Query params obligatorios:** `lat`, `lon`. El dashboard también envía `pollutant` (`pm10` | `pm25` | `no2`).
- **Respuesta esperada:**

```json
{
  "aqi": 87,
  "pm25": 22.3,
  "pm10": 41.0,
  "no2": 19.4,
  "wind": 8.7,
  "sources": ["OpenAQ", "TEMPO"]
}
```

Los campos `aqi`, `pm25`, `no2` y `wind` se muestran directamente; `sources` se usa en el popup del mapa.

### `/aq/trends`

- **Uso:** gráficas históricas en `/map` y `/trends`.
- **Método:** `GET`
- **Query params:** `lat`, `lon`, `days` (por defecto 7).
- **Respuesta esperada:**

```json
{
  "series": [
    {"ts": "2024-08-01T00:00:00Z", "pm25": 18.2, "no2": 24.1},
    {"ts": "2024-08-01T01:00:00Z", "pm25": 17.6, "no2": 22.0}
  ],
  "correlation": 0.68
}
```

`series` alimenta las gráficas de líneas y dispersión; `correlation` se muestra como coeficiente NO₂ ↔ PM2.5.

### `/ai/predict`

- **Uso:** gráfica de predicción IA en `/dashboard`.
- **Método:** `GET`
- **Query params:** `lat`, `lon`, `pollutant`, `days` (30 por defecto).
- **Respuesta esperada:**

```json
{
  "predictions": [
    {"ds": "2024-08-01", "yhat": 21.4},
    {"ds": "2024-08-02", "yhat": 22.0}
  ]
}
```

`ds` (o `ts`) y `yhat` se trazan como serie temporal.

### `/ai/seasonal`

- **Uso:** bloque de "Tendencia y Estacionalidad" en `/dashboard`.
- **Método:** `GET`
- **Query params:** `lat`, `lon`, `pollutant`.
- **Respuesta esperada:**

```json
{
  "trend": [
    {"ts": "2024-07-01", "value": 19.2},
    {"ts": "2024-07-02", "value": 18.7}
  ]
}
```

Si `trend` está vacío o no existe, el frontend muestra un mensaje "No hay tendencia disponible".

### `/alerts/subscribe`

- **Uso:** formulario de alertas (`/alerts`).
- **Método:** `POST`
- **Body esperado:**

```json
{
  "contact": "usuario@example.com",
  "preferences": {
    "type": "email",
    "city": "Monterrey",
    "lat": 25.67,
    "lon": -100.31
  }
}
```

El backend debe responder con un `200 OK`; cualquier error se muestra como "Ocurrió un error al suscribirte".

> Nota: todos los valores numéricos se renderizan tal cual; si el backend devuelve `null` o el campo falta, el frontend mostrará `N/A` o `–` según el contexto.

---

📌 License

MIT License © 2025 CleanSkies Team
