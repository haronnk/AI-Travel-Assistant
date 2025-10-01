# travel_tools.py
import os
import requests
import googlemaps
from dotenv import load_dotenv

# --- Load API keys ---
load_dotenv()
GMAPS_KEY = os.getenv("GMAPS_KEY")
gmaps = googlemaps.Client(key=GMAPS_KEY)


# --- Core Tools ---
def geocode_place(place):
    """Geocode a place name into latitude & longitude."""
    res = gmaps.geocode(place)
    return res[0]['geometry']['location'] if res else None


def search_hotels(lat, lng, radius=1500, limit=5):
    """Search nearby hotels given coordinates."""
    resp = gmaps.places_nearby(location=(lat, lng), radius=radius, type="lodging")
    hotels = []
    for h in resp.get('results', [])[:limit]:
        hotels.append({
            "name": h.get("name"),
            "rating": h.get("rating", "N/A"),
            "lat": h["geometry"]["location"]["lat"],
            "lng": h["geometry"]["location"]["lng"]
        })
    return hotels


def search_attractions(lat, lng, radius=2000, limit=5):
    """Search nearby tourist attractions given coordinates."""
    resp = gmaps.places_nearby(location=(lat, lng), radius=radius, type="tourist_attraction")
    attractions = []
    for a in resp.get('results', [])[:limit]:
        attractions.append({
            "name": a.get("name"),
            "rating": a.get("rating", "N/A"),
            "lat": a["geometry"]["location"]["lat"],
            "lng": a["geometry"]["location"]["lng"]
        })
    return attractions


def get_walk_info(origin, dest):
    """Get walking distance and duration between two places."""
    routes = gmaps.directions(origin, dest, mode="walking")
    if not routes:
        return None
    leg = routes[0]['legs'][0]
    return {
        "distance": leg.get("distance", {}).get("text"),
        "duration": leg.get("duration", {}).get("text")
    }


def get_weather(lat, lon, days=5):
    """Fetch daily weather forecast for given coordinates."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,"
        f"temperature_2m_min,precipitation_probability_mean,weathercode&timezone=auto"
    )
    resp = requests.get(url)
    data = resp.json()

    weather = []
    for i in range(min(days, len(data["daily"]["temperature_2m_max"]))):
        weather.append({
            "day": f"Day {i+1}",
            "max_temp": data["daily"]["temperature_2m_max"][i],
            "min_temp": data["daily"]["temperature_2m_min"][i],
            "rain": f"{data['daily']['precipitation_probability_mean'][i]}%"
        })
    return weather


def show_route_map(origin_lat, origin_lng, dest_lat, dest_lng):
    """Return an iframe embed code for walking directions between two points."""
    iframe = f"""
    <iframe
      width="100%" height="250"
      frameborder="0" style="border:0"
      src="https://www.google.com/maps/embed/v1/directions?key={GMAPS_KEY}
        &origin={origin_lat},{origin_lng}
        &destination={dest_lat},{dest_lng}
        &mode=walking" allowfullscreen>
    </iframe>
    """
    return iframe
