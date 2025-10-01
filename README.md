# 🧳 Smart Travel AI Assistant

An AI-powered *travel planning assistant* built with *Streamlit, **Google Maps API, **Open-Meteo, and **Gemini AI*.  
It helps users plan trips with *AI itineraries, hotels, attractions, weather forecasts, and flight links*.  
Supports both *single-agent (Gemini)* and *multi-agent* dispatching.

---

## 🚀 Features
- ✅ AI-generated itineraries using *Gemini* (single-agent) or *multi-agent* dispatching  
- ✅ Hotel & attraction search via *Google Maps Places API*  
- ✅ 5-day weather forecast via *Open-Meteo API*  
- ✅ Interactive Google Maps links for each location  
- ✅ Flight search links (Google Flights & Skyscanner)  
- ✅ Export trip details as a *PDF report*  
- ✅ Streamlit app with tabbed interface  
- ✅ Toggle between *Gemini* and *Multi-Agent* dispatchers  

---

## 📂 Project Structure

travel-ai-assistant/
│── agent_app.py              # Main Streamlit app
│── travel_tools.py           # Tools (Google Maps, weather, etc.)
│── function_dispatcher.py    # Single-agent Gemini dispatcher
│── multiagent_dispatcher.py  # Multi-agent dispatcher
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
│── .gitignore                # Ignore sensitive files
│── .env                      # API keys (not in GitHub)

---

## 🔑 Setup

### ⿡ Clone repo
```bash
git clone https://github.com/<your-username>/travel-ai-assistant.git
cd travel-ai-assistant

⿢ Create & activate virtual environment

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

⿣ Install dependencies

pip install -r requirements.txt

⿤ Add API Keys

Create a .env file in the project root:

GMAPS_KEY=your_google_maps_api_key
OWM_KEY=your_open_meteo_key   # (not always needed, Open-Meteo is free)
GEMINI_KEY=your_gemini_api_key


⸻

🖥 Run Locally

streamlit run agent_app.py

Then open: http://localhost:8501

⸻

☁ Deploy on Google Cloud Run
	1.	Install Google Cloud CLI
	2.	Authenticate:

gcloud init


	3.	Enable Cloud Run + Build:

gcloud services enable run.googleapis.com cloudbuild.googleapis.com


	4.	Deploy:

gcloud run deploy travel-ai-app \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated


	5.	Set environment variables:

gcloud run services update travel-ai-app \
  --region us-central1 \
  --update-env-vars GMAPS_KEY="your_key",OWM_KEY="your_key",GEMINI_KEY="your_key"



Your app will be live at:

https://<service-name>-<project-id>.us-central1.run.app

