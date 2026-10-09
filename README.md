# 🌍 Asteroid Impact Simulator

A scientifically accurate asteroid impact simulation tool with real-time NASA data integration, atmospheric physics modeling, economic impact analysis, and planetary defense planning.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![NASA API](https://img.shields.io/badge/NASA-API-orange)

---

## 🚀 Features

- **Real-time NASA Integration** — Live asteroid feed from NASA's Near-Earth Object API
- **Advanced Physics Engine** — Atmospheric entry, fragmentation, blast, seismic & fireball effects
- **Interactive Map Simulator** — Click-to-select impact location with Leaflet.js damage zone visualization
- **Economic Impact Analysis** — Regional GDP-based damage estimation with recovery timeline
- **Planetary Defense Planning** — Kinetic impactor, gravity tractor, nuclear deflection strategies
- **Live Dashboard** — Real-time asteroid tracking with NASA Sentry risk objects
- **Fallback Mode** — Works offline with realistic demo data when NASA API rate-limited

---

## 🛠️ Local Setup

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/asteroid-impact-tool.git
cd asteroid-impact-tool
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env and set your NASA_API_KEY
```

Get a free NASA API key at: **https://api.nasa.gov/**

> Without your own key, `DEMO_KEY` still works (30 requests/hour, 50/day)

### 3. Run Locally

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🌐 Deployment

### Deploy to Render (Recommended — Free)

1. Push your code to GitHub
2. Go to **https://render.com** → New → Web Service
3. Connect your GitHub repo
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
6. Add environment variables:
   - `NASA_API_KEY` = your API key
   - `SECRET_KEY` = a random secret string
   - `DEBUG` = `False`

### Deploy to Heroku

```bash
heroku create your-asteroid-tool
heroku config:set NASA_API_KEY=your_key SECRET_KEY=your_secret DEBUG=False
git push heroku main
```

---

## 🏗️ Project Structure

```
asteroid-impact-tool/
├── app.py                    # Flask application & API routes
├── config.py                 # Configuration & environment variables
├── run.py                    # CLI runner
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment process file
├── runtime.txt               # Python version pin
├── .env.example              # Environment template
├── src/
│   ├── main.py               # AsteroidLauncher — simulation orchestrator
│   ├── impact_calculator.py  # Physics: crater, blast, seismic, fireball
│   ├── atmospheric_model.py  # Atmospheric entry & fragmentation physics
│   ├── economic_impact.py    # GDP-based economic damage calculator
│   ├── population_analyzer.py# Population impact estimator
│   ├── mitigation_solver.py  # Planetary defense strategies
│   ├── nasa_api.py           # NASA NEO API integration
│   ├── real_time_tracker.py  # Background asteroid monitor
│   └── visualization.py      # Report generation
├── templates/
│   ├── index.html            # Landing page
│   ├── simulator.html        # Interactive simulator
│   └── dashboard.html        # Live tracking dashboard
└── static/
    ├── css/style.css         # Main stylesheet
    ├── css/animations.css    # Animation keyframes
    ├── js/asteroid_simulator.js   # Simulator logic & results display
    ├── js/real_time_data.js  # Live data fetching & dashboard
    ├── js/interactive_map.js # Leaflet map utilities
    └── js/particles.js       # Particle background system
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/launch` | Run a full impact simulation |
| `GET`  | `/api/nasa/live-feed` | Today's asteroids from NASA |
| `GET`  | `/api/nasa/sentry` | NASA Sentry risk objects |
| `GET`  | `/api/asteroid/<id>` | Detailed asteroid info |
| `GET`  | `/api/stats/global` | Global tracking statistics |
| `GET`  | `/api/simulations/active` | Active simulation list |

### Example: Launch Simulation

```bash
curl -X POST http://localhost:5000/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "asteroid_type": "stone",
    "diameter": 500,
    "speed": 20,
    "angle": 45,
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

---

## 🧪 Physics Models

| Effect | Model |
|--------|-------|
| Crater size | Holsapple scaling law with angle correction |
| Atmospheric entry | US Standard Atmosphere + Sutton-Graves heating |
| Fragmentation | Dynamic pressure vs material strength |
| Blast wave | Overpressure scaling with damage zones |
| Seismic | Energy-to-Richter-magnitude conversion |
| Economic | Regional GDP density × damage factor |

---

## 📄 License

MIT License — Educational and research use.

Data provided by [NASA Near Earth Object Program](https://neo.jpl.nasa.gov/).
