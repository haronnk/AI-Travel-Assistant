# test_weather.py (One Call 3.0)
import os
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
OWM_KEY = os.getenv("OWM_KEY")

print("Loaded OWM_KEY:", OWM_KEY)

if not OWM_KEY:
    raise SystemExit("❌ OWM_KEY not found in .env file")

# Example: Rome coordinates
lat, lon = 41.8902, 12.4922

# Use One Call 3.0 endpoint
url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,current,alerts&units=metric&appid={OWM_KEY}"

print("Requesting URL:", url)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print("❌ Error fetching weather:", e)
    raise SystemExit()

print("Raw API Response:", data)

# Show next 3 days forecast
for day in data.get("daily", [])[:3]:
    temp = day["temp"]["day"]
    desc = day["weather"][0]["description"]
    pop = day.get("pop", 0) * 100
    print(f"Temp: {temp}°C | {desc} | Rain chance: {pop:.1f}%")
