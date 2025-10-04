# Nube Backend

Backend en Flask para la plataforma Nube, encargado de exponer servicios REST relacionados con calidad del aire, clima y analítica derivada de datos abiertos. El proyecto incluye utilidades para descargar datasets de OpenAQ, Meteostat/OpenWeather y OpenStreetMap, así como notebooks y scripts de modelado predictivo.

## Tecnologías principales
- Python 3.13
- Flask + Flask-CORS
- Requests y utilidades propias para integrar APIs externas
- Prophet, CatBoost y TensorFlow para modelos de series de tiempo y regresión
- Docker para empaquetado y despliegue

## Estructura del repositorio
```
backend/
├── Nube.py                 # Punto de entrada Flask
├── api/                    # Blueprint principal y conectores externos
│   ├── routes.py           # Endpoints Flask + integración con modelos/conectores
│   ├── constants.py        # IDs de sensores + carga de claves (.env)
│   ├── requests_service.py # Cliente HTTP genérico (X-API-Key, manejo de errores)
│   ├── openaq_connection.py        # Wrapper OpenAQ v3 + descarga histórica S3
│   ├── weather_api_connection.py  # Cliente One Call 3.0 con fallback weather
│   ├── earth_access_connection.py # CMR/Earthdata (colecciones, granulos)
│   └── openstreetmap_connection.py# Generador de tráfico sintético vía OSMnx
├── ai/                     # Scripts y datos para modelos predictivos
│   ├── model.py            # Pipeline de entrenamiento NN + CatBoost
│   └── predict_data.py     # Pronósticos con Prophet y análisis estacional
├── cache/                  # Ejemplos de resultados cacheados (JSON)
├── Dockerfile
└── requirements.txt
```
> Nota: las carpetas `ai/air_data`, `ai/weather_data` y `ai/traffic_data` contienen datasets comprimidos (.csv.gz) que alimentan los experimentos de ML.

## Requisitos previos
- Python 3.13 (o 3.11+ si se ajustan dependencias de TensorFlow)
- pip y virtualenv
- Opcional: Docker 24+

## Variables de entorno
Defínelas en un archivo `.env` en la raíz o exporta en tu shell antes de ejecutar la app.
- `OPEN_AQ_KEY`: clave de API de OpenAQ (requerida para llamadas autenticadas).
- `TEMPO_KEY`: token para la API TEMPO (reservado para integración futura).
- `EARTH_ACCESS_KEY`: credencial para fuentes de EarthData (verifica `constants.py`, actualmente usa `os.get` y deberá corregirse a `os.getenv`).
- `PORT`: puerto de escucha; por defecto `5000`.

Ejemplo de `.env`:
```
OPEN_AQ_KEY=tu_token
TEMPO_KEY=otro_token
EARTH_ACCESS_KEY=credencial
PORT=5000
```

## Instalación y ejecución local
1. Crear entorno virtual
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```
3. Levantar el servidor Flask
   ```bash
   python Nube.py
   ```
4. Abre `http://localhost:5000/api/health` para verificar el estado.

## Ejecución con Docker
1. Construir la imagen
   ```bash
   docker build -t nube-backend .
   ```
2. Ejecutar el contenedor (mapeando el puerto que necesites)
   ```bash
   docker run --env-file .env -p 5000:5000 nube-backend
   ```

## Endpoints principales (`api/routes.py`)
| Método | Ruta                    | Descripción |
|--------|------------------------|-------------|
| GET    | `/api/health`          | Health check simple. |
| GET    | `/api/aq/latest`       | Integra OpenAQ + OpenWeather (fallback) para entregar últimas mediciones, AQI y metadatos. Permite `location_id` o `lat/lon`. |
| GET    | `/api/aq/predictions`  | Expone los modelos (gases NN + CatBoost PM10/PM2.5) usando `ai/output/dataset_final.csv`. Permite filtrar por `location_id`. |
| GET    | `/api/aq/trends`       | Series históricas y correlación PM2.5↔NO2 a partir del dataset consolidado. |
| GET    | `/api/aq/forecast`     | Pronóstico baseline (media 24h) para el contaminante solicitado. |
| GET    | `/api/aq/sources`      | Lista estaciones de aire, clima y dataset de tráfico sintético usado. |
| POST   | `/api/alerts/subscribe`| Persiste suscripciones en `api/cache/alerts.json`. |

> Todos los endpoints requieren que los modelos y artefactos estén generados en `ai/models/` y que las claves de entorno (`OPENAQ_KEY`, `OPENWEATHER_KEY`, `EARTH_ACCESS_KEY`) estén disponibles.

## Scripts y utilidades destacadas
- `api/openaq_connection.py`: wrapper de OpenAQ v3 (`/locations`, `/locations/{id}/latest`, `/measurements`) y descarga histórica desde S3.
- `api/weather_api_connection.py`: cliente One Call 3.0 con manejo de `401` (fallback a `data/2.5/weather`).
- `api/earth_access_connection.py`: integración con Earthdata CMR (colecciones, granulos, descarga). Incluye CLI (`python api/earth_access_connection.py granules ...`).
- `api/openstreetmap_connection.py`: generador de tráfico sintético parametrizable mediante OSMnx.
- `ai/create_dataset.py`: ETL que fusiona aire, clima y features temporales → `ai/output/dataset_final.csv`.
- `ai/model.py`: entrena la red neuronal multisalida para gases (`co`, `no`, `no2`, `nox`, `o3`, `so2`) y dos CatBoost para partículas (`pm10`, `pm25`).
  - Usa `dataset_final.csv`, interpola huecos cortos por estación (`interpolate_pollutants`), añade atributos trigonométricos (sin/cos de hora/mes) y limpia valores extremos.
  - Split temporal (80/20) para evaluar; reporta métricas en consola (`MSE`, `RMSE`, `R^2`) y guarda metadatos (columnas, rellenos) junto con los artefactos en `ai/models/`.
- `ai/inference.py`: expone utilidades de inferencia (`predict_gases`, `predict_particle`), el resumen/forecast metropolitano y permite pruebas rápidas (`--rows`).
- `api/requests_service.py`: cliente HTTP centralizado con cabeceras y manejo de errores.

### Datos usados por los modelos (`ai/`)
- `ai/create_dataset.py` fusiona todas las fuentes necesarias para entrenar los modelos:
  - **Calidad del aire**: agrega todas las estaciones presentes en `ai/air_data/` (Universidad, Tecnológico, Centro de Monterrey, San Nicolás, Escobedo, Apodaca). Cada CSV se pivota por `parameter`, se normalizan columnas (`location_id`, `value`) y se ordena por estación.
  - **Clima**: combina todas las estaciones Meteostat en `ai/weather_data/`, calcula medias horarias (`temp_mean`, `rhum_mean`, `wspd_mean`) y preserva las columnas individuales (`temp_76393`, `temp_MMMY0`, etc.).
  - **Ingeniería de atributos**: interpola huecos cortos (hasta 6 muestras), genera rolling averages y diferencias (6/24 h) para cada contaminante, además de variables de calendario (hora, día de la semana, mes, `sin/cos`).
- El dataset unificado se guarda en `ai/output/dataset_final.csv` y contiene todas las estaciones de la ZMM con `location_id`, `lat`, `lon` y las features generadas.
- `ai/model.py` consume ese dataset consolidado: el modelo de gases usa todas las variables meteorológicas y las series de contaminantes, mientras que los modelos CatBoost de partículas se entrenan por objetivo pero siguen viendo los datos de todas las estaciones (sólo descartan filas que no tengan el contaminante específico).
- `ai/models/` almacena los artefactos (`gas_model.keras`, `catboost_pm10.cbm`, `catboost_pm25.cbm`) junto con metadatos de columnas e imputaciones para reproducir inferencia en API (`/api/aq/predictions`).

## Flujo de trabajo recomendado
1. **Actualizar datos**: descarga/actualiza `ai/air_data`, `ai/weather_data`, `ai/traffic_data` con los scripts de `api/`.
2. **Regenerar dataset**: `python ai/create_dataset.py` para producir `ai/output/dataset_final.csv`.
3. **Entrenar modelos**: `python ai/model.py` (usa TensorFlow + CatBoost) y genera artefactos en `ai/models/`.
4. **Validar inferencia**: `python ai/inference.py --rows 5` o probar `/api/aq/predictions` ya con Flask en marcha.
5. **Desplegar**: iniciar Flask (`python Nube.py`) o empaquetar con Docker.

## Próximos pasos sugeridos
- Conectar futuras fuentes (p. ej., TEMPO) reutilizando la arquitectura de clientes.
- Reemplazar prints por logging estructurado y añadir manejo global de errores HTTP.
- Persistir suscripciones/alertas en almacenamiento externo (DB, servicio de notificaciones).
- Automatizar pruebas (PyTest) para los endpoints y los pipelines de inferencia.

## Referencia detallada de la API
Base URL general: `https://<tu-dominio>/api`. Todos los ejemplos asumen HTTPS en producción; sustituye `<tu-dominio>` por el host donde despliegues el backend.

### GET `/health`
- Verifica que el servicio Flask está levantado.
- Respuesta 200 siempre que la app esté viva.
```bash
curl -s https://<tu-dominio>/api/health
```
```json
{"ok": true}
```

### GET `/aq/latest`
- Parámetros opcionales: `location_id` (string) o `lat`/`lon` (float). Si no se envía un identificador válido el API responde `404`.
- Realiza llamadas a OpenAQ (calidad del aire) y OpenWeather (clima) usando las llaves configuradas en el backend; el frontend solo necesita consumir la respuesta.
```bash
curl "https://<tu-dominio>/api/aq/latest?location_id=7919"
```
```json
{
  "location": {
    "id": "7919",
    "name": "Apodaca-7919",
    "lat": 25.7772,
    "lon": -100.1883
  },
  "measurements": {
    "pm25": {
      "value": 22.6,
      "unit": "ug/m3",
      "last_updated": "2024-12-24T10:00:00Z",
      "quality": "good",
      "sensor_id": 182737
    },
    "no2": {
      "value": 0.018,
      "unit": "ppm",
      "last_updated": "2024-12-24T10:00:00Z",
      "quality": "moderate",
      "sensor_id": 182740
    }
  },
  "aqi": 71.2,
  "weather": {
    "temperature": 16.0,
    "humidity": 94,
    "pressure": 1020,
    "wind_speed": 12.7,
    "description": "very cloudy"
  },
  "sources": {
    "openaq": {
      "id": 7919,
      "name": "Apodaca",
      "city": "Monterrey",
      "coordinates": {"latitude": 25.7772, "longitude": -100.1883},
      "datetime_first": "2018-06-30T00:00:00Z",
      "datetime_last": "2024-12-24T10:00:00Z"
    }
  }
}
```

### GET `/aq/predictions`
- Parámetros opcionales: `location_id`, `rows` (por defecto 1, máximo práctico recomendado 24) y `include_particles` (`true`/`false`).
- Devuelve las filas del dataset usadas como entrada (`inputs`), el resultado del modelo de gases (`gases`) y, si se solicita, los vectores de partículas (`particles`).
```bash
curl "https://<tu-dominio>/api/aq/predictions?location_id=7919&rows=2"
```
```json
{
  "rows": 2,
  "inputs": [
    {
      "datetime": "2024-12-24 10:00:00+00:00",
      "location_id": 7919,
      "location_name": "Apodaca-7919",
      "pm10": 31.0,
      "co": 0.41,
      "no2": 0.0186,
      "rhum_mean": 90.33,
      "temp_mean": 16.63,
      "...": "más de 60 columnas de contexto"
    }
  ],
  "gases": [
    {"co": 0.8643, "no": 0.0327, "no2": 0.0193, "nox": 0.0520, "o3": 0.0131, "so2": 0.0033}
  ],
  "particles": {
    "pm10": [61.85, 71.69],
    "pm25": [18.31, 22.10]
  }
}
```
- Manejo recomendado en el frontend cuando el payload es grande:
  1. Solicita solo las filas que necesites (`rows=1` para dashboards, `rows=24` para gráficos horarios).
  2. Si solo muestras gases, agrega `include_particles=false` para reducir ~40% del tamaño.
  3. Consume únicamente los campos relevantes de `inputs`. Puedes mapear las claves a etiquetas más legibles y omitir el resto.
  4. Persistir en el cliente solo los vectores que renderizarás; para tablas largas usa paginación o agrega un botón "ver detalles".
  5. Si requieres un histórico mayor, realiza varias peticiones paginadas (`rows=24` + `location_id`) y almacena en IndexedDB/local storage para evitar re-descargas.

Ejemplo en JavaScript para quedarte con lo esencial:
```js
const params = new URLSearchParams({ location_id: '7919', rows: '1' });
fetch(`https://<tu-dominio>/api/aq/predictions?${params}`)
  .then((resp) => resp.json())
  .then(({ gases = [], particles }) => {
    const latest = gases[0] ?? {};
    const pm10 = particles?.pm10?.[0] ?? null;
    renderPrediction({ co: latest.co, no2: latest.no2, pm10 });
  })
  .catch(console.error);
```

### GET `/aq/trends`
- Requiere `location_id`. Parámetro opcional `days` (1-30 recomendado) para limitar el histórico.
```bash
curl "https://<tu-dominio>/api/aq/trends?location_id=7919&days=7"
```
```json
{
  "location_id": "7919",
  "days": 7,
  "series": {
    "pm25": [],
    "no2": [
      {"datetime": "2024-12-22T12:00:00Z", "no2": 0.0157},
      {"datetime": "2024-12-22T13:00:00Z", "no2": 0.0177}
    ]
  },
  "correlation_pm25_no2": null
}
```

### GET `/aq/forecast`
- Requiere `location_id`. Parámetros opcionales: `pollutant` (default `pm25`) y `h` (1-168 horas).
```bash
curl "https://<tu-dominio>/api/aq/forecast?location_id=7919&pollutant=pm10&h=4"
```
```json
{
  "location_id": "7919",
  "pollutant": "pm10",
  "hours": 4,
  "model": "naive_mean",
  "predictions": [
    {"timestamp": "2024-12-24T12:00:00+00:00", "yhat": 64.125, "pi_low": 23.89, "pi_high": 104.36},
    {"timestamp": "2024-12-24T13:00:00+00:00", "yhat": 64.125, "pi_low": 23.89, "pi_high": 104.36}
  ]
}
```

### GET `/aq/sources`
- Devuelve todas las estaciones de aire disponibles y las estaciones meteorológicas que alimentan el modelo.
```bash
curl -s https://<tu-dominio>/api/aq/sources
```
```json
{
  "air_quality": [
    {"location_id": "427", "location_name": "Juárez-427", "lat": 25.6461, "lon": -100.0956, "openaq_id": "427"},
    {"location_id": "7919", "location_name": "Apodaca-7919", "lat": 25.7772, "lon": -100.1883, "openaq_id": "7919"}
  ],
  "weather": [
    {"station_id": "76393", "name": "Monterrey", "lat": 25.8667, "lon": -100.2000},
    {"station_id": "76394", "name": "Monterrey Airport", "lat": 25.8667, "lon": -100.2333}
  ]
}
```

### POST `/alerts/subscribe`
- Recibe un JSON con `contact` (email/teléfono) y un objeto opcional `preferences`. Persiste la suscripción en `api/cache/alerts.json`.
```bash
curl -X POST https://<tu-dominio>/api/alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{"contact":"ana@example.com","preferences":{"threshold_pm25":35}}'
```
```json
{
  "success": true,
  "stored": {
    "contact": "ana@example.com",
    "preferences": {"threshold_pm25": 35},
    "created_at": "2024-12-24T11:15:30Z"
  }
}
```
- Considera agregar validación en el frontend (formato de email, longitud de teléfono) antes de enviar la solicitud.

### POST `/aq/recommendation`
- Requiere un JSON con al menos `location_id`. Opcionalmente acepta `rows` para seleccionar cuántas filas previas revisar (se usa la más reciente).
- Usa los modelos locales para obtener la predicción más reciente y construye una recomendación con OpenAI (`OPENAI_API_KEY` debe estar definido y la librería `openai` instalada).
```bash
curl -X POST https://<tu-dominio>/api/aq/recommendation \
  -H "Content-Type: application/json" \
  -d '{"location_id":"7919"}'
```
```json
{
  "location_id": "7919",
  "location_name": "Apodaca-7919",
  "datetime": "2024-12-24 11:00:00+00:00",
  "gases": {"co": 0.80, "no2": 0.018, "o3": 0.012},
  "particles": {"pm10": 71.69, "pm25": 22.10},
  "recommendation": "1) Riesgo moderado: las partículas finas superan los 20 ug/m3..."
}
```
- Maneja los códigos `500`/`503` para notificar al usuario si la clave de OpenAI falta o si la llamada fue rechazada.

### GET `/aq/metropolitan-summary`
- Parámetro opcional `rows` para indicar cuántas observaciones recientes incluir por estación (default `1`, máximo sugerido `24`).
- Agrega todas las ubicaciones de la ZMM, ejecuta los modelos de gases/partículas y devuelve un payload listo para dashboards metropolitanos.
```bash
curl "https://<tu-dominio>/api/aq/metropolitan-summary?rows=2"
```
```json
{
  "generated_at": "2024-12-24T12:05:10Z",
  "rows_per_location": 2,
  "locations_count": 6,
  "locations": [
    {
      "location_id": "7919",
      "location_name": "Apodaca-7919",
      "lat": 25.7772,
      "lon": -100.1883,
      "observations": [
        {
          "datetime": "2024-12-24T10:00:00+00:00",
          "gases": {"co": 0.8644, "no2": 0.0193, "o3": 0.0131},
          "particles": {"pm10": 61.85, "pm25": 18.31}
        },
        {
          "datetime": "2024-12-24T11:00:00+00:00",
          "gases": {"co": 0.8036, "no2": 0.0175, "o3": 0.0122},
          "particles": {"pm10": 71.69, "pm25": 22.10}
        }
      ]
    }
  ],
  "summary": {
    "gases": {"co": {"min": 0.80, "max": 0.97, "avg": 0.86}},
    "particles": {"pm10": {"min": 42.15, "max": 109.13, "avg": 68.44}}
  },
  "highlights": {
    "highest_pm10": {
      "location_id": "7951",
      "location_name": "Universidad-7951",
      "value": 109.13,
      "datetime": "2024-12-24T11:00:00+00:00"
    }
  },
  "errors": {
    "pm25": "CatBoost artifacts for pm25 not found."
  }
}
```
- Si faltan artefactos (`ai/models/*.cbm` o `gas_model.keras`) el endpoint seguirá respondiendo, adjuntando el detalle en `errors` para que el frontend pueda mostrar un aviso.

### GET `/aq/metropolitan-forecast`
- Pronóstico agregado para la Zona Metropolitana; estima hasta `hours` horas hacia el futuro usando un baseline (media de las últimas `window` horas por estación).
- Parámetros opcionales:
  - `hours`: horizonte en horas (default `168`, equivalente a 7 días). Límites recomendados `1` a `720` (30 días).
  - `window`: ventana en horas para el promedio histórico por estación (default `24`).
  - `pollutants`: lista separada por comas (p. ej. `pm10,pm25,o3`) siempre que existan en el dataset.
```bash
curl "https://<tu-dominio>/api/aq/metropolitan-forecast?hours=168&window=24"
```
```json
{
  "generated_at": "2024-12-24T12:05:10Z",
  "horizon_hours": 168,
  "window_hours": 24,
  "pollutants": ["pm10", "pm25"],
  "locations_count": 6,
  "locations": [
    {
      "location_id": "7919",
      "baseline_window": {
        "start": "2024-12-23T12:00:00+00:00",
        "end": "2024-12-24T11:00:00+00:00",
        "rows": 24
      },
      "baseline_stats": {
        "pm10": {"window_avg": 64.1, "window_min": 42.0, "window_max": 88.5, "samples": 24},
        "pm25": {"window_avg": 22.4, "window_min": 15.1, "window_max": 34.2, "samples": 18}
      },
      "predictions": [
        {"timestamp": "2024-12-24T12:00:00+00:00", "pollutants": {"pm10": 64.1, "pm25": 22.4}},
        {"timestamp": "2024-12-24T13:00:00+00:00", "pollutants": {"pm10": 64.1, "pm25": 22.4}},
        "..."
      ]
    }
  ],
  "aggregate": {
    "timeline": [
      {
        "timestamp": "2024-12-24T12:00:00+00:00",
        "pollutants": {
          "pm10": {"avg": 63.4, "min": 46.0, "max": 77.8, "locations_reporting": 6},
          "pm25": {"avg": 25.5, "min": 19.8, "max": 30.3, "locations_reporting": 4}
        }
      }
    ],
    "stats": {
      "pm10": {"overall_avg": 63.4, "overall_min": 46.0, "overall_max": 109.1},
      "pm25": {"overall_avg": 25.5, "overall_min": 19.8, "overall_max": 35.8}
    }
  },
  "highlights": {
    "pm10": {"location_id": "7951", "value": 109.1, "timestamp": "2024-12-24T12:00:00+00:00"}
  }
}
```
- Util para dashboards de planificación semanal/mensual; ten presente que es un baseline y no sustituye un modelo entrenado para horizontes largos (puedes reemplazarlo por Prophet/CatBoost en el futuro y reutilizar la misma estructura de respuesta).

> Los endpoints que dependen de servicios externos (OpenAQ/OpenWeather) devolverán errores 4xx/5xx si faltan las llaves de entorno o si la API upstream responde fuera de rango. Maneja estos casos en el frontend mostrando un mensaje de reintento.
