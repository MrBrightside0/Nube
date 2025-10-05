# CleanSkies API 🌎

Backend FastAPI que expone servicios de calidad del aire (AQI), tendencias y un asistente conversacional.

## 🔧 Ejecución local
```bash
pip install -r requirements.txt
python api.py
```

### Variables de entorno relevantes
- `ALLOWED_ORIGINS`: lista separada por comas con los orígenes que pueden llamar a la API (ej. `https://app.mi-frontend.com,https://admin.mi-frontend.com`). Si no se define, se permiten `http://localhost:3000` y `http://localhost:5173` para desarrollo.

## 📚 Rutas de la API

### GET `/api/health`
- **Descripción:** Comprobación simple para verificar que el servicio está operativo.
- **Query params:** Ninguno.
- **Respuesta 200:**
  ```json
  {"ok": true}
  ```

### GET `/api/aq/predict`
- **Descripción:** Genera una predicción de AQI para la ubicación indicada utilizando datos recientes de OpenAQ y clima.
- **Query params:**
  - `lat` (`float`, requerido) — Latitud del punto de interés.
  - `lon` (`float`, requerido) — Longitud del punto de interés.
- **Respuesta 200:**
  ```json
  {
    "name": "Current Zone",
    "lat": 19.4326,
    "lon": -99.1332,
    "aqi": 82.14,
    "pm25": 35.2,
    "no2": 16.5,
    "wind": 3.4,
    "trend": [
      {"ts": "Hour 1", "pm25": 34.2, "no2": 15.5},
      {"ts": "Hour 2", "pm25": 35.2, "no2": 16.5}
    ]
  }
  ```
- **Notas:** El campo `trend` contiene hasta 6 observaciones horarias simuladas a partir del valor actual.
- **Errores:** Si ocurre algún problema al consultar datos externos o el modelo de IA, la respuesta será `{ "error": "detalle" }`.

### POST `/api/chat`
- **Descripción:** Chatbot SatAirlite conectado a OpenAI que responde con recomendaciones según el contexto de calidad del aire.
- **Body (JSON):**
  ```json
  {
    "message": "texto del usuario",
    "aqi": 85
  }
  ```
- **Notas:** El campo `message` es obligatorio; `aqi` es opcional y ayuda a contextualizar la respuesta.
- **Respuesta 200:**
  ```json
  {"response": "texto del asistente"}
  ```
- **Errores:** Ante un fallo interno devuelve `{ "response": "Hubo un problema al conectar con el asistente." }`.

### GET `/api/aq/trends`
- **Descripción:** Obtiene una serie temporal de contaminantes PM2.5 y NO₂ y la correlación entre ambos para los últimos `days` días.
- **Query params:**
  - `lat` (`float`, requerido)
  - `lon` (`float`, requerido)
  - `days` (`int`, opcional, por defecto `7`) — Número de puntos a generar/analizar.
- **Respuesta 200:**
  ```json
  {
    "trend": [
      {"ts": "2024-05-01", "pm25": 32.1, "no2": 18.3},
      {"ts": "2024-05-02", "pm25": 30.4, "no2": 16.8}
    ],
    "correlation": 0.67
  }
  ```
- **Notas:** Si el modelo de tendencias falla se generan datos simulados realistas y la correlación se calcula en base a ellos.
