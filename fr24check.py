import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FR24_API_KEY")

url = "https://fr24api.flightradar24.com/api/live/flight-positions/light"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Accept-Version": "v1",
    "API-Version": "v1"
}
params = {"bounds": "38.3,36.8,-123.2,-121.5"}  # Bay Area box

resp = requests.get(url, headers=headers, params=params)
print("Status:", resp.status_code)
print(resp.text[:600])
