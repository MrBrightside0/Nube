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
│   ├── routes.py           # Endpoints (actualmente placeholders)
│   ├── constants.py        # IDs de sensores y claves esperadas via .env
│   ├── requests_service.py # Cliente HTTP básico con autenticación OpenAQ
│   ├── openaq_connection.py
│   ├── weather_api_connection.py
│   └── openstreetmap_connection.py
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

## Endpoints actuales (`api/routes.py`)
| Método | Ruta               | Estado | Descripción |
|--------|--------------------|--------|-------------|
| GET    | `/api/health`      | ✅     | Health check simple. |
| GET    | `/api/aq/latest`   | 🚧     | Devolver última medición de PM2.5/NO2 y clima; pendiente integrar clientes. |
| GET    | `/api/aq/trends`   | 🚧     | Tendencias históricas y correlaciones. |
| GET    | `/api/aq/forecast` | 🚧     | Pronóstico 24h usando Prophet/ARIMA. |
| GET    | `/api/aq/sources`  | 🚧     | Metadatos de datasets usados. |
| POST   | `/api/alerts/subscribe` | 🚧 | Registro de preferencias para alertas. |

> Los endpoints marcados como 🚧 contienen TODOs para conectar con los clientes reales (`tempo_client`, `openaq_client`, `weather_client`) y persistir la información.

## Scripts y utilidades
- `api/openaq_connection.py`: descarga datos históricos de sensores regiomontanos desde el bucket S3 de OpenAQ.
- `api/weather_api_connection.py`: baja series horarias de Meteostat para estaciones cercanas.
- `api/openstreetmap_connection.py`: genera un dataset sintético de tráfico para Monterrey usando OSMnx.
- `ai/predict_data.py`: pronósticos y visualizaciones (Prophet, resampling diario).
- `ai/model.py`: pipeline de entrenamiento para gases y partículas (NN + CatBoost).
- `ai/test.py`: consulta industrias cercanas a un sensor vía Overpass API (diagnóstico).

### Datos usados por los modelos (`ai/`)
- `ai/create_dataset.py` fusiona todas las fuentes necesarias para entrenar los modelos:
  - **Calidad del aire**: agrega todas las estaciones presentes en `ai/air_data/` (Universidad, Tecnológico, Centro de Monterrey, San Nicolás, Escobedo, Apodaca). Cada CSV se pivota por `parameter`, se normalizan columnas (`location_id`, `value`) y se ordena por estación.
  - **Clima**: combina todas las estaciones Meteostat en `ai/weather_data/`, calcula medias horarias (`temp_mean`, `rhum_mean`, `wspd_mean`) y preserva las columnas individuales (`temp_76393`, `temp_MMMY0`, etc.).
  - **Ingeniería de atributos**: interpola huecos cortos (hasta 6 muestras), genera rolling averages y diferencias (6/24 h) para cada contaminante, además de variables de calendario (hora, día de la semana, mes, `sin/cos`).
- El dataset unificado se guarda en `ai/output/dataset_final.csv` y contiene todas las estaciones de la ZMM con `location_id`, `lat`, `lon` y las features generadas.
- `ai/model.py` consume ese dataset consolidado: el modelo de gases usa todas las variables meteorológicas y las series de contaminantes, mientras que los modelos CatBoost de partículas se entrenan por objetivo pero siguen viendo los datos de todas las estaciones (sólo descartan filas que no tengan el contaminante específico).
- `ai/models/` almacena los artefactos (`gas_model.keras`, `catboost_pm10.cbm`, `catboost_pm25.cbm`) junto con metadatos de columnas e imputaciones para reproducir inferencia en API (`/api/aq/predictions`).

## Flujo de trabajo recomendado
1. **Sincronizar datos**: ejecutar los scripts de descarga según sea necesario (ocupando claves y verificando cuotas de API).
2. **Entrenar modelos**: correr `ai/model.py` o `ai/predict_data.py` para actualizar modelos y pronósticos.
3. **Exponer servicios**: completar los TODOs en `api/routes.py` conectando los clientes de datos y modelos.
4. **Despliegue**: usar el Dockerfile y Railway/Render para desplegar el backend (asegura las variables de entorno).

## Próximos pasos sugeridos
- Implementar los clientes `tempo_client`, `openaq_client` y `weather_client` y conectarlos en los endpoints.
- Añadir almacenamiento para suscripciones (por ejemplo, base de datos ligera o servicio externo).
- Sustituir prints por logging estructurado y manejar errores HTTP con códigos apropiados.
- Automatizar pruebas básicas de los endpoints (PyTest + Flask testing client).
