import os
from dotenv import load_dotenv
import google.generativeai as genai
from function_dispatcher import call_gemini_and_dispatch

# Load keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")  # replace with the one in your list_models.py

# Example tools
def add(a: int, b: int):
    return {"sum": a + b}

def greet(name: str):
    return {"message": f"Hello, {name}!"}

tools = {
    "add": add,
    "greet": greet
}

# Run
query = "Can you greet Haron and then add 5+7?"
result = call_gemini_and_dispatch(model, query, tools)
print("FINAL RESULT:", result)
