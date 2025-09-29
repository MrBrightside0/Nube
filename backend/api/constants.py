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


