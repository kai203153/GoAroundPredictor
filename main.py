import json
import requests

with open("credentials.json") as f:
    creds = json.load(f)
    client_id = creds["clientId"]
    client_secret = creds["clientSecret"]

auth_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

response = requests.post(auth_url, data=data)

data = response.json()
token = data["access_token"]

url = "https://opensky-network.org/api/states/all?lamin=37&lomin=-123&lamax=38&lomax=-122"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
flights = response.json()

print("✈️ Number of flights:", len(flights["states"]))
print("First entry:", flights["states"][0])
