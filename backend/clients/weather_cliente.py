import requests
import os

OWM_API_KEY = os.getenv("OWM_API_KEY", "229eaec3d1f52e5eb0eb86d609fc50b")  # ← tu key

def get_weather_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    res = requests.get(url).json()

    # Si la respuesta no contiene "main", devolvemos valores por defecto
    if "main" not in res or "wind" not in res:
        print("⚠️ Error en respuesta de OpenWeather:", res)
        return {"temp": 25.0, "humidity": 50.0, "wind_speed": 2.0}

    return {
        "temp": res["main"].get("temp", 25.0),
        "humidity": res["main"].get("humidity", 50.0),
        "wind_speed": res["wind"].get("speed", 2.0),
    }
