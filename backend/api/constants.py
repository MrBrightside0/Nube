import os
from dotenv import load_dotenv

load_dotenv()

OPENAQ_KEY = os.getenv("OPEN_AQ_KEY")
SENSORS_DICT = {"Garcia" : 4454898,
                "San Bernabe" : 4408712,
                "Universidad" : 7951,
                "Santa Catarina" : 4454946,
                "San Pedro" : 10713,
                "Preparatoria ITESM Eugenio Garza Lagüera" : 4454896,
                "TECNL" : 4454900,
                "Juarez" : 427,
                "Cadereyta" : 4454897,
                "Pesqueria" : 10666,
                "Apodaca" : 7919,
                "San Nicolas" : 4454899,
                "Misión San Juan" : 4454945,
                "Escobedo" : 4411165,
                "Obispado" : 8059,
                }

WEATHER_STATIONS_DICT = {
    "76393": {
        "name": "Monterrey",
        "lat": 25.8667,
        "lon": -100.2000
    },
    "76394": {
        "name": "Monterrey Airport",
        "lat": 25.8667,
        "lon": -100.2333
    },
    "MMMY0": {
        "name": "Monterrey / Las Ladrilleras",
        "lat": 25.7786,
        "lon": -100.1071
    }
}


