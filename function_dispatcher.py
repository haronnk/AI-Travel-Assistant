# function_dispatcher.py
import json
import re
from typing import Any, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
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


# --- Cleaner to strip lat/lng ---
def clean_output(text: str) -> str:
    """
    Remove coordinates (lat/lng) if they slip into Gemini's final result.
    Example: "Lat: 41.89, Lng: 12.48" -> removed.
    """
    # Remove "Lat: ... Lng: ..." patterns
    text = re.sub(r"Lat:\s*[\d\.\-]+,\s*Lng:\s*[\d\.\-]+", "", text)
    text = re.sub(r"\(Lat:[^)]+\)", "", text)
    # Remove any raw coordinate floats with commas
    text = re.sub(r"\([\d\.\-]+\s*,\s*[\d\.\-]+\)", "", text)
    return text.strip()


# --- Dispatcher ---
def call_gemini_and_dispatch(model, user_prompt: str, tools: Dict[str, Any], max_steps: int = 4) -> Dict[str, Any]:
    instruction = (
        "You are a travel planner AI. Always reply ONLY with JSON.\n"
        "Format: {\"action\": <tool>, \"args\": {..}}.\n\n"
        "Tools available:\n"
        "- search_hotels(lat, lng, radius=1500, limit=5)\n"
        "- search_attractions(lat, lng, radius=2000, limit=5)\n"
        "- get_weather(lat, lon, days=5)\n\n"
        "When finished, reply {\"action\": \"done\", \"result\": \"<final plan>\"}.\n\n"
        "IMPORTANT:\n"
        "- Do NOT include lat/lng or technical details in the final plan.\n"
        "- Write the itinerary in long, rich paragraphs (morning, afternoon, evening).\n"
        "- Hotels and weather should be summarized in natural language, no raw data.\n"
        "- Aim for a detailed travel blog style itinerary with context and flow."
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
            result_text = j.get("result", "")
            return {"done": True, "result": clean_output(result_text)}

        if action in tools:
            try:
                result = tools[action](**args)
            except Exception as e:
                result = {"error": str(e)}
            history += f"\nToolResult {action}: {json.dumps(result, default=str)}"
        else:
            return {"error": "unknown_action", "raw": j}

    return {"error": "max_steps_exceeded"}


# --- Convenience wrapper ---
def run_gemini_dispatcher(user_prompt: str, lat=None, lng=None, days=3):
    model = genai.GenerativeModel("gemini-2.0-flash")

    tools = {
        "search_hotels": search_hotels,
        "search_attractions": search_attractions,
        "get_weather": get_weather,
    }

    result = call_gemini_and_dispatch(model, user_prompt, tools)

    if "done" in result and result["done"]:
        return result["result"]
    return f"⚠️ Gemini dispatch failed: {result}"
