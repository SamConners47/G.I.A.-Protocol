import { useState, useEffect } from "react";
import "./App.css";

const API_BASE = "gia-protocol-production-4b69.up.railway.app"; // Update after Railway deploy

interface Event {
  id: number;
  title: string;
  description: string;
  severity: string;
  date: string;
  regions: string[];
}

interface ImpactResponse {
  event: string;
  location: string;
  overall_severity: number;
  impacts: Record<string, any>;
}

function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [impacts, setImpacts] = useState<ImpactResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState("India");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/api/events`)
      .then(r => r.json())
      .then(setEvents)
      .catch(() => {
        // FALLBACK EVENTS
        setEvents([
          { id: 1, title: "Middle East Oil Crisis", description: "15% global supply disruption", severity: "high", date: "2026-01-05", regions: ["Middle East"] },
          { id: 2, title: "Ukraine Grain Blockade", description: "Black Sea exports halted", severity: "high", date: "2026-01-04", regions: ["Europe"] }
        ]);
      });
  }, []);

  const analyzeEvent = async (event: Event) => {
    setImpacts(null);
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: `${event.title}: ${event.description}`, location })
      });
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setImpacts(data);
    } catch (e) {
      console.error(e);
      setError("Using demo data (backend temporarily unavailable)");
      // FAKE LOADING
      setTimeout(() => {
        setImpacts({
          event: event.title,
          location,
          overall_severity: 7.2,
          impacts: {
            energy: {severity: 8, timeframe: "immediate", example: "Petrol +₹5", impact_description: "Oil crisis"},
            food: {severity: 6, timeframe: "2 weeks", example: "Rice +15%", impact_description: "Supply chain"},
            travel: {severity: 7, timeframe: "immediate", example: "Flights +20%", impact_description: "Fuel costs"},
            jobs: {severity: 4, timeframe: "1 month", example: "Exports delayed", impact_description: "Trade risk"},
            currency: {severity: 5, timeframe: "2 weeks", example: "₹84/$", impact_description: "Import pressure"}
          }
        });
        setLoading(false);
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  const getColor = (severity: number) => 
    severity >= 7 ? "#ff4444" : severity >= 4 ? "#ff9900" : "#44aa44";

  return (
    <div className="app">
      <header>
        <h1>⚡ G.I.A. Protocol</h1>
        <p>Geopolitical Impact Analyzer</p>
      </header>

      <div className="container">
        <div className="sidebar">
          <div className="location">
            <label>Location:</label>
            <select value={location} onChange={e => setLocation(e.target.value)}>
              <option>India</option>
              <option>USA</option>
              <option>Europe</option>
              <option>Global</option>
            </select>
          </div>

          <h2>Recent Events</h2>
          <div className="events">
            {events.map(event => (
              <div key={event.id} className="event" onClick={() => analyzeEvent(event)}>
                <div className="event-header">
                  <h3>{event.title}</h3>
                  <span className={`severity ${event.severity}`}>{event.severity}</span>
                </div>
                <p>{event.description}</p>
                <small>{event.date}</small>
              </div>
            ))}
          </div>
        </div>

        <div className="main">
          {loading && <div className="loading">🤖 Analyzing impacts...</div>}
          
          {error && <div className="error">{error}</div>}
          
          {impacts && (
            <div className="analysis">
              <h2>Impact Analysis: {impacts.location}</h2>
              
              <div className="overall">
                <div>Overall Severity</div>
                <div className="meter">
                  <div className="fill" style={{ 
                    width: `${(impacts.overall_severity / 10) * 100}%`,
                    backgroundColor: getColor(impacts.overall_severity)
                  }} />
                </div>
                <div className="score">{impacts.overall_severity.toFixed(1)}/10</div>
              </div>

              <div className="impacts">
                {Object.entries(impacts.impacts).map(([category, data]) => (
                  <div key={category} className="impact" style={{ 
                    borderLeftColor: getColor(data.severity)
                  }}>
                    <h4>{category.toUpperCase()}</h4>
                    <div>Severity: <strong>{data.severity}/10</strong></div>
                    <div>{data.timeframe}</div>
                    <div><strong>{data.example}</strong></div>
                    <div className="desc">{data.impact_description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!impacts && !loading && !error && (
            <div className="placeholder">
              Click an event to analyze its impact on daily life
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
