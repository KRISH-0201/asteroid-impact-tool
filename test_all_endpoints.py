import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from app import app
import json

def run_tests():
    client = app.test_client()
    passed = 0
    total = 0

    def check(name, condition, extra=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f" PASS: {name} {extra}")
        else:
            print(f" FAIL: {name} {extra}")

    print("\n--- Testing UI Routes ---")
    r = client.get('/')
    check("GET / (Landing)", r.status_code == 200)

    r = client.get('/simulator')
    check("GET /simulator", r.status_code == 200)

    r = client.get('/dashboard')
    check("GET /dashboard", r.status_code == 200)

    print("\n--- Testing API Endpoints ---")
    r = client.get('/api/health')
    check("GET /api/health", r.status_code == 200 and r.json.get('status') == 'online')

    r = client.get('/api/presets')
    check("GET /api/presets", r.status_code == 200 and 'tunguska' in r.json.get('presets', {}))

    r = client.get('/api/stats/global')
    check("GET /api/stats/global", r.status_code == 200 and 'tracking_stats' in r.json)

    print("\n--- Testing /api/launch with Mitigation Strategies ---")
    payload = {
        'asteroid_type': 'stone',
        'diameter': 100,
        'speed': 17,
        'angle': 45,
        'latitude': 40.7128,
        'longitude': -74.0060,
        'mitigation_strategy': 'kinetic_impactor'
    }
    r = client.post('/api/launch', json=payload)
    check("POST /api/launch (kinetic_impactor)", r.status_code == 200 and 'impact_basic' in r.json)
    sim_data = r.json if r.status_code == 200 else {}
    if sim_data:
        print(f"   Energy: {sim_data.get('impact_basic', {}).get('energy_megatons')} MT")
        print(f"   Mitigation Outcome: {sim_data.get('mitigation_outcome')}")

    print("\n--- Testing ARIA AI Assistant (/api/ai/analyze) ---")
    ai_payload = {
        'question': 'How much energy does this impact release?',
        'simulation_data': sim_data
    }
    r = client.post('/api/ai/analyze', json=ai_payload)
    check("POST /api/ai/analyze (energy question)", r.status_code == 200 and 'Hiroshima' in r.json.get('response', ''))
    print(f"   ARIA: {r.json.get('response')[:80]}...")

    ai_payload_dart = {
        'question': 'What defense options exist against this asteroid?',
        'simulation_data': sim_data
    }
    r = client.post('/api/ai/analyze', json=ai_payload_dart)
    check("POST /api/ai/analyze (defense question)", r.status_code == 200 and len(r.json.get('response', '')) > 20)

    print("\n--- Testing Scenario Comparison (/api/compare) ---")
    compare_payload = {
        'scenario_a': {
            'asteroid_type': 'stone',
            'diameter': 50,
            'speed': 15,
            'angle': 45,
            'latitude': 40.7128,
            'longitude': -74.0060
        },
        'scenario_b': {
            'asteroid_type': 'iron',
            'diameter': 200,
            'speed': 25,
            'angle': 60,
            'latitude': 40.7128,
            'longitude': -74.0060
        }
    }
    r = client.post('/api/compare', json=compare_payload)
    check("POST /api/compare", r.status_code == 200 and 'winner_energy' in r.json.get('comparison', {}))
    if r.status_code == 200:
        c = r.json['comparison']
        print(f"   Winner Energy: Scenario {c.get('winner_energy').upper()}")

    print(f"\n==========================================")
    print(f"Total: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    print(f"==========================================")

if __name__ == '__main__':
    run_tests()
