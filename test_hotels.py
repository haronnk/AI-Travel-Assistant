# test_hotels.py
import os, requests
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()
API_KEY = os.getenv("GMAPS_KEY")

if not API_KEY:
    raise SystemExit("❌ Google Maps key not found in .env")

# Coordinates for the Colosseum in Rome
lat, lng = 41.8902, 12.4922

# Nearby hotels request (using Places API)
url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1500&type=lodging&key={API_KEY}"
resp = requests.get(url, timeout=10)
resp.raise_for_status()
data = resp.json()

print("API Status:", data.get("status"))
print("Found:", len(data.get("results", [])), "results (showing up to 5):\n")

for hotel in data.get("results", [])[:5]:
    print("-", hotel.get("name"), "| Rating:", hotel.get("rating", "N/A"))
