from function_dispatcher import run_gemini_dispatcher

# Example inputs
destination = "Rome"
days = 4
lat, lng = 41.8902, 12.4922   # Near Colosseum

print("=== Testing Gemini Dispatcher ===")
plan = run_gemini_dispatcher(
    f"Plan a {days}-day trip to {destination} with hotels, attractions, and weather.",
    lat=lat,
    lng=lng,
    days=days
)

print("\n--- AI Plan ---")
print(plan)
