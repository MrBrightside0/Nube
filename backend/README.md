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
- `ai/model.py`: entrena NN para gases y CatBoost individual para PM10/PM25; guarda artefactos + metadatos en `ai/models/`.
- `ai/inference.py`: carga modelos/escálers y permite pruebas rápidas (`--rows`).
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
