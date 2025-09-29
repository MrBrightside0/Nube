import requests
import pandas as pd

def get_nearby_industries(sensor_lat: float, sensor_lon: float, radius_km: float = 10) -> pd.DataFrame:
    """
    Consulta OpenStreetMap para obtener fabricas/industrias
    cercanas a un sensor.
    """

# Calcular bounding box (aprox: 1° ~ 111 km)
    delta = radius_km / 111.0
    bbox = f"{sensor_lat - delta},{sensor_lon - delta},{sensor_lat + delta},{sensor_lon + delta}"

    # Query Overpass API
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="industry"]({bbox});
      node["industrial"]({bbox});
      node["building"="industrial"]({bbox});

      way["amenity"="industry"]({bbox});
      way["industrial"]({bbox});
      way["building"="industrial"]({bbox});

      relation["amenity"="industry"]({bbox});
      relation["industrial"]({bbox});
      relation["building"="industrial"]({bbox});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={'data': query})

    if response.status_code != 200:
        print("❌ Error al consultar Overpass API")
        return pd.DataFrame()

    data = response.json()
    industries = []

    for element in data.get('elements', []):
        if 'lat' in element and 'lon' in element:  
            lat, lon = element['lat'], element['lon']
        elif 'center' in element:  
            lat, lon = element['center']['lat'], element['center']['lon']
        else:
            continue

        name = element.get('tags', {}).get('name', 'Unnamed Factory')
        tag = element.get('tags', {}).get('amenity', element.get('tags', {}).get('building', 'industrial'))
        industries.append({'name': name, 'lat': lat, 'lon': lon, 'tag': tag})

    if industries:
        df = pd.DataFrame(industries).drop_duplicates(subset=['lat','lon'])
        return df
    else:
        return pd.DataFrame(columns=['name','lat','lon','tag'])


if __name__ == "__main__":
    sensor_lat, sensor_lon = 25.800411111110996, -100.58487777778
    df_industries = get_nearby_industries(sensor_lat, sensor_lon, radius_km=10)

    if not df_industries.empty:
        print("Fábricas / Industrias cercanas al sensor:")
        print(df_industries[['name','lat','lon','tag']])
    else:
        print("No se encontraron fábricas cercanas en la zona.")

