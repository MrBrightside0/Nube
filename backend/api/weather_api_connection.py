from urllib.request import urlretrieve
from constants import WEATHER_STATIONS_DICT
import os

#Descargar csv de datos historicos
def download_weather_data(start_year: int, end_year: int, output_dir: str = "."):
    os.makedirs(output_dir, exist_ok=True)

    for year in range(start_year, end_year + 1):
        for station_id in WEATHER_STATIONS_DICT.keys():
            url = f"https://data.meteostat.net/hourly/{year}/{station_id}.csv.gz"
            filename = f"{output_dir}/{station_id}_{year}.csv.gz"
            
            try:
                urlretrieve(url, filename)
                print(f"[INFO] Archivo {filename} descargado")
            except Exception as e:
                print(f"[INFO] Error descargando {station_id=} {year=}: {e}")

if __name__ == "__main__":
    download_weather_data(2020, 2024, output_dir="../ai/weather_data")

