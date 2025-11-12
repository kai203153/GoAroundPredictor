import os
import requests
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
API_KEY = os.getenv("FR24_API_KEY")

if not API_KEY:
    raise ValueError("❌ FR24_API_KEY not found in .env file!")

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Accept-Version": "v1"
}

# ✅ Live API endpoint
BASE_URL = "https://fr24api.flightradar24.com/api/live/flight-positions/full"

# Bounding box for the San Francisco Bay Area (north, south, west, east)
params = {
    "bounds": "38.3,36.8,-123.2,-121.5",
    "limit": 100
}

print("Fetching live flights near SFO...")

response = requests.get(BASE_URL, headers=HEADERS, params=params)

print(f"Status: {response.status_code}")
print(response.text)
