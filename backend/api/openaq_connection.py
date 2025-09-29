from requests_service import get_request 
import xml.etree.ElementTree as ET
from constants import SENSORS_DICT
import requests
import os

BASE_URL = "https://api.openaq.org/v3/locations/"
BUCKET_URL = "https://openaq-data-archive.s3.amazonaws.com"
OUTPUT_DIR = "../ai/data/"


def get_sensor_data(sensor_id : int) -> dict:
    api_url = BASE_URL + str(sensor_id)
    data = get_request(api_url)

    return data 


def get_monterrey_sensors_data() -> dict:
    sensors_data = list()
    
    for location in SENSORS_DICT.keys():
        print(f"[INFO] Obteniendo datos del sensor ubicado en {location}")
        sensors_data.append(get_sensor_data(SENSORS_DICT[location]))
    
    print(sensors_data)
    return sensors_data


def download_historical_data(location: str, start_year: int = 2020, end_year: int = 2025) -> None:
    dir_name = f"{OUTPUT_DIR}{location}/"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(dir_name, exist_ok=True)

    location_id = SENSORS_DICT[location]

    for year in range(start_year, end_year + 1):
        prefix = f"records/csv.gz/locationid={location_id}/year={year}/"
        url = f"{BUCKET_URL}?list-type=2&prefix={prefix}"
        print(f"[INFO] Listando archivos de {year} para {location}")
        resp = requests.get(url)
        resp.raise_for_status()
        
        root = ET.fromstring(resp.text)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        files = [c.find("s3:Key", ns).text for c in root.findall("s3:Contents", ns)]
        
        for f in files:
            file_url = f"{BUCKET_URL}/{f}"
            filename = os.path.join(dir_name, os.path.basename(f))
            
            if os.path.exists(filename):
                print(f"[SKIP] {filename} ya existe")
                continue
            
            print(f"[DOWNLOAD] {file_url} → {filename}")
            r = requests.get(file_url, stream=True)
            r.raise_for_status()
            with open(filename, "wb") as out:
                for chunk in r.iter_content(chunk_size=8192):
                    out.write(chunk)
    
    print("[INFO] Descarga completa de datos históricos")


def download_all_sensors_historical_data() -> None:
    for location in SENSORS_DICT.keys():
        download_historical_data(location,
                                 start_year=2021,
                                 end_year=2023
                                 )


if __name__ == "__main__":
    download_all_sensors_historical_data()
