import os
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
API_KEY = os.getenv("FR24_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Accept-Version": "v1",
    "API-Version": "v1"
}

HISTORIC_URL = "https://fr24api.flightradar24.com/api/historic/flight-positions/full"
TRACK_URL = "https://fr24api.flightradar24.com/api/flight-tracks"

# -----------------------------
# Step 1: Fetch inbound flights from recent intervals
# -----------------------------
tracks = []
now = datetime.now(timezone.utc)
intervals = [now - timedelta(hours=h) for h in range(1, 6, 1)] 

for ts in intervals:
    unix_ts = int(ts.timestamp())
    print(f"\n🕒 Fetching inbound flights at {ts.isoformat()}...")
    params = {
        "airports": "inbound:KSFO",
        "bounds": "38.3,36.8,-123.2,-121.5",
        "timestamp": unix_ts,
        "limit": 20
    }

    resp = requests.get(HISTORIC_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print("❌ Error fetching inbound flights:", resp.text)
        continue

    flights = resp.json().get("data", [])
    print(f"→ Found {len(flights)} flights")

    # -----------------------------
    # Step 2: For each flight, fetch its track
    # -----------------------------
    for i, f in enumerate(flights):
        fr24_id = f.get("fr24_id")
        callsign = f.get("callsign")
        if not fr24_id:
            continue

        date_str = ts.strftime("%Y-%m-%d")
        print(f"   ({i+1}/{len(flights)}) Track for {callsign} ({fr24_id})...")

        t_resp = requests.get(
            TRACK_URL,
            headers=HEADERS,
            params={"flight_id": fr24_id, "date": date_str}
        )
        print(f"      URL: {t_resp.url}")
        print(f"      Status: {t_resp.status_code}")
        print(f"      Body: {t_resp.text[:400]}")

        if t_resp.status_code != 200:
            print(f"      ⚠️ Failed: {t_resp.status_code} {t_resp.text[:150]}")
            time.sleep(6)
            continue

        try:
            t_json = t_resp.json()
        except Exception as e:
            print(f"      ⚠️ JSON decode error for {callsign}: {e}")
            continue

        if not t_json or t_json == []:
            print(f"      ⚠️ Empty response for {callsign} ({fr24_id}) on {date_str}")
            continue

        # FR24 sometimes returns a list, sometimes {"tracks": [...]}
        if isinstance(t_json, list):
            points = []
            for obj in t_json:
                if isinstance(obj, dict) and "tracks" in obj:
                    points.extend(obj["tracks"])
        elif isinstance(t_json, dict):
            points = t_json.get("tracks", [])
        else:
            points = []

        if not points:
            print(f"      ⚠️ No track points for {callsign}")
            continue

        for p in points:
            if all(k in p for k in ["lat", "lon", "alt", "timestamp"]):
                tracks.append({
                    "callsign": callsign,
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "alt": p["alt"],
                    "timestamp": p["timestamp"]
                })

        time.sleep(6)  # stay under 10 req/min

# -----------------------------
# Step 3: Save & visualize
# -----------------------------
df_tracks = pd.DataFrame(tracks)
print(f"\n✅ Saved {len(df_tracks)} points from {df_tracks['callsign'].nunique() if not df_tracks.empty else 0} flights.")
df_tracks.to_csv("sfo_landing_paths.csv", index=False)

if df_tracks.empty:
    print("⚠️ No track data found to plot.")
    exit()

plt.figure(figsize=(8, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-123.2, -121.5, 36.8, 38.3])
ax.coastlines()
ax.gridlines(draw_labels=True)


for callsign, group in df_tracks.groupby("callsign"):
    plt.plot(group["lon"], group["lat"], linewidth=1, transform=ccrs.PlateCarree(), label=callsign)

plt.title("Inbound Flight Paths to SFO (Historical Data)")
plt.legend(fontsize=6, loc="lower left")
plt.show()
