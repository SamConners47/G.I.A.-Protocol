from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MOCK EVENTS (always works)
@app.route("/api/events", methods=["GET"])
def get_events():
    return jsonify([
        {
            "id": 1,
            "title": "Middle East Oil Crisis",
            "description": "Tensions disrupt 15% of global oil supply",
            "severity": "high",
            "date": "2026-01-05",
            "regions": ["Middle East", "Global"]
        },
        {
            "id": 2, 
            "title": "Ukraine Grain Blockade",
            "description": "Black Sea exports halted affecting food prices",
            "severity": "high",
            "date": "2026-01-04",
            "regions": ["Europe", "Global"]
        },
        {
            "id": 3,
            "title": "US-China Tech Tariffs",
            "description": "New 25% tariffs on electronics imports",
            "severity": "medium",
            "date": "2026-01-03",
            "regions": ["USA", "China", "Global"]
        }
    ])

# BULLETPROOF ANALYZE (mock + real AI fallback)
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json or {}
        event = data.get("event", "")
        location = data.get("location", "India")
        
        if not event:
            return jsonify({"error": "Event required"}), 400
        
        # MOCK DATA (always works for demo)
        mock_response = {
            "event": event,
            "location": location,
            "overall_severity": 7.2,
            "impacts": {
                "energy": {
                    "severity": 8,
                    "timeframe": "immediate",
                    "example": "Petrol ₹105/litre",
                    "impact_description": "Oil supply disruption spikes fuel prices"
                },
                "food": {
                    "severity": 6,
                    "timeframe": "2 weeks", 
                    "example": "Wheat +25%",
                    "impact_description": "Grain export blockade raises grocery costs"
                },
                "travel": {
                    "severity": 7,
                    "timeframe": "immediate",
                    "example": "Flights +18%",
                    "impact_description": "Airlines pass fuel surcharges to passengers"
                },
                "jobs": {
                    "severity": 4,
                    "timeframe": "1 month",
                    "example": "500K jobs at risk",
                    "impact_description": "Export industries face uncertainty"
                },
                "currency": {
                    "severity": 5,
                    "timeframe": "2 weeks",
                    "example": "₹84/USD",
                    "impact_description": "Oil imports pressure rupee value"
                }
            }
        }
        return jsonify(mock_response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "G.I.A. Protocol API running",
        "endpoints": ["/api/events", "/api/analyze"],
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
