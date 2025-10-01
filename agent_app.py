# agent_app.py
import os, streamlit as st, pandas as pd
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Import shared tools + dispatcher
from travel_tools import (
    geocode_place,
    search_hotels,
    search_attractions,
    get_walk_info,
    show_route_map,
    get_weather,
)
from multiagent_dispatcher import run_multiagent_dispatcher
from function_dispatcher import run_gemini_dispatcher

# --- PDF Export ---
def export_pdf(reply, hotels, attractions, weather, query, days):
    file_path = "travel_plan.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Smart Travel AI Assistant")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Query: {query}")
    c.drawString(50, height - 100, f"Days: {days}")

    # Hotels
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 140, "Hotels Nearby")
    c.setFont("Helvetica", 11)
    y = height - 160
    for h in hotels:
        text = f"- {h['name']} | Rating: {h.get('rating','N/A')}"
        c.drawString(60, y, text[:100])
        y -= 20

    # Attractions
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "Attractions Nearby")
    c.setFont("Helvetica", 11)
    y -= 40
    for a in attractions:
        text = f"- {a['name']} | Rating: {a.get('rating','N/A')}"
        c.drawString(60, y, text[:100])
        y -= 20

    # Weather
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "Weather Forecast")
    c.setFont("Helvetica", 11)
    y -= 40
    for w in weather:
        text = f"{w['day']}: {w['min_temp']}°C - {w['max_temp']}°C, Rain: {w['rain']}"
        c.drawString(60, y, text)
        y -= 20

    # AI Plan
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "AI Suggested Itinerary")
    c.setFont("Helvetica", 11)
    y -= 40
    for line in reply.split("\n"):
        if line.strip():
            c.drawString(60, y, line[:100])
            y -= 20
            if y < 50:  
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)

    c.save()
    return file_path


# --- Agent Logic ---
def travel_agent(query, days=3, hotel_limit=5, attraction_limit=5, use_multiagent=False):
    loc = geocode_place(query)
    if not loc:
        return "❌ Could not find destination.", [], [], [], loc

    lat, lng = loc['lat'], loc['lng']

    # --- AI Dispatcher ---
    try:
        if use_multiagent:
            ai_plan = run_multiagent_dispatcher(
                f"Plan a {days}-day trip to {query} with hotels, attractions, and weather.",
                lat=lat, lng=lng, days=days
            )
        else:
            ai_plan = run_gemini_dispatcher(
                f"Plan a {days}-day trip to {query} with hotels, attractions, and weather.",
                lat=lat, lng=lng, days=days
            )
    except Exception as e:
        ai_plan = f"⚠️ Dispatcher failed: {e}\n\nFallback: basic plan for {query}."

    # Fallback calls
    hotels = search_hotels(lat, lng, limit=hotel_limit)
    attractions = search_attractions(lat, lng, limit=attraction_limit)
    weather = get_weather(lat, lng, days)

    return ai_plan, hotels, attractions, weather, loc


# --- Streamlit UI ---
st.set_page_config(page_title="Smart Travel AI Assistant", layout="wide")
st.title("🧳 Smart Travel AI Assistant")

# Sidebar
st.sidebar.title("ℹ️ About")
st.sidebar.write(
    "The **Smart Travel AI Assistant** helps you plan trips by suggesting hotels, "
    "attractions, weather forecasts, and flight search links. "
    "It combines Google Maps, Open-Meteo, and Gemini AI to generate personalized itineraries."
)
st.sidebar.markdown("---")
st.sidebar.write("👤 Built by **Haron**")

# Toggle Dispatcher
use_multiagent = st.sidebar.toggle("Use Multi-Agent Mode", value=True)

# Filters
query = st.text_input("Where do you want to go?", key="destination_input")
trip_days = st.sidebar.slider("Number of days", 1, 14, 3, key="days_slider")
hotel_limit = st.sidebar.slider("Number of hotels to show", 1, 10, 5, key="hotels_slider")
attraction_limit = st.sidebar.slider("Number of attractions to show", 1, 10, 5, key="attractions_slider")

if st.button("Plan My Trip", key="plan_button"):
    with st.spinner("Generating your travel plan..."):
        reply, hotels, attractions, weather, loc = travel_agent(
            query, trip_days, hotel_limit, attraction_limit, use_multiagent
        )

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📝 Itinerary", "🏨 Hotels", "📍 Attractions", "🌦 Weather", "✈ Flights"]
        )

        with tab1:
            st.subheader("AI Travel Itinerary")
            st.write(reply)

        with tab2:
            st.subheader("Hotels Nearby")
            for h in hotels:
                st.write(f"**{h['name']} (⭐ {h.get('rating','N/A')})**")
                st.markdown(show_route_map(h["lat"], h["lng"], loc["lat"], loc["lng"]), unsafe_allow_html=True)
                st.markdown(f"[📍 Open in Google Maps](https://www.google.com/maps?q={h['lat']},{h['lng']})")

        with tab3:
            st.subheader("Attractions Nearby")
            for a in attractions:
                st.write(f"**{a['name']} (⭐ {a.get('rating','N/A')})**")
                st.markdown(show_route_map(a["lat"], a["lng"], loc["lat"], loc["lng"]), unsafe_allow_html=True)
                st.markdown(f"[📍 Open in Google Maps](https://www.google.com/maps?q={a['lat']},{a['lng']})")

        with tab4:
            st.subheader("Weather Forecast")
            df = pd.DataFrame(weather)
            st.dataframe(df)

            # 🌈 Line graph for temperature
            chart_data = pd.DataFrame({
                "Day": [w["day"] for w in weather],
                "Max Temp (°C)": [w["max_temp"] for w in weather],
                "Min Temp (°C)": [w["min_temp"] for w in weather]
            }).set_index("Day")

            st.line_chart(chart_data)

            # 🌧️ Rain probability as bar chart
            rain_data = pd.DataFrame({
                "Day": [w["day"] for w in weather],
                "Rain Probability (%)": [int(w["rain"].replace("%", "")) for w in weather]
            }).set_index("Day")

            st.bar_chart(rain_data)

        with tab5:
            st.subheader("Flight Search Links")
            st.markdown(f"[Google Flights](https://www.google.com/travel/flights)")
            st.markdown(f"[Skyscanner](https://www.skyscanner.net/)")

        # PDF Export
        pdf_path = export_pdf(reply, hotels, attractions, weather, query, trip_days)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="travel_plan.pdf")
