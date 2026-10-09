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
    q = question.lower()
    
    if sim_data:
        energy = float(sim_data.get('impact_basic', {}).get('energy_megatons', 0))
        crater = float(sim_data.get('crater', {}).get('diameter_km', 0))
        deaths = int(sim_data.get('crater', {}).get('people_killed', 0) + 
                    sim_data.get('fireball', {}).get('deaths', 0) +
                    sim_data.get('shockwave', {}).get('deaths', 0))
        
        if any(w in q for w in ['energy', 'power', 'how big', 'how strong']):
            hiroshima = energy / 0.015
            return f"This impact released {energy:.2f} megatons of TNT — equivalent to {hiroshima:,.0f} Hiroshima atomic bombs. {'This is a catastrophic regional to global event.' if energy > 100 else 'This is a significant but survivable event for regions far from the impact.'}"
        
        if any(w in q for w in ['crater', 'hole', 'size']):
            return f"The impact would create a crater approximately {crater:.1f} km wide and {crater * 0.1:.1f} km deep. {'This is larger than most ancient craters we can see today.' if crater > 10 else 'A major geological feature visible from low orbit.'}"
        
        if any(w in q for w in ['death', 'kill', 'casualt', 'people', 'survive']):
            return f"The estimated death toll from all combined effects (crater, fireball, blast wave, winds, and earthquake) is approximately {deaths:,} people. This accounts for local population density and the range of each damage mechanism."
        
        if any(w in q for w in ['defend', 'stop', 'prevent', 'mitigat', 'deflect']):
            params = sim_data.get('parameters', {})
            d = float(params.get('diameter', 100))
            v = float(params.get('speed', 17))
            if d < 150:
                return f"For a {d:.0f}m asteroid at {v:.1f} km/s, a kinetic impactor (like NASA's DART mission) launched 10+ years in advance would be highly effective. Even a 1 cm/s velocity change accumulates to a full Earth radius of deflection over a decade."
            elif d < 1000:
                return f"A {d:.0f}m object is in the challenging range. Multiple kinetic impactors or a standoff nuclear explosion would be needed with decades of warning time. Detection is the critical first step."
            else:
                return f"A {d:.0f}m impactor is in the extinction-class range. No current technology can reliably deflect this on short notice. Decades of preparation and international coordination would be required. Evacuation of the impact zone may be the only near-term option."
    
    # General knowledge responses
    if any(w in q for w in ['tunguska']):
        return "The 1908 Tunguska event was a 60m asteroid airburst over Siberia releasing ~15 MT of energy. It flattened 2,150 km² of forest. No crater formed because the asteroid exploded at ~8-10km altitude. It remains the largest impact event in recorded history."
    
    if any(w in q for w in ['dart', 'dimorphos', 'kinetic']):
        return "NASA's DART mission (2022) successfully redirected the asteroid Dimorphos by crashing a spacecraft into it at 6.1 km/s. The moon's orbit around Didymos was shortened by 33 minutes — a proof-of-concept for planetary defense!"
    
    if any(w in q for w in ['apophis']):
        return "Apophis (99942) will make a historically close pass on April 13, 2029, coming within 38,000 km — closer than geostationary satellites. Probability of impact: essentially zero. Diameter: ~370m. Impact energy if it hit: ~1,150 MT."
    
    if any(w in q for w in ['chicxulub', 'dinosaur', 'extinction']):
        return "The Chicxulub impactor (66 million years ago) was ~10km wide, releasing ~100 million MT. It triggered global wildfires, an impact winter lasting years from dust and soot, acid rain, and the Cretaceous-Paleogene extinction killing ~75% of species."
    
    if any(w in q for w in ['probability', 'likely', 'risk', 'chance']):
        return "Impact probabilities: Tunguska-class (15 MT) every ~500-1,000 years; city-destroyer (500m+) every ~50,000 years; extinction-level (10km+) every ~100 million years. Only ~40% of objects >140m have been catalogued — discovery is the key challenge."
    
    if any(w in q for w in ['nasa', 'track', 'detect', 'monitor']):
        return "NASA's CNEOS tracks near-Earth objects using telescope networks (ATLAS, Pan-STARRS, Catalina). The Sentry system automatically computes impact probabilities for all known NEOs. The ESA Space Situational Awareness program and NELIOTA also contribute globally."
    
    return ("Great question! Asteroid impact science involves many interacting factors: the size determines mass, which with velocity gives kinetic energy. "
            "Energy determines crater size, fireball radius, and blast wave extent. Location determines casualties. "
            "Try running a simulation and I can give you specific insights! Key tip: doubling the diameter increases energy by ~8x.")


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
