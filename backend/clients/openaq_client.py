import requests

def get_latest_openaq(lat, lon):
    url = f"https://api.openaq.org/v2/measurements?coordinates={lat},{lon}&radius=5000&limit=5&sort=desc&order_by=datetime"
    res = requests.get(url).json()
    pm25, no2 = None, None
    for r in res.get("results", []):
        if r["parameter"] == "pm25" and pm25 is None:
            pm25 = r["value"]
        if r["parameter"] == "no2" and no2 is None:
            no2 = r["value"]
    return pm25 or 25.0, no2 or 20.0
