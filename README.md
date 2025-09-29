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

📌 License

MIT License © 2025 CleanSkies Team
