# ☄️ AsteroidIQ — Real-Time Planetary Defense & Impact Simulator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-AsteroidIQ%20on%20Render-00e5ff?style=for-the-badge&logo=render)](https://asteroid-impact-tool.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![NASA API](https://img.shields.io/badge/NASA-API%20Integrated-orange?style=for-the-badge&logo=nasa)](https://api.nasa.gov/)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

> **Live Deployment:** [https://asteroid-impact-tool.onrender.com](https://asteroid-impact-tool.onrender.com)

A science-grade planetary defense simulation platform bridging real-time NASA JPL telemetry, multi-physics hydrodynamic impact modeling, atmospheric ablation & airburst dynamics, economic damage assessment, and AI-powered planetary defense planning.

---

## 🌟 Key Features

- **🌐 Live Telemetry Feed** — Real-time orbital monitoring of near-Earth objects using NASA's NeoWs & Sentry impact risk catalogs.
- **💥 Multi-Physics Impact Engine** — Hydrodynamic cratering equations (Schmidt-Holsapple scaling), atmospheric fragmentation/ablation, thermal fireball flux ($r^{-2}$ radiation), peak overpressure shockwaves, and seismic Richter magnitude.
- **🛡️ Planetary Defense Planning (DART Physics)** — Interactive mitigation testing including Kinetic Impactors (NASA DART mission physics), Gravity Tractors, Zero-G impactors, and civilian evacuation modeling.
- **⚖️ Dual-Scenario Comparison Engine** — Compare two impact scenarios side by side with real-time differential physics bars (energy ratio, crater size, casualty differential, and economic loss).
- **🤖 ARIA AI Assistant** — Asteroid Risk Intelligence Assistant that answers complex planetary defense questions with context-aware insights based on current simulation metrics.
- **🗺️ High-Precision GIS Mapping** — Interactive Leaflet maps powered by clean, watermark-free **Esri Dark Gray Canvas** tiles with dynamic damage zone overlays.
- **📄 Mission Report Export** — One-click JSON mission report export detailing all parameters, physics breakdowns, and recovery timelines.

---

## 🚀 Live Demo & Navigation

- **Landing Page**: [https://asteroid-impact-tool.onrender.com/](https://asteroid-impact-tool.onrender.com/)
- **Impact Simulator**: [https://asteroid-impact-tool.onrender.com/simulator](https://asteroid-impact-tool.onrender.com/simulator)
- **Live NASA Dashboard**: [https://asteroid-impact-tool.onrender.com/dashboard](https://asteroid-impact-tool.onrender.com/dashboard)
- **API Health Check**: [https://asteroid-impact-tool.onrender.com/api/health](https://asteroid-impact-tool.onrender.com/api/health)

---

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/KRISH-0201/asteroid-impact-tool.git
cd asteroid-impact-tool
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and provide your NASA API key (or use the included default):
```env
NASA_API_KEY=DIZpTOKqJRe011xRfnquTks6ZVwxLHkQaxeVF0IU
SECRET_KEY=your_secret_key_here
DEBUG=True
FLASK_ENV=development
```

*(Get a free API key at [api.nasa.gov](https://api.nasa.gov/))*

### 4. Run Automated Test Suite

```bash
python test_all_endpoints.py
```
*(All 10/10 end-to-end tests should pass with 100% success rate)*

### 5. Start the Server

```bash
python app.py
```

Open your browser at **http://localhost:5001** (or **http://127.0.0.1:5001**).

---

## ☁️ Deployment

### Render (Configured via `render.yaml`)

The repository includes a ready-to-use `render.yaml` blueprint:

1. Push your repository to GitHub: `https://github.com/KRISH-0201/asteroid-impact-tool`
2. Go to [dashboard.render.com](https://dashboard.render.com/) → **New +** → **Web Service**
3. Connect `KRISH-0201/asteroid-impact-tool`
4. Set:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Instance Type**: `Free`
5. Environment Variables:
   - `NASA_API_KEY`: `DIZpTOKqJRe011xRfnquTks6ZVwxLHkQaxeVF0IU`
   - `PYTHON_VERSION`: `3.11.9`
   - `FLASK_ENV`: `production`
   - `DEBUG`: `False`

---

## 🔌 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & system status |
| `POST` | `/api/launch` | Execute full multi-physics impact simulation |
| `POST` | `/api/compare` | Dual-scenario side-by-side comparative analysis |
| `POST` | `/api/ai/analyze` | ARIA AI assistant contextual analysis |
| `GET` | `/api/presets` | Historical asteroid presets (Tunguska, Chelyabinsk, Chicxulub, etc.) |
| `GET` | `/api/nasa/live-feed` | Live tracked near-Earth objects from NASA API |
| `GET` | `/api/nasa/sentry` | NASA Sentry potential impact risk catalog |
| `GET` | `/api/stats/global` | Global tracking statistics & engine cache status |
| `GET` | `/api/export/simulation/<id>`| Export simulation mission report |

---

## 🔬 Scientific & Physics Models

| Effect / Metric | Model & Governing Physics |
| :--- | :--- |
| **Crater Diameter** | Schmidt-Holsapple scaling laws with target rock density and impact angle corrections |
| **Atmospheric Entry** | Numerical integration of drag deceleration ($\frac{dv}{dt}$) & Sutton-Graves convective heating |
| **Airburst Yield** | Hydrodynamic ram pressure vs. asteroid tensile yield strength threshold |
| **Fireball & Thermal** | Inverse-square radiation flux decay $q = \frac{\eta E}{4\pi r^2}$ with emission duration scaling |
| **Shockwave Blast** | Glasstone & Dolan overpressure scaling with 5 psi and 1 psi damage thresholds |
| **Seismic Impact** | Gutenberg-Richter equivalent magnitude $M_w = 0.67 \log_{10}(E_{\text{seismic}}) - 5.87$ |
| **Planetary Defense** | NASA DART momentum enhancement factor $\beta$ kinetic deflection modeling |

---

## 🏗️ Project Architecture

```
asteroid-impact-tool/
├── app.py                     # Flask application gateway & REST API routes
├── config.py                  # System constants & environment config
├── render.yaml                # 1-Click Render deployment blueprint
├── requirements.txt           # Python dependencies
├── Procfile                   # Process file for cloud deployment
├── runtime.txt                # Python 3.11.9 runtime pin
├── test_all_endpoints.py      # Automated 10/10 test suite
├── src/
│   ├── main.py                # AsteroidLauncher — orchestrator & math integration
│   ├── impact_calculator.py   # Physics: crater, thermal, overpressure, seismic
│   ├── atmospheric_model.py   # Atmospheric entry, drag & airburst model
│   ├── mitigation_solver.py   # DART kinetic impactor & defense physics
│   ├── economic_impact.py     # GDP-based exposure & recovery model
│   ├── population_analyzer.py # Casualty & mortality estimations
│   ├── nasa_api.py            # NASA NeoWs & Sentry telemetry integration
│   ├── real_time_tracker.py   # Background telemetry monitor
│   ├── usgs_api.py            # Elevation service integration
│   └── visualization.py       # Mission report compiler
├── templates/
│   ├── index.html             # Landing page with live feed & 3D starfield
│   ├── simulator.html         # Impact simulator, comparison modal & ARIA chat
│   └── dashboard.html         # Live tracking dashboard with GIS map & charts
└── static/
    ├── css/                   # Responsive sci-fi stylesheets
    └── js/                    # Interactive Leaflet maps, simulator UI & Chart.js
```

---

## 📄 License

This project is licensed under the **MIT License**.  
Orbital and astronomical telemetry provided by the [NASA Near-Earth Object Program](https://cneos.jpl.nasa.gov/).
