import json
import requests
import pandas as pd

with open("credentials.json") as f:
    creds = json.load(f)
    client_id = creds["clientId"]
    client_secret = creds["clientSecret"]

auth_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

auth_data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

response = requests.post(auth_url, data=auth_data)

token_data = response.json()
token = token_data["access_token"]

url = "https://opensky-network.org/api/states/all?lamin=37&lomin=-123&lamax=38&lomax=-122"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
flights = response.json()

columns = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source"
]

df = pd.DataFrame(flights["states"], columns=columns)

goaround_df = pd.read_csv("data/go_arounds_augmented.csv")
sfo_df = goaround_df[goaround_df["airport"] == "KSFO"]
sfo_df.to_csv("data/sfo_goarounds.csv", index=False)

print(sfo_df["has_ga"].value_counts())
print("Saved file shape:", sfo_df.shape)
