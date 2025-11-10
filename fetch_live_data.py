import json
import requests
import pandas as pd

def fetch_flights(bbox=(-123.5, -121.5, 36.5, 38.5)):
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
    token = response.json()["access_token"]

    url = f"https://opensky-network.org/api/states/all?lamin={bbox[2]}&lomin={bbox[0]}&lamax={bbox[3]}&lomax={bbox[1]}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    flights = response.json()

    columns = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact",
        "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
        "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
        "spi", "position_source"
    ]
    df_live = pd.DataFrame(flights["states"], columns=columns)
    return df_live
