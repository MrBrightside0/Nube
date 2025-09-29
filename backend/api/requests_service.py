import requests
from constants import OPENAQ_KEY
def get_request(url : str):
    headers = {
        "X-API-Key": OPENAQ_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}


def post_request(data: dict, url : str):
    headers = {
        "X-API-Key": OPENAQ_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

