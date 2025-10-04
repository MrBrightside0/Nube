# Nube Backend API

## Descripcion general
Este backend expone una API HTTP con Flask para consultar datos sinteticos de calidad del aire, predicciones generadas por un prototipo de IA y un end point de subscripcion de alertas. Incluye ademas un script auxiliar para conectarse a la API de OpenAI.

## Requisitos
- Python 3.11+ (desarrollado con Python 3.13)
- pip para instalar dependencias
- Cuenta y clave de API de OpenAI si quieres usar `api/openai_connection.py`

## Configuracion del entorno
1. Crear y activar un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv env
   source env/bin/activate
   ```
2. Instalar dependencias principales:
   ```bash
   pip install flask openai python-dotenv
   ```

## Variables de entorno
El archivo `constants.py` carga variables desde un archivo `.env` o desde el entorno del sistema. Define al menos las siguientes claves antes de iniciar el servidor:

| Nombre | Uso |
| --- | --- |
| `OPEN_AQ_KEY` | Token para integrar con OpenAQ (opcional en este prototipo) |
| `OPENWEATHER_KEY` | Clave de OpenWeather (opcional) |
| `TEMPO_KEY` | Clave del satelite TEMPO (opcional) |
| `EARTH_ACCESS_KEY` | Clave para servicios de datos de la NASA (opcional) |
| `OPENAI_API_KEY` | Requerida para `api/openai_connection.py` |
| `OPENAI_MODEL` | Modelo de OpenAI a usar (`gpt-4o-mini` por defecto) |
| `OPENAI_TEMPERATURE` | Temperatura a usar al llamar a OpenAI (`0.2` por defecto) |

`constants.py` imprime en consola que llaves fueron detectadas, lo cual ayuda a validar la configuracion.

## Ejecucion local
```bash
python Nube.py
```
El servidor levanta en `http://localhost:5000/` y expone los siguientes endpoints bajo el blueprint `api`.

## Endpoints

### GET `/health`
Devuelve un estado simple para comprobar que el servicio esta vivo.

```bash
curl http://localhost:5000/health
```
Respuesta de ejemplo:
```json
{"status": "ok"}
```

### GET `/aq/latest`
Entrega valores sinteticos de calidad del aire para una ubicacion.

Parametros de consulta:
- `lat` (float, opcional)
- `lon` (float, opcional)
- `pollutant` (string, opcional, default `pm25`)

```bash
curl "http://localhost:5000/aq/latest?lat=25.67&lon=-100.31&pollutant=pm25"
```
Respuesta de ejemplo:
```json
{
  "aqi": 88,
  "pm25": 15.7,
  "pm10": 42.2,
  "no2": 37.1,
  "wind": 3.8,
  "sources": ["TEMPO", "MODEL"],
  "pollutant": "pm25"
}
```

### GET `/aq/trends`
Devuelve series historicas sinteticas para varios contaminantes.

Parametros de consulta:
- `lat` (float, opcional)
- `lon` (float, opcional)
- `days` (int, opcional, default `7`)

```bash
curl "http://localhost:5000/aq/trends?lat=25.67&lon=-100.31&days=5"
```
Respuesta de ejemplo:
```json
{
  "series": [
    {"ts": "2024-09-27T12:00:00Z", "pm25": 12.8, "no2": 21.0},
    {"ts": "2024-09-28T12:00:00Z", "pm25": 13.6, "no2": 22.3}
  ],
  "correlation": 0.63
}
```

### GET `/ai/predict`
Genera predicciones sinteticas a futuro para el contaminante seleccionado.

Parametros de consulta:
- `lat` (float, opcional)
- `lon` (float, opcional)
- `pollutant` (string, opcional, default `pm25`)
- `days` (int, opcional, default `30`)

```bash
curl "http://localhost:5000/ai/predict?lat=25.67&lon=-100.31&days=3"
```
Respuesta de ejemplo:
```json
{
  "pollutant": "pm25",
  "predictions": [
    {"ds": "2024-10-01", "yhat": 15.0},
    {"ds": "2024-10-02", "yhat": 15.4},
    {"ds": "2024-10-03", "yhat": 15.8}
  ]
}
```

### GET `/ai/seasonal`
Retorna una tendencia semanal sintetica para el contaminante indicado.

Parametros de consulta:
- `lat` (float, opcional)
- `lon` (float, opcional)
- `pollutant` (string, opcional, default `pm25`)

```bash
curl "http://localhost:5000/ai/seasonal?pollutant=pm25"
```
Respuesta de ejemplo:
```json
{
  "pollutant": "pm25",
  "trend": [
    {"ts": "2024-07-14", "value": 10.0},
    {"ts": "2024-07-21", "value": 10.7}
  ]
}
```

### POST `/alerts/subscribe`
Registra una subscripcion de alertas para un contacto. Requiere un JSON con la informacion de contacto y preferencias.

Cuerpo esperado:
```json
{
  "contact": {
    "name": "Ada Lovelace",
    "email": "ada@example.com"
  },
  "preferences": {
    "type": "sms",
    "city": "Monterrey"
  }
}
```

```bash
curl -X POST http://localhost:5000/alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "contact": {"name": "Ada Lovelace", "email": "ada@example.com"},
    "preferences": {"type": "sms", "city": "Monterrey"}
  }'
```
Respuesta de ejemplo:
```json
{
  "message": "Subscription registered",
  "contact": {"name": "Ada Lovelace", "email": "ada@example.com"},
  "preferences": {"type": "sms", "city": "Monterrey"}
}
```

## Script de OpenAI
El archivo `api/openai_connection.py` permite interactuar con el API de OpenAI y garantiza respuestas en formato JSON. Ejemplo rapido:

```bash
export OPENAI_API_KEY="tu-token"
python api/openai_connection.py --prompt "Describe la calidad del aire en JSON" --model gpt-4o-mini
```

Tambien puedes pasar un payload JSON por stdin:

```bash
echo '{"prompt": "Devuelve {\\"status\\": \\"ok\\"}"}' | python api/openai_connection.py
```

Si ejecutas `python api/openai_connection.py --test` se realiza una llamada breve para validar la clave configurada.

## Desarrollo
- Los endpoints viven en `api/routes.py` y se montan en `Nube.py`.
- Ajusta la logica segun sea necesario para conectar con fuentes de datos reales.
- El script `api/openai_connection.py` reutiliza las variables de `constants.py` para mantenerse sincronizado con el entorno.
