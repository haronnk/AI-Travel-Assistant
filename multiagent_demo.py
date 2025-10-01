# multiagent_demo.py
from multiagent_dispatcher import run_multiagent_dispatcher

if __name__ == "__main__":
    print("\n--- Multi-Agent Demo Output ---\n")
    query = "Rome"
    days = 3
    lat, lng = 41.9028, 12.4964  # Rome coords

    result = run_multiagent_dispatcher(query, lat, lng, days)
    print(result)
