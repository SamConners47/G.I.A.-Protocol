import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/api/events", methods=["GET"])
def get_real_events():
    """Fetch LIVE geopolitical events from NewsAPI"""
    try:
        # Real news query
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "geopolitics OR war OR sanctions OR \"trade war\" OR ukraine OR china OR russia OR israel OR iran",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": NEWS_API_KEY
        }
        
        if not NEWS_API_KEY:
            return _mock_events()
            
        response = requests.get(url, params=params, timeout=10)
        articles = response.json().get("articles", [])
        
        events = []
        for i, article in enumerate(articles[:5]):
            events.append({
                "id": i + 1,
                "title": article["title"][:80] + "..." if len(article["title"]) > 80 else article["title"],
                "description": article["description"][:120] + "..." if article["description"] else "Breaking geopolitical development",
                "severity": "high" if any(word in article["title"].lower() for word in ["war", "attack", "crisis"]) else "medium",
                "date": article["publishedAt"][:10],
                "source": article["source"]["name"],
                "url": article["url"],
                "regions": _extract_regions(article["title"] + " " + article["description"])
            })
            
        return jsonify(events or _mock_events())
        
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return _mock_events()

def _extract_regions(text: str) -> list:
    """Extract regions from news text"""
    regions = []
    region_words = ["ukraine", "russia", "china", "israel", "iran", "middle east", "europe", "asia", "usa"]
    for word in region_words:
        if word in text.lower():
            regions.append(word.replace(" ", "-").title())
    return regions or ["Global"]

@app.route("/api/analyze", methods=["POST"])
def analyze_real():
    """REAL AI analysis with fallback"""
    try:
        data = request.json or {}
        event = data.get("event", "")
        location = data.get("location", "India")
        
        if not event:
            return jsonify({"error": "Event required"}), 400
        
        # Try real Gemini analysis
        if GEMINI_API_KEY:
            return _gemini_analysis(event, location)
        else:
            return _mock_analysis(event, location)
            
    except Exception as e:
        print(f"Analysis error: {e}")
        return _mock_analysis(event, location)

def _gemini_analysis(event: str, location: str):
    """Real Gemini AI analysis"""
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try multiple models
    models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.0-pro"]
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"""
            Geopolitical event: "{event}"
            User location: {location}
            
            Analyze impact on daily life in these categories:
            1. Energy (fuel/electricity prices)  
            2. Food costs (groceries/inflation)
            3. Travel (flights/transport)
            4. Jobs (employment stability)
            5. Currency (local exchange rates)
            
            Return ONLY valid JSON:
            {{
              "energy": {{"severity": 1-10, "timeframe": "immediate|2 weeks|1 month", "example": "Petrol +₹5", "impact": "Oil prices spike"}},
              "food": {{...}},
              "travel": {{...}},
              "jobs": {{...}},
              "currency": {{...}}
            }}
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean JSON
            for marker in ["```json", "```"]:
                if text.startswith(marker): text = text[len(marker):]
                if text.endswith(marker): text = text[:-len(marker):]
            
            impacts = json.loads(text)
            overall = sum(v.get("severity", 0) for v in impacts.values()) / len(impacts)
            
            return jsonify({
                "event": event,
                "location": location,
                "impacts": impacts,
                "overall_severity": round(overall, 1),
                "source": "Google Gemini AI"
            })
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
    
    # All models failed
    return _mock_analysis(event, location)

def _mock_analysis(event: str, location: str):
    """Realistic mock data"""
    return jsonify({
        "event": event,
        "location": location,
        "overall_severity": 7.2,
        "impacts": {
            "energy": {"severity": 8, "timeframe": "immediate", "example": "Petrol ₹105", "impact": "Oil supply disruption"},
            "food": {"severity": 6, "timeframe": "2 weeks", "example": "Wheat +25%", "impact": "Grain supply issues"},
            "travel": {"severity": 7, "timeframe": "immediate", "example": "Flights +18%", "impact": "Fuel surcharges"},
            "jobs": {"severity": 4, "timeframe": "1 month", "example": "Export jobs risk", "impact": "Trade uncertainty"},
            "currency": {"severity": 5, "timeframe": "2 weeks", "example": "₹84/USD", "impact": "Import costs rise"}
        },
        "source": "Fallback Analysis"
    })

def _mock_events():
    """Fallback events"""
    return jsonify([
        {"id": 1, "title": "Global News Service Unavailable", "description": "Using demo data", "severity": "medium", "date": "2026-01-05", "regions": ["Global"]}
    ])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
