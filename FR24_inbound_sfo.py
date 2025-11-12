import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("FR24_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Accept-Version": "v1"
}

url = "https://fr24api.flightradar24.com/api/historic/flight-positions/full"

# Start around 2025-11-08 03:00 UTC (example, adjust for peak period)
start_time = datetime(2025, 11, 8, 3, 0)
records = []

for i in range(60):  # every minute for an hour
    target_time = start_time + timedelta(minutes=i)
    timestamp_unix = int(target_time.timestamp())
    print(f"⏱️ Fetching {target_time.isoformat()} ({timestamp_unix})...")

    params = {
        "airports": "inbound:KSFO",
        "timestamp": timestamp_unix,
        "bounds": "38.3,36.8,-123.2,-121.5",
    }

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        flights = data.get("data", [])
        print(f"✅ {len(flights)} flights at {target_time}")
        for flight in flights:
            records.append({
                "timestamp": target_time.isoformat(),
                "callsign": flight.get("callsign"),
                "origin": flight.get("orig_icao"),
                "altitude_ft": flight.get("alt"),
                "speed_kt": flight.get("gspeed"),
                "eta": flight.get("eta"),
                "lat": flight.get("lat"),
                "lon": flight.get("lon"),
            })
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")

    time.sleep(1)  # polite delay to avoid rate limits

df = pd.DataFrame(records)
filename = f"data/inbound_SFO_hour_{start_time.strftime('%Y%m%d_%H%M')}.csv"
df.to_csv(filename, index=False)
print(f"\n💾 Saved {len(df)} total records to {filename}")
