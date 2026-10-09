from flask import Flask, request, jsonify, send_file, render_template  # type: ignore
from flask_cors import CORS  # type: ignore
import sys
import os
import json
import threading
import time
import hashlib
from datetime import datetime, timedelta
import logging

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src directory to path (absolute, so app works from any working directory)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import all modules
from config import Config  # type: ignore
from main import AsteroidLauncher  # type: ignore
from real_time_tracker import RealTimeAsteroidTracker  # type: ignore
from atmospheric_model import AtmosphericEntryModel  # type: ignore
from economic_impact import EconomicImpactCalculator  # type: ignore
from nasa_api import NASADataFetcher  # type: ignore
from mitigation_solver import MitigationSolver  # type: ignore
from usgs_api import USGSElevationAPI  # type: ignore
from risk_model import ThreatRiskModel  # type: ignore

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize all modules
launcher = AsteroidLauncher()
tracker = RealTimeAsteroidTracker()
atmospheric_model = AtmosphericEntryModel()
economic_calculator = EconomicImpactCalculator()
nasa_fetcher = NASADataFetcher()
mitigation_solver = MitigationSolver()
usgs_api = USGSElevationAPI()
risk_model = ThreatRiskModel()
# Global data stores - typed separately to avoid union-type inference issues
asteroids_data: list = []
sentry_data: list = []
tracking_stats: dict = {
    'total_tracked': 0,
    'hazardous_count': 0,
    'today_count': 0,
    'last_update': None
}
simulation_cache: dict = {}
active_simulations: list = []

def update_tracking_data(data):
    """Callback for real-time tracking updates"""
    global asteroids_data, sentry_data
    if 'asteroids' in data:
        asteroids_data = list(data['asteroids'])
    if 'sentry_objects' in data:
        sentry_data = list(data['sentry_objects'])
    tracking_stats['last_update'] = datetime.now().isoformat()
    logger.info(f"Updated tracking data: {len(data.get('asteroids', []))} asteroids")

# Initialize directories
for directory in [Config.SIMULATION_DIR, Config.CHARTS_DIR, Config.REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Frontend Routes
@app.route('/')
def route_index():
    return render_template('index.html')

@app.route('/simulator')
def route_simulator():
    return render_template('simulator.html')

@app.route('/dashboard')
def route_dashboard():
    return render_template('dashboard.html')

# API Routes
@app.route('/api/health')
def health_check():
    """Basic health check"""
    return jsonify({'status': 'online', 'system': 'Anti-Gravity Defense Platform API'})


@app.route('/api/launch', methods=['POST'])
def api_launch():
    """Advanced asteroid impact simulation API"""
    try:
        data = request.json or {}
        _hash: str = hashlib.sha256(str(data).encode()).hexdigest()
        simulation_id = f"sim_{int(time.time())}_{_hash[:12]}"  # pyre-ignore[6]
        
        # Validate input parameters
        params = {
            'asteroid_type': str(data.get('asteroid_type', 'stone')),
            'diameter': float(data.get('diameter', 100)),
            'speed': float(data.get('speed', 17)),
            'angle': float(data.get('angle', 45)),
            'latitude': float(data.get('latitude', 40.7128)),
            'longitude': float(data.get('longitude', -74.0060)),
            'altitude': float(data.get('altitude', 100))
        }
        
        # Parameter validation
        if not (Config.MIN_ASTEROID_SIZE <= params['diameter'] <= Config.MAX_ASTEROID_SIZE):
            return jsonify({'error': 'Invalid asteroid size'}), 400
        
        if not (Config.MIN_VELOCITY <= params['speed'] <= Config.MAX_VELOCITY):
            return jsonify({'error': 'Invalid velocity'}), 400
        
        # Check cache
        cache_key = str(sorted(params.items()))
        if cache_key in simulation_cache:
            cached_result = dict(simulation_cache[cache_key])
            cached_result['from_cache'] = True
            return jsonify(cached_result)
        
        # Add to active simulations
        active_simulations.append({
            'id': simulation_id,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'parameters': params
        })
        
        # Basic impact calculation
        results = launcher.launch_asteroid(**params)
        results['simulation_id'] = simulation_id
        
        # USGS Terrain Elevation
        elevation = usgs_api.get_elevation(params['latitude'], params['longitude'])
        
        # Apply anti-gravity mitigation strategies
        mitigation_strategy = data.get('mitigationStrategy') or data.get('mitigation_strategy') or 'none'
        results['impact_basic'], outcome_msg = mitigation_solver.apply_advanced_mitigation(
            mitigation_strategy, results['impact_basic'], params
        )
        results['mitigation_outcome'] = outcome_msg

        # AI Probabilistic Risk Assessment
        risk_data = risk_model.predict_risk(params['diameter'], params['speed'], 3000, elevation)
        results['risk_assessment'] = risk_data
        
        # Enhanced atmospheric entry simulation
        if data.get('atmospheric_model', True):
            _diameter = float(params['diameter'])
            _speed = float(params['speed'])
            _altitude = float(params['altitude'])
            _angle = float(params['angle'])
            atmospheric_conditions = {
                'altitude': _altitude * 1000,
                'velocity': _speed * 1000,
                'mass': results['impact_basic']['mass'],
                'radius': _diameter / 2,
                'angle': _angle,
                'type': str(params['asteroid_type'])
            }
            
            entry_results = atmospheric_model.simulate_entry(atmospheric_conditions)
            results['atmospheric_entry'] = entry_results
            
            # Fragmentation analysis
            if data.get('fragmentation_model', True):
                fragmentation_results = atmospheric_model.fragmentation_model(atmospheric_conditions)
                results['fragmentation'] = fragmentation_results
        
        # Economic impact analysis
        if data.get('economic_model', True):
            economic_results = economic_calculator.comprehensive_economic_analysis(
                results['impact_basic'], 
                params['latitude'], 
                params['longitude']
            )
            results['economic_impact'] = economic_results
        
        # Cache results
        simulation_cache[cache_key] = results
        
        # Update active simulations
        for sim in active_simulations:
            if isinstance(sim, dict) and sim.get('id') == simulation_id:
                sim['status'] = 'completed'
                sim['end_time'] = datetime.now().isoformat()
                break
        
        # Enhanced results with real-world context
        results['real_world_comparison'] = get_real_world_comparison(results)
        results['mitigation_options'] = get_mitigation_options(params, results)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nasa/live-feed')
def api_nasa_live_feed():
    """Live NASA asteroid data feed"""
    try:
        # Get today's asteroids
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        asteroids = nasa_fetcher.get_asteroids_by_date_range(today, tomorrow)
        
        # Process and enhance data
        enhanced_asteroids = []
        for asteroid in asteroids:
            enhanced = nasa_fetcher.enhance_asteroid_data(asteroid)
            enhanced_asteroids.append(enhanced)
        
        # Update global data
        global asteroids_data
        asteroids_data = enhanced_asteroids
        tracking_stats['total_tracked'] = len(enhanced_asteroids)
        tracking_stats['today_count'] = len(enhanced_asteroids)
        tracking_stats['hazardous_count'] = sum(1 for a in enhanced_asteroids if a.get('is_hazardous', False))
        
        return jsonify({
            'asteroids': enhanced_asteroids,
            'stats': tracking_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"NASA API error: {e}")
        return jsonify({'error': 'Failed to fetch NASA data', 'asteroids': []}), 500

@app.route('/api/nasa/sentry')
def api_nasa_sentry():
    """NASA Sentry risk assessment data"""
    try:
        global sentry_data
        sentry_objects = nasa_fetcher.get_sentry_objects()
        sentry_data = list(sentry_objects)
        
        return jsonify({
            'sentry_objects': sentry_objects,
            'risk_count': len(sentry_objects),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Sentry API error: {e}")
        return jsonify({'error': 'Failed to fetch Sentry data', 'sentry_objects': []}), 500

@app.route('/api/asteroid/<asteroid_id>')
def api_asteroid_details(asteroid_id):
    """Detailed information about specific asteroid"""
    try:
        details = nasa_fetcher.get_asteroid_details(asteroid_id)
        
        # Add simulation suggestions
        details['simulation_suggestions'] = generate_simulation_suggestions(details)
        
        return jsonify(details)
        
    except Exception as e:
        return jsonify({'error': f'Asteroid not found: {e}'}), 404

@app.route('/api/simulations/active')
def api_active_simulations():
    """Get currently active simulations"""
    return jsonify({
        'active_simulations': active_simulations,
        'total_simulations': len(simulation_cache),
        'cache_size': len(simulation_cache)
    })

@app.route('/api/export/simulation/<simulation_id>')
def api_export_simulation(simulation_id):
    """Export simulation results"""
    try:
        # Find simulation in cache
        simulation_data = None
        for cache_key in list(simulation_cache.keys()):
            cached_data = simulation_cache[cache_key]
            if isinstance(cached_data, dict) and cached_data.get('simulation_id') == simulation_id:
                simulation_data = cached_data
                break
        
        if not simulation_data:
            return jsonify({'error': 'Simulation not found'}), 404
        
        # Generate report
        report_path = launcher.generate_report(simulation_data)
        return send_file(report_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/global')
def api_global_stats():
    """Global asteroid tracking statistics"""
    return jsonify({
        'tracking_stats': tracking_stats,
        'system_status': {
            'nasa_api': 'online',
            'simulation_engine': 'online',
            'cache_size': len(simulation_cache),
            'uptime': get_uptime()
        },
        'recent_asteroids': list(asteroids_data)[:10]  # pyre-ignore[6]
    })

@app.route('/api/ai/analyze', methods=['POST'])
def api_ai_analyze():
    """ARIA AI analysis endpoint — returns context-aware insights for simulation data"""
    try:
        data = request.json or {}
        question = str(data.get('question', '')).strip()[:500]
        sim_data = data.get('simulation_data', {})
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        response = generate_aria_response(question, sim_data)
        return jsonify({
            'response': response,
            'assistant': 'ARIA',
            'version': '1.0'
        })
    except Exception as e:
        logger.error(f"AI endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare_scenarios():
    """Compare two asteroid impact scenarios side by side"""
    try:
        data = request.json or {}
        scenario_a = data.get('scenario_a', {})
        scenario_b = data.get('scenario_b', {})
        
        if not scenario_a or not scenario_b:
            return jsonify({'error': 'Two scenarios required'}), 400
        
        def run_scenario(params):
            p = {
                'asteroid_type': str(params.get('asteroid_type', 'stone')),
                'diameter': float(params.get('diameter', 100)),
                'speed': float(params.get('speed', 17)),
                'angle': float(params.get('angle', 45)),
                'latitude': float(params.get('latitude', 0)),
                'longitude': float(params.get('longitude', 0)),
                'altitude': float(params.get('altitude', 100))
            }
            return launcher.launch_asteroid(**p)
        
        results_a = run_scenario(scenario_a)
        results_b = run_scenario(scenario_b)
        
        def extract_summary(r):
            deaths = (r.get('crater', {}).get('people_killed', 0) +
                      r.get('fireball', {}).get('deaths', 0) +
                      r.get('shockwave', {}).get('deaths', 0) +
                      r.get('winds', {}).get('deaths', 0))
            return {
                'energy_megatons': r.get('impact_basic', {}).get('energy_megatons', 0),
                'crater_diameter_km': r.get('crater', {}).get('diameter_km', 0),
                'fireball_radius_km': r.get('fireball', {}).get('radius_km', 0),
                'blast_range_km': r.get('shockwave', {}).get('max_range_km', 0),
                'earthquake_magnitude': r.get('earthquake', {}).get('magnitude', 0),
                'total_deaths': deaths,
                'economic_impact_usd': r.get('economic_impact', {}).get('total_economic_impact_usd', 0),
                'ai_threat_pct': r.get('risk_assessment', {}).get('threat_level_pct', 0),
                'entry_mode': 'airburst' if not r.get('atmospheric_entry', {}).get('survived', True) else 'ground_impact'
            }
        
        return jsonify({
            'scenario_a': {
                'params': scenario_a,
                'results': results_a,
                'summary': extract_summary(results_a)
            },
            'scenario_b': {
                'params': scenario_b,
                'results': results_b,
                'summary': extract_summary(results_b)
            },
            'comparison': {
                'winner_energy': 'a' if extract_summary(results_a)['energy_megatons'] > extract_summary(results_b)['energy_megatons'] else 'b',
                'winner_deaths': 'a' if extract_summary(results_a)['total_deaths'] > extract_summary(results_b)['total_deaths'] else 'b',
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets')
def api_presets():
    """Return historical event preset parameters"""
    presets = {
        'chelyabinsk': {'asteroid_type': 'stone', 'diameter': 20, 'speed': 18, 'angle': 18, 'latitude': 55.15, 'longitude': 61.40, 'label': 'Chelyabinsk 2013', 'year': 2013, 'energy_mt': 0.5},
        'tunguska': {'asteroid_type': 'stone', 'diameter': 60, 'speed': 27, 'angle': 30, 'latitude': 60.89, 'longitude': 101.89, 'label': 'Tunguska 1908', 'year': 1908, 'energy_mt': 15},
        'barringer': {'asteroid_type': 'iron', 'diameter': 50, 'speed': 15, 'angle': 45, 'latitude': 35.027, 'longitude': -111.022, 'label': 'Barringer Crater', 'year': -50000, 'energy_mt': 10},
        'chicxulub': {'asteroid_type': 'stone', 'diameter': 10000, 'speed': 20, 'angle': 60, 'latitude': 21.40, 'longitude': -89.52, 'label': 'Chicxulub 66MYA', 'year': -66000000, 'energy_mt': 1e8},
        'city_killer': {'asteroid_type': 'stone', 'diameter': 500, 'speed': 17, 'angle': 45, 'latitude': 40.7128, 'longitude': -74.006, 'label': 'City Killer Class', 'year': None, 'energy_mt': 5000},
        'ocean_impact': {'asteroid_type': 'stone', 'diameter': 300, 'speed': 17, 'angle': 45, 'latitude': 30.0, 'longitude': -40.0, 'label': 'Ocean Impact', 'year': None, 'energy_mt': 700},
    }
    return jsonify({'presets': presets})

# Helper functions
def generate_aria_response(question: str, sim_data: dict) -> str:
    """Generate ARIA AI assistant response based on question and simulation context"""
    q = question.lower().strip()
    
    # 1. Greetings & Identity
    if any(q.startswith(w) or q == w for w in ['hi', 'hello', 'hey', 'greetings', 'who are you', 'what is aria', 'help', 'what can you do', 'good morning', 'good afternoon']):
        return (
            "Hello! I am <strong>ARIA</strong> (Asteroid Risk Intelligence Assistant), your planetary defense and impact physics advisor.<br><br>"
            "I can assist you with:<br>"
            "• <strong>Simulation Analysis</strong>: Ask about kinetic energy, crater diameter, casualties, blast radius, or economic losses for your simulation.<br>"
            "• <strong>Planetary Defense</strong>: Ask about NASA's DART kinetic impactor, gravity tractors, or nuclear deflection strategies.<br>"
            "• <strong>Impact Phenomena</strong>: Airbursts vs ground craters, thermal fireball burns, tsunamis, or seismic Richter magnitude.<br>"
            "• <strong>Known Asteroids</strong>: Apophis (2029 close pass), Bennu, Tunguska, Chelyabinsk, or the Chicxulub dinosaur extinction.<br>"
            "Try running a simulation and ask: <em>'Can we deflect this asteroid?'</em> or <em>'How many casualties would occur?'</em>"
        )
    
    # 2. Context-Aware Inquiries (Active Simulation Metrics)
    if sim_data and isinstance(sim_data, dict):
        impact_basic = sim_data.get('impact_basic', {})
        crater_data = sim_data.get('crater', {})
        fireball_data = sim_data.get('fireball', {})
        shockwave_data = sim_data.get('shockwave', {})
        winds_data = sim_data.get('winds', {})
        earthquake_data = sim_data.get('earthquake', {})
        economic_data = sim_data.get('economic_impact', {})
        params = sim_data.get('parameters', {})
        
        energy = float(impact_basic.get('energy_megatons', 0))
        crater_km = float(crater_data.get('diameter_km', 0))
        fireball_km = float(fireball_data.get('radius_km', 0))
        blast_km = float(shockwave_data.get('max_range_km', 0))
        winds_kmh = float(winds_data.get('max_speed_kmh', 0))
        magnitude = float(earthquake_data.get('magnitude', 0))
        deaths = int(crater_data.get('people_killed', 0) + fireball_data.get('deaths', 0) + shockwave_data.get('deaths', 0) + winds_data.get('deaths', 0))
        
        if any(w in q for w in ['energy', 'power', 'megaton', 'hiroshima', 'bomb', 'how big', 'how strong']):
            hiroshima = energy / 0.015 if energy > 0 else 0
            tsar = energy / 50.0 if energy > 0 else 0
            scale_desc = "an extinction-level global catastrophe" if energy >= 1e6 else \
                         "a continental-scale disaster" if energy >= 1000 else \
                         "a catastrophic regional event capable of obliterating an entire metropolitan area" if energy >= 100 else \
                         "a massive regional destruction event" if energy >= 1 else \
                         "a localized blast equivalent to a low-yield tactical nuclear detonation"
            return f"This impact releases <strong>{energy:,.2f} Megatons of TNT</strong> — equivalent to approximately <strong>{hiroshima:,.0f} Hiroshima atomic bombs</strong> (or {tsar:,.1f} Tsar Bombas). This classification is {scale_desc}."

        if any(w in q for w in ['crater', 'hole', 'depth', 'crater size', 'how deep']):
            if crater_km <= 0:
                return "Because of atmospheric drag and ram pressure, this asteroid disintegrated as an <strong>atmospheric airburst</strong> before reaching the surface. No ground crater was excavated, but extreme downwards blast overpressure occurs."
            return f"The ground impact would excavate a transient crater approximately <strong>{crater_km:.2f} km in diameter</strong> and roughly <strong>{(crater_km * 0.15):.2f} km deep</strong>. For comparison, Arizona's famous Barringer Meteor Crater is 1.2 km wide."

        if any(w in q for w in ['death', 'kill', 'casualt', 'people', 'survive', 'fatalit', 'how many died']):
            return (f"Estimated total casualty toll: <strong>{deaths:,} fatalities</strong>.<br>"
                    f"Breakdown: Crater ground zero ({crater_data.get('people_killed', 0):,} instant), "
                    f"thermal fireball radiation ({fireball_data.get('deaths', 0):,} severe burn fatalities), "
                    f"and shockwave overpressure / building collapse ({shockwave_data.get('deaths', 0):,} fatalities). "
                    f"Peak wind velocities reach {winds_kmh:.0f} km/h with an earthquake of M{magnitude:.1f}.")

        if any(w in q for w in ['fireball', 'thermal', 'burn', 'heat', 'radiation']):
            return f"The thermal radiation fireball reaches a maximum lethal radius of <strong>{fireball_km:.2f} km</strong>. Within this perimeter, thermal radiation flux causes immediate ignition of clothing, third-degree burns, and secondary urban firestorms."

        if any(w in q for w in ['shockwave', 'blast', 'wind', 'pressure', 'overpressure']):
            return f"The shockwave blast wave extends to a lethal range of <strong>{blast_km:.2f} km</strong> with peak ground wind gusts reaching <strong>{winds_kmh:.0f} km/h</strong>. Overpressure >5 psi will collapse multi-story concrete structures."

        if any(w in q for w in ['earthquake', 'seismic', 'richter', 'shaking', 'quake']):
            return f"The kinetic energy transferred into Earth's crust generates a seismic event of <strong>Magnitude {magnitude:.1f}</strong> on the Richter scale, detectable by global seismograph networks and causing severe structural collapse near the epicenter."

        if any(w in q for w in ['economic', 'money', 'cost', 'damage', 'gdp', 'dollar', 'loss']):
            tot_econ = economic_data.get('total_economic_impact_usd', 0)
            recov = economic_data.get('summary', {}).get('recovery_timeline_years', 0)
            return f"Estimated total economic destruction: <strong>${tot_econ:,.0f} USD</strong> with a projected infrastructure recovery timeline of <strong>{recov:.1f} years</strong>, disrupting regional commerce and global supply chains."

        if any(w in q for w in ['defend', 'stop', 'prevent', 'mitigat', 'deflect', 'save', 'dart', 'protect']):
            d = float(params.get('diameter', 100))
            v = float(params.get('speed', 17))
            if d <= 150:
                return f"For this <strong>{d:.0f}m</strong> asteroid traveling at {v:.1f} km/s, a <strong>Kinetic Impactor</strong> (similar to NASA's DART mission) launched 5–10 years prior to predicted impact achieves 100% mission success! A velocity delta (Δv) of only a few cm/s accumulates into a full Earth radius miss distance over orbital timescales."
            elif d <= 500:
                return f"This <strong>{d:.0f}m</strong> asteroid is in the 'City Killer' class. A single kinetic impactor is insufficient; multiple synchronized kinetic impactors or a <strong>Standoff Nuclear Detonation</strong> (using X-ray vaporization to vaporize the surface and create rocket-like thrust) would be required with 10–20 years warning time."
            else:
                return f"An asteroid of <strong>{d:.0f}m</strong> is in the continental/extinction category. Current technology cannot deflect this object without at least 30–50 years advance discovery. The primary planetary defense priority would be mass civil evacuation and underground shelter protocols."

    # 3. Defense Concepts
    if any(w in q for w in ['dart', 'dimorphos', 'didymos', 'kinetic impactor', 'kinetic']):
        return "NASA's <strong>DART</strong> (Double Asteroid Redirection Test) mission made history on September 26, 2022, by intentionally slamming a 570 kg spacecraft into the asteroid moonlet Dimorphos at 6.1 km/s. It shortened Dimorphos's orbital period by 33 minutes—proving humanity can deflect hazardous asteroids!"

    if any(w in q for w in ['gravity tractor', 'tractor']):
        return "A <strong>Gravity Tractor</strong> is a non-contact planetary defense spacecraft. By hovering close to an asteroid for months to years, its mutual gravitational attraction gently tugs the asteroid off its collision trajectory without risking fragmentation."

    if any(w in q for w in ['nuke', 'nuclear', 'standoff']):
        return "For large asteroids (>500m) discovered with short warning time, a <strong>Standoff Nuclear Detonation</strong> is the most viable option. Rather than blowing the asteroid apart (which creates dangerous shotgun fragments), the bomb detonates hundreds of meters away; intense X-ray and neutron flux vaporizes a thin surface layer, acting as a rocket exhaust that pushes the asteroid away."

    if any(w in q for w in ['evacuat', 'shelter', 'what to do', 'civil defense', 'prepare']):
        return "In an imminent asteroid impact scenario:<br>1. Evacuate the primary impact ground zero and tsunami inundation zones.<br>2. Move away from glass windows (the majority of Chelyabinsk injuries were caused by shattered window glass from the blast wave seconds after the visual flash).<br>3. Take shelter in reinforced interior rooms or underground basements."

    # 4. Impact Physics
    if any(w in q for w in ['tsunami', 'ocean impact', 'water impact', 'sea', 'ocean']):
        return "Ocean impacts generate towering initial water cavity waves hundreds of meters high. While deep-ocean waves lose energy through dispersion, as they approach continental shelves, they compress and inundate coastlines for thousands of kilometers, posing catastrophic risks to coastal population centers."

    if any(w in q for w in ['airburst', 'explode in air', 'break up', 'atmospheric entry']):
        return "An <strong>Airburst</strong> occurs when aerodynamic drag and dynamic ram pressure exceed the internal tensile strength of the incoming asteroid. The asteroid violently pancakes and fragments at high altitude (10–30 km), dumping its kinetic energy into the atmosphere in a blinding fireball and high-pressure shockwave (like Chelyabinsk and Tunguska)."

    if any(w in q for w in ['winter', 'impact winter', 'climate', 'dust', 'cooling']):
        return "An <strong>Impact Winter</strong> is triggered when asteroids >1km vaporize rock and eject millions of tons of sub-micron silicate dust, soot, and sulfur aerosols into the stratosphere. This blocks sunlight globally, halting photosynthesis and dropping global temperatures by 5–15°C for years, causing global agricultural collapse."

    if any(w in q for w in ['meteoroid', 'meteor', 'meteorite', 'comet', 'difference', 'what is an asteroid']):
        return "Astronomical distinctions:<br>• <strong>Asteroid</strong>: Rocky or metallic celestial body orbiting the Sun (mostly in the Asteroid Belt between Mars and Jupiter).<br>• <strong>Meteoroid</strong>: Small asteroid fragment in space.<br>• <strong>Meteor</strong>: The bright streak of light as a meteoroid burns up in Earth's atmosphere ('shooting star').<br>• <strong>Meteorite</strong>: Any space rock fragment that survives atmospheric entry and hits the ground.<br>• <strong>Comet</strong>: Icy body with volatile frozen gases from the outer solar system that develops a coma and tail."

    # 5. Famous Asteroids & History
    if any(w in q for w in ['apophis', '99942']):
        return "<strong>Apophis (99942)</strong> is a ~370-meter asteroid that will make a historically close flyby on <strong>April 13, 2029</strong>, passing within 31,600 km of Earth's surface—closer than geostationary weather satellites! NASA radar and optical observations have completely ruled out any impact in 2029 and for at least the next 100 years."

    if any(w in q for w in ['bennu', '101955', 'osiris']):
        return "<strong>Bennu (101955)</strong> is a ~500m carbonaceous asteroid visited by NASA's OSIRIS-REx mission, which returned pristine samples to Earth in 2023. Bennu currently has the highest cumulative impact probability on NASA's Sentry Risk Table for the late 22nd century (~1 in 1,750 chance around the year 2182)."

    if any(w in q for w in ['tunguska', '1908']):
        return "The <strong>1908 Tunguska Event</strong> occurred on June 30, 1908, when a ~50–60m stony asteroid exploded at an altitude of 5–10 km over Siberia, releasing ~12–15 Megatons of energy. It flattened 2,150 km² of Siberian forest (over 80 million trees) with no ground crater."

    if any(w in q for w in ['chelyabinsk', '2013']):
        return "The <strong>2013 Chelyabinsk Superbolide</strong> was a ~20m asteroid that entered undetected at 19 km/s over Russia, exploding at 30 km altitude with ~500 Kilotons of energy (30x Hiroshima). The blinding flash was followed 2–3 minutes later by a shockwave that injured ~1,500 people, primarily from flying window glass."

    if any(w in q for w in ['chicxulub', 'dinosaur', 'extinction', 'k-pg', '66 million']):
        return "The <strong>Chicxulub Impactor</strong> hit the Yucatán Peninsula 66 million years ago. It was approximately 10 to 14 km wide and released roughly <strong>100 million Megatons</strong> of kinetic energy. It triggered global megatsunamis, worldwide forest fires, acid rain, and an impact winter that wiped out 75% of all plant and animal species, including non-avian dinosaurs."

    if any(w in q for w in ['barringer', 'meteor crater', 'arizona']):
        return "<strong>Barringer Crater</strong> (Meteor Crater in Arizona) was created ~50,000 years ago by a 50-meter metallic iron-nickel asteroid traveling at ~12.8 km/s. Because of its dense iron composition, it survived atmospheric entry intact, carving a 1.2 km wide, 170-meter deep crater."

    # 6. Detection & Tracking
    if any(w in q for w in ['sentry', 'cneos', 'track', 'detect', 'telescope', 'find', 'atlas', 'pan-starrs', 'nasa']):
        return "NASA's <strong>Center for Near Earth Object Studies (CNEOS)</strong> and the automated <strong>Sentry System</strong> monitor near-Earth objects using ground telescopes (ATLAS, Pan-STARRS, Catalina Sky Survey) and Goldstone radar. Over 34,000 NEOs have been cataloged to date, with ~95% of asteroids larger than 1 km identified."

    if any(w in q for w in ['torino', 'palermo', 'scale']):
        return "The <strong>Torino Scale</strong> is a 0 to 10 integer rating for public communication: 0 indicates zero risk of collision, 1 is normal, and 8 to 10 represent certain collisions causing regional to global catastrophes. The <strong>Palermo Technical Scale</strong> is a logarithmic scale used by specialists to assess normalized impact risk against background hazard."

    # Default Intelligent Response
    return (
        f"Regarding your question about <em>'{question}'</em>:<br>"
        "Impact physics is governed by three primary variables: <strong>diameter</strong> (which dictates mass by M ∝ D³), "
        "<strong>density</strong> (iron, stone, carbonaceous, or cometary ice), and <strong>velocity</strong> (which scales kinetic energy by E = ½ M v²).<br><br>"
        "💡 <strong>Pro Tip</strong>: Adjust the parameter sliders on the left or select a historical preset (e.g., Chelyabinsk, Tunguska, or Chicxulub) and click <strong>Simulate Impact</strong> to see the exact blast zone, crater footprint, and planetary defense options calculated live!"
    )

def get_real_world_comparison(results):
    """Compare impact to real-world events"""
    energy_mt = results['impact_basic']['energy_megatons']
    
    comparisons = []
    
    if energy_mt < 0.001:
        comparisons.append("💥 Equivalent to a large conventional bomb")
    elif energy_mt < 0.015:
        comparisons.append("☢️ Similar to the Hiroshima atomic bomb (15 KT)")
    elif energy_mt < 1:
        comparisons.append("☢️ Comparable to the largest nuclear weapons ever tested")
    elif energy_mt < 15:
        comparisons.append("🌲 Similar to the Tunguska event (1908) — flattened 2,000 km² of Siberian forest")
    elif energy_mt < 500:
        comparisons.append("🏙️ Regional catastrophe — city-destroying blast radius")
    elif energy_mt < 10_000:
        comparisons.append("🌍 Country-scale devastation — comparable to multiple nuclear arsenals")
    elif energy_mt < 1_000_000:
        comparisons.append("🌏 Continental-scale devastation with global climate disruption")
    elif energy_mt < 100_000_000:
        comparisons.append("☄️ Chicxulub-class impact — extinction-level event (dinosaur killer was ~100M MT)")
    else:
        comparisons.append("💀 Civilization-ending impact — beyond any historical precedent")
    
    return comparisons

def get_mitigation_options(params, results):
    """Generate mitigation strategy options"""
    energy_mt = results['impact_basic']['energy_megatons']
    diameter = params['diameter']
    
    options = []
    
    if diameter < 50:
        options.append({
            'strategy': 'Atmospheric Breakup',
            'feasibility': 'High',
            'description': 'Small asteroid will likely break up naturally'
        })
    
    if energy_mt < 100:
        options.append({
            'strategy': 'Kinetic Impactor',
            'feasibility': 'High',
            'description': 'Deflection using spacecraft impact'
        })
        
        options.append({
            'strategy': 'Gravity Tractor',
            'feasibility': 'Medium',
            'description': 'Slow deflection using gravitational pull'
        })
    
    if energy_mt > 1:
        options.append({
            'strategy': 'Nuclear Deflection',
            'feasibility': 'Medium',
            'description': 'High-energy deflection for large objects'
        })
    
    options.append({
        'strategy': 'Evacuation',
        'feasibility': 'High',
        'description': 'Population evacuation from impact zone'
    })
    
    return options

def generate_simulation_suggestions(asteroid_details):
    """Generate simulation parameter suggestions based on real asteroid data"""
    suggestions = {
        'diameter': asteroid_details.get('estimated_diameter_max', 100),
        'speed': asteroid_details.get('velocity_km_s', 17),
        'angle': 45,  # Default
        'asteroid_type': 'stone'  # Default
    }
    
    # Estimate type based on size and other factors
    diameter = float(suggestions['diameter'])
    if diameter > 1000:
        suggestions['asteroid_type'] = 'stone'
    elif diameter < 50:
        suggestions['asteroid_type'] = 'iron'
    
    return suggestions

def get_uptime():
    """Calculate system uptime"""
    if not hasattr(get_uptime, 'start_time'):
        get_uptime.start_time = datetime.now()
    
    uptime = datetime.now() - get_uptime.start_time
    return str(uptime).split('.')[0]  # Remove microseconds

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Start real-time monitoring
try:
    monitoring_thread = tracker.start_real_time_monitoring(update_tracking_data)
    logger.info("✅ Real-time asteroid monitoring started")
except Exception as e:
    logger.error(f"⚠️ Monitoring failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting Advanced Asteroid Defense System...")
    logger.info("=" * 60)
    logger.info("🛰️  Real-time NASA API integration: ENABLED")
    logger.info("🌍 Advanced atmospheric modeling: ENABLED") 
    logger.info("💰 Economic impact analysis: ENABLED")
    logger.info("🛡️  Planetary defense planning: ENABLED")
    logger.info("=" * 60)
    logger.info("📊 Main Interface: http://localhost:5000")
    logger.info("🎮 Simulator: http://localhost:5000/simulator")
    logger.info("📈 Dashboard: http://localhost:5000/dashboard")
    logger.info("=" * 60)
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
