import requests
import pandas as pd
from datetime import datetime
import os
from time import sleep

# --- Configuration ---
API_BASE = "https://opensky-network.org/api"
SFO_ICAO = "KSFO"
DATA_PATH = "data/sfo_goarounds.csv"   # your filtered 2019 dataset
OUT_DIR = "data/tracks_2019"
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_historical_track(icao24, timestamp):
    """
    Fetch historical track for a given aircraft ICAO24 and UNIX timestamp (2019).
    """
    url = f"{API_BASE}/tracks/all?icao24={icao24}&time={timestamp}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"⚠️ Error fetching track for {icao24}: {response.text}")
        return None

    data = response.json()
    if "path" not in data or data["path"] is None:
        print(f"⚠️ No path for {icao24} at {timestamp}")
        return None

    df = pd.DataFrame(
        data["path"],
        columns=["time", "lat", "lon", "baro_altitude", "true_track", "on_ground"]
    )
    return df


def fetch_tracks_from_2019(n=10):
    """
    Fetch tracks for up to n flights from the 2019 dataset (for cross-checking runway info).
    """
    sfo_df = pd.read_csv(DATA_PATH)
    sfo_df["time"] = pd.to_datetime(sfo_df["time"], utc=True)

    # Take 10 go-arounds (or mix with normal landings)
    subset = sfo_df.sample(n)
    print(f"📆 Fetching tracks for {len(subset)} flights from 2019...")

    for _, row in subset.iterrows():
        icao = row["icao24"]
        ts = int(row["time"].timestamp())
        callsign = str(row["callsign"]).strip().replace(" ", "_")

        print(f"➡️ Fetching {callsign or icao} @ {datetime.utcfromtimestamp(ts)}")
        df_track = fetch_historical_track(icao, ts)

        if df_track is None or df_track.empty:
            continue

        file_path = os.path.join(OUT_DIR, f"track_{callsign or icao}_{ts}.csv")
        df_track.to_csv(file_path, index=False)
        print(f"💾 Saved {len(df_track)} points → {file_path}")
        sleep(5)  # polite delay to avoid rate limits


if __name__ == "__main__":
    fetch_tracks_from_2019(n=100)
