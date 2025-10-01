# multiagent_dispatcher.py
import json
from typing import Any, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Import tools
from travel_tools import search_hotels, search_attractions, get_weather

# --- Setup Gemini ---
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")
genai.configure(api_key=GEMINI_KEY)

# --- JSON helpers ---
def _extract_first_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in model response")
    return text[start:end+1]

def parse_model_json(text: str) -> Dict[str, Any]:
    snippet = _extract_first_json(text)
    try:
        return json.loads(snippet)
    except Exception:
        repaired = snippet.replace("'", '"')
        return json.loads(repaired)

# --- Multi-Agent Dispatcher ---
def call_multiagent(model, user_prompt: str, tools: Dict[str, Any], max_steps: int = 6) -> Dict[str, Any]:
    instruction = (
        "You are a multi-agent coordinator. Always reply ONLY with JSON.\n"
        "Format: {\"action\": <tool>, \"args\": {..}}.\n\n"
        "Available tools:\n"
        "- hotel_agent(lat, lng, limit)\n"
        "- attraction_agent(lat, lng, limit)\n"
        "- weather_agent(lat, lng, days)\n\n"
        "When finished, reply {\"action\": \"done\", \"result\": \"<final detailed plan>\"}.\n"
        "Expand the itinerary into paragraphs (one per day). Do NOT include lat/lng in the final output."
    )

    history = instruction + "\n\nUser: " + user_prompt

    for _ in range(max_steps):
        resp = model.generate_content(history)
        text = resp.text.strip()

        try:
            j = parse_model_json(text)
        except Exception:
            return {"error": "parse_failed", "raw": text}

        action = j.get("action")
        args = j.get("args", {})

        if action == "done":
            return {"done": True, "result": j.get("result", "")}

        if action in tools:
            try:
                result = tools[action](**args)
            except Exception as e:
                result = {"error": str(e)}
            history += f"\nToolResult {action}: {json.dumps(result, default=str)}"
        else:
            return {"error": "unknown_action", "raw": j}

    return {"error": "max_steps_exceeded"}

# --- Wrappers for tools ---
def hotel_agent(lat, lng, limit=5):
    return search_hotels(lat, lng, limit=limit)

def attraction_agent(lat, lng, limit=5):
    return search_attractions(lat, lng, limit=limit)

def weather_agent(lat, lng, days=5):
    return get_weather(lat, lng, days)

# --- Convenience wrapper ---
def run_multiagent_dispatcher(query: str, lat: float, lng: float, days: int = 3):
    model = genai.GenerativeModel("gemini-2.0-flash")

    tools = {
        "hotel_agent": hotel_agent,
        "attraction_agent": attraction_agent,
        "weather_agent": weather_agent,
    }

    result = call_multiagent(model, f"Plan a {days}-day trip to {query}", tools)

    if "done" in result and result["done"]:
        return result["result"]
    return f"⚠️ Multi-Agent dispatch failed: {result}"
