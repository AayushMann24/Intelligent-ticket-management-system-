import requests

BASE_URL = "http://127.0.0.1:8000"

def get_all_tickets():
    response = requests.get(
        f"{BASE_URL}/tickets"
)
    return response.json()