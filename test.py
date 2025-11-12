import requests, os, pprint
HEADERS = {
    "Authorization": f"Bearer {os.getenv('FR24_API_KEY')}",
    "Accept": "application/json",
    "Accept-Version": "v1"
}
r = requests.get(
    "https://fr24api.flightradar24.com/api/flight-tracks",
    headers=HEADERS,
    params={"flight_id":"3d0d1cc7", "date":"2025-11-10"}
)
print(r.status_code, r.text[:500])
pprint.pprint(r.json())
