import requests

# Rome (Colosseum) coordinates
lat, lon = 41.8902, 12.4922

url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_mean,weathercode&timezone=auto"

resp = requests.get(url)
data = resp.json()

print("Weather Forecast (Next 3 days):")
for i in range(3):
    print(
        f"Day {i+1}: "
        f"Max {data['daily']['temperature_2m_max'][i]}°C, "
        f"Min {data['daily']['temperature_2m_min'][i]}°C, "
        f"Rain chance {data['daily']['precipitation_probability_mean'][i]}%"
    )
