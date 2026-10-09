import sys
import os
import json
import time
import math
from datetime import datetime
import numpy as np  # type: ignore

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Import core modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config  # type: ignore
from impact_calculator import ImpactCalculator  # type: ignore
from population_analyzer import PopulationAnalyzer  # type: ignore
from mitigation_solver import MitigationSolver  # type: ignore
from visualization import Visualizer  # type: ignore
from atmospheric_model import AtmosphericEntryModel  # type: ignore
from economic_impact import EconomicImpactCalculator  # type: ignore

class AsteroidLauncher:
    def __init__(self):
        self.calculator = ImpactCalculator()
        self.population = PopulationAnalyzer()
        self.mitigation = MitigationSolver()
        self.visualizer = Visualizer()
        self.atmospheric = AtmosphericEntryModel()
        self.economic = EconomicImpactCalculator()
        
        # Simulation history
        self.simulation_history = []
        self.active_simulations = {}
        
        # Enhanced physics constants
        self.TUNGUSKA_ENERGY = 15  # MT TNT equivalent
        self.CHICXULUB_ENERGY = 100e6  # MT TNT equivalent
        
        # Ensure output directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary output directories"""
        # Use absolute paths relative to the project root (parent of src/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        directories = [
            os.path.join(project_root, Config.SIMULATION_DIR),
            os.path.join(project_root, Config.REPORTS_DIR),
            os.path.join(project_root, Config.CHARTS_DIR),
            os.path.join(project_root, 'data', 'asteroids'),
            os.path.join(project_root, 'data', 'population'),
            os.path.join(project_root, 'data', 'geographical')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def launch_asteroid(self, asteroid_type, diameter, speed, angle, latitude, longitude, altitude=100):
        """Complete advanced asteroid impact simulation"""
        
        simulation_start = time.time()
        simulation_id = f"sim_{int(simulation_start)}_{hash(str([asteroid_type, diameter, speed, angle, latitude, longitude]))}"
        
        # Convert and validate parameters
        params = {
            'asteroid_type': str(asteroid_type).lower(),
            'diameter': float(diameter),
            'speed': float(speed),
            'angle': float(angle),
            'latitude': float(latitude),
            'longitude': float(longitude),
            'altitude': float(altitude)
        }
        
        # Parameter validation
        self.validate_parameters(params)
        
        # Initialize results structure (typed as dict to allow wider value types later)
        results: dict = {
            'simulation_id': simulation_id,
            'timestamp': int(simulation_start),
            'parameters': params,
            'computation_time': 0,
            'version': '2.0.0'
        }
        
        try:
            # Mark simulation as active
            self.active_simulations[simulation_id] = {
                'status': 'running',
                'start_time': simulation_start,
                'progress': 0
            }
            
            # 1. Basic Impact Physics
            self.update_simulation_progress(simulation_id, 20, "Calculating impact physics...")
            impact_data = self.calculator.calculate_impact(
                params['diameter'],
                params['speed'],
                params['latitude'],
                params['longitude'],
                params['angle'],
                params['asteroid_type']
            )
            results['impact_basic'] = impact_data
            
            # 2. Advanced Atmospheric Entry
            self.update_simulation_progress(simulation_id, 35, "Simulating atmospheric entry...")
            atmospheric_conditions = {
                'altitude': float(params['altitude']) * 1000,  # Convert to meters
                'velocity': float(params['speed']) * 1000,     # Convert to m/s
                'mass': impact_data['mass'],
                'radius': float(params['diameter']) / 2,
                'angle': float(params['angle']),
                'type': str(params['asteroid_type'])
            }
            
            entry_results = self.atmospheric.simulate_entry(atmospheric_conditions)
            fragmentation_results = self.atmospheric.fragmentation_model(atmospheric_conditions)
            
            results['atmospheric_entry'] = entry_results
            results['fragmentation'] = fragmentation_results
            
            # 3. Comprehensive Damage Analysis
            self.update_simulation_progress(simulation_id, 50, "Analyzing blast effects...")
            
            # Crater effects
            crater_data = self.calculator.calculate_enhanced_crater_effects(
                impact_data, params['latitude'], params['longitude']
            )
            
            # Fireball effects
            fireball_data = self.calculator.calculate_fireball_effects(
                impact_data['energy_megatons']
            )
            
            # Blast wave effects
            blast_data = self.calculator.calculate_blast_effects(
                impact_data['energy_megatons'], params['latitude'], params['longitude']
            )
            
            # Wind effects
            wind_data = self.calculator.calculate_wind_effects(
                impact_data['energy_megatons'], params['latitude'], params['longitude']
            )
            
            # Seismic effects
            earthquake_data = self.calculator.calculate_earthquake_effects(
                impact_data['energy_megatons'], params['latitude'], params['longitude']
            )
            
            # 4. Population Impact Analysis
            self.update_simulation_progress(simulation_id, 70, "Analyzing population effects...")
            population_data = self.population.analyze_comprehensive_impact(
                params['latitude'], params['longitude'], 
                crater_data, fireball_data, blast_data, wind_data, earthquake_data
            )
            
            # 5. Economic Impact Assessment
            self.update_simulation_progress(simulation_id, 85, "Calculating economic impact...")
            economic_data = self.economic.comprehensive_economic_analysis(
                impact_data, params['latitude'], params['longitude']
            )
            
            # 6. Mitigation Analysis
            self.update_simulation_progress(simulation_id, 95, "Evaluating mitigation options...")
            mitigation_data = self.mitigation.analyze_mitigation_options(
                params, impact_data, entry_results
            )
            
            # Compile comprehensive results
            results.update({
                'crater': crater_data,
                'fireball': fireball_data,
                'shockwave': blast_data,
                'winds': wind_data,
                'earthquake': earthquake_data,
                'population_effects': population_data,
                'economic_impact': economic_data,
                'mitigation_options': mitigation_data,
                'impact_location': {
                    'latitude': params['latitude'],
                    'longitude': params['longitude']
                }
            })
            
            # Add comparative analysis and visualization data
            results['comparative_analysis'] = self.generate_comparative_analysis(results)
            results['visualization_data'] = self.prepare_visualization_data(results)
            
            # Finalize simulation
            computation_time = time.time() - simulation_start
            results['computation_time'] = int(float(computation_time) * 1000) / 1000.0
            
            self.update_simulation_progress(simulation_id, 100, "Simulation complete")
            self.active_simulations[simulation_id]['status'] = 'completed'
            self.active_simulations[simulation_id]['end_time'] = time.time()
            
            # Save results
            self.save_simulation_results(results)
            
            # Add to history
            self.simulation_history.append({
                'id': simulation_id,
                'timestamp': simulation_start,
                'parameters': params,
                'energy_mt': impact_data['energy_megatons'],
                'total_deaths': self.calculate_total_deaths(results)
            })
            
            return results
            
        except Exception as e:
            # Handle simulation error
            self.active_simulations[simulation_id]['status'] = 'error'
            self.active_simulations[simulation_id]['error'] = str(e)
            raise Exception(f"Simulation failed: {e}")
    
    def validate_parameters(self, params):
        """Validate simulation parameters"""
        if not (10 <= params['diameter'] <= 2000):
            raise ValueError("Asteroid diameter must be between 10m and 2000m")
        
        if not (5 <= params['speed'] <= 72):
            raise ValueError("Impact speed must be between 5 and 72 km/s")
        
        if not (15 <= params['angle'] <= 90):
            raise ValueError("Impact angle must be between 15° and 90°")
        
        if not (-90 <= params['latitude'] <= 90):
            raise ValueError("Latitude must be between -90° and 90°")
        
        if not (-180 <= params['longitude'] <= 180):
            raise ValueError("Longitude must be between -180° and 180°")
        
        if params['asteroid_type'] not in ['iron', 'stone', 'carbon', 'comet']:
            raise ValueError("Asteroid type must be iron, stone, carbon, or comet")
    
    def update_simulation_progress(self, simulation_id, progress, status):
        """Update simulation progress"""
        if simulation_id in self.active_simulations:
            self.active_simulations[simulation_id]['progress'] = progress
            self.active_simulations[simulation_id]['status_message'] = status
    
    def generate_comparative_analysis(self, results):
        """Generate comparative analysis with historical events"""
        energy_mt = results['impact_basic']['energy_megatons']
        
        comparisons = {
            'historical_events': [],
            'nuclear_weapons': [],
            'natural_disasters': [],
            'extinction_events': []
        }
        
        # Historical impact events
        if energy_mt >= 15:
            tunguska_multiple = energy_mt / self.TUNGUSKA_ENERGY
            comparisons['historical_events'].append({
                'event': 'Tunguska Event (1908)',
                'comparison': f"{tunguska_multiple:.1f}x more powerful",
                'description': 'Siberian explosion that flattened 2,000 km² of forest'
            })
        
        if energy_mt >= 100e6:
            chicxulub_fraction = energy_mt / self.CHICXULUB_ENERGY
            comparisons['extinction_events'].append({
                'event': 'Chicxulub Impact (66 MYA)',
                'comparison': f"{chicxulub_fraction:.3f}x the energy",
                'description': 'Impact that killed the dinosaurs'
            })
        
        # Nuclear weapons comparison
        hiroshima_energy = 0.015  # MT
        if energy_mt >= hiroshima_energy:
            hiroshima_multiple = energy_mt / hiroshima_energy
            comparisons['nuclear_weapons'].append({
                'weapon': 'Hiroshima bomb',
                'comparison': f"{hiroshima_multiple:.0f}x more powerful",
                'description': 'Little Boy atomic bomb (15 kilotons)'
            })
        
        tsar_bomba_energy = 50  # MT
        if energy_mt >= tsar_bomba_energy:
            tsar_multiple = energy_mt / tsar_bomba_energy
            comparisons['nuclear_weapons'].append({
                'weapon': 'Tsar Bomba',
                'comparison': f"{tsar_multiple:.1f}x more powerful",
                'description': 'Largest nuclear weapon ever detonated'
            })
        
        # Natural disasters
        total_deaths = self.calculate_total_deaths(results)
        
        if total_deaths >= 100000:
            comparisons['natural_disasters'].append({
                'disaster': 'Major earthquake',
                'comparison': f"Comparable to devastating earthquake",
                'description': f"Estimated {total_deaths:,} casualties"
            })
        
        return comparisons
    
    def calculate_total_deaths(self, results):
        """Calculate total estimated deaths from all effects"""
        total = 0
        
        if 'crater' in results:
            total += results['crater'].get('people_killed', 0)
        if 'fireball' in results:
            total += results['fireball'].get('deaths', 0)
        if 'shockwave' in results:
            total += results['shockwave'].get('deaths', 0)
        if 'winds' in results:
            total += results['winds'].get('deaths', 0)
        if 'earthquake' in results:
            total += results['earthquake'].get('deaths', 0)
        
        return int(total)
    
    def prepare_visualization_data(self, results):
        """Prepare data for map visualization"""
        lat = results['impact_location']['latitude']
        lon = results['impact_location']['longitude']
        
        zones = []
        
        # Crater zone
        if 'crater' in results:
            zones.append({
                'type': 'crater',
                'center': [lat, lon],
                'radius_km': results['crater'].get('diameter_km', 0) / 2,
                'color': '#ff0000',
                'opacity': 0.8,
                'label': 'Crater Zone'
            })
        
        # Fireball zone
        if 'fireball' in results:
            zones.append({
                'type': 'fireball',
                'center': [lat, lon],
                'radius_km': results['fireball'].get('radius_km', 0),
                'color': '#ff6600',
                'opacity': 0.6,
                'label': 'Fireball Zone'
            })
        
        # Blast zones
        if 'shockwave' in results:
            damage_zones = results['shockwave'].get('damage_zones', {})
            
            for zone_type, radius in damage_zones.items():
                if radius > 0:
                    zones.append({
                        'type': f'blast_{zone_type}',
                        'center': [lat, lon],
                        'radius_km': radius,
                        'color': self.get_zone_color(zone_type),
                        'opacity': 0.3,
                        'label': f'{zone_type.title()} Damage Zone'
                    })
        
        # Wind zone
        if 'winds' in results:
            zones.append({
                'type': 'wind',
                'center': [lat, lon],
                'radius_km': results['winds'].get('range_km', 0),
                'color': '#ffff00',
                'opacity': 0.2,
                'label': 'Wind Blast Zone'
            })
        
        return {
            'impact_point': [lat, lon],
            'damage_zones': zones,
            'total_affected_area': sum(math.pi * (zone['radius_km']**2) for zone in zones)
        }
    
    def get_zone_color(self, zone_type):
        """Get color for damage zone type"""
        colors = {
            'severe': '#ff0000',
            'moderate': '#ff6600',
            'light': '#ffaa00'
        }
        return colors.get(zone_type, '#cccccc')
    
    def save_simulation_results(self, results):
        """Save simulation results to file"""
        simulation_id = results['simulation_id']
        timestamp = results['timestamp']
        
        # Create filename
        filename = os.path.join(Config.SIMULATION_DIR, f"simulation_{simulation_id}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Simulation saved: {filename}")
            
            # Also save summary
            summary = {
                'id': simulation_id,
                'timestamp': timestamp,
                'parameters': results['parameters'],
                'energy_mt': results['impact_basic']['energy_megatons'],
                'crater_diameter_km': results['crater'].get('diameter_km', 0),
                'total_deaths': self.calculate_total_deaths(results),
                'computation_time': results['computation_time']
            }
            
            summary_file = os.path.join(Config.SIMULATION_DIR, f"summary_{simulation_id}.json")
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[WARN] Failed to save simulation: {e}")
    
    def generate_report(self, simulation_data):
        """Generate comprehensive PDF report"""
        # This would integrate with the visualization module
        # to create charts and maps, then compile into PDF
        return self.visualizer.generate_pdf_report(simulation_data)
    
    def get_simulation_status(self, simulation_id):
        """Get status of active simulation"""
        return self.active_simulations.get(simulation_id, {'status': 'not_found'})
    
    def get_simulation_history(self, limit=10):
        """Get recent simulation history"""
        history = list(sorted(self.simulation_history, key=lambda x: x['timestamp'], reverse=True))
        return history[:int(limit)]  # pyre-ignore[6]

# Command line interface
def main():
    """Enhanced console interface"""
    print("🚀 Advanced Asteroid Impact Simulator v2.0")
    print("=" * 60)
    
    launcher = AsteroidLauncher()
    
    # Interactive mode
    while True:
        print("\nSelect simulation mode:")
        print("1. Quick simulation (default parameters)")
        print("2. Custom simulation")
        print("3. Real asteroid simulation")
        print("4. View simulation history")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            # Quick simulation
            print("\n🎯 Running quick simulation...")
            results = launcher.launch_asteroid(
                asteroid_type='stone',
                diameter=100,
                speed=17,
                angle=45,
                latitude=40.7128,
                longitude=-74.0060
            )
            display_results_summary(results)
            
        elif choice == '2':
            # Custom simulation
            try:
                params = get_custom_parameters()
                print(f"\n🎯 Running custom simulation...")
                results = launcher.launch_asteroid(**params)
                display_results_summary(results)
            except Exception as e:
                print(f"❌ Simulation failed: {e}")
                
        elif choice == '3':
            # Real asteroid simulation
            print("\n🛰️ Feature coming soon: Real asteroid database integration")
            
        elif choice == '4':
            # Simulation history
            history = launcher.get_simulation_history()
            print(f"\n📊 Recent Simulations ({len(history)}):")
            for i, sim in enumerate(history):
                print(f"{i+1}. {sim['id']} - {sim['energy_mt']:.2f} MT - {sim['total_deaths']:,} deaths")
                
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

def get_custom_parameters():
    """Get custom simulation parameters from user"""
    print("\nEnter simulation parameters:")
    
    asteroid_type = input("Asteroid type (stone/iron/carbon/comet) [stone]: ").strip() or 'stone'
    diameter = float(input("Diameter in meters [100]: ") or 100)
    speed = float(input("Impact speed in km/s [17]: ") or 17)
    angle = float(input("Impact angle in degrees [45]: ") or 45)
    latitude = float(input("Latitude [-90 to 90] [40.7128]: ") or 40.7128)
    longitude = float(input("Longitude [-180 to 180] [-74.0060]: ") or -74.0060)
    
    return {
        'asteroid_type': asteroid_type,
        'diameter': diameter,
        'speed': speed,
        'angle': angle,
        'latitude': latitude,
        'longitude': longitude
    }

def display_results_summary(results):
    """Display simulation results summary"""
    print("\n" + "="*60)
    print("💥 SIMULATION RESULTS")
    print("="*60)
    
    # Basic info
    energy_mt = results['impact_basic']['energy_megatons']
    total_deaths = results.get('crater', {}).get('people_killed', 0) + \
                  results.get('fireball', {}).get('deaths', 0) + \
                  results.get('shockwave', {}).get('deaths', 0)
    
    print(f"\n⚡ Impact Energy: {energy_mt:.2f} megatons TNT")
    print(f"🕳️  Crater Diameter: {results.get('crater', {}).get('diameter_km', 0):.2f} km")
    print(f"🔥 Fireball Radius: {results.get('fireball', {}).get('radius_km', 0):.2f} km")
    print(f"💥 Blast Range: {results.get('shockwave', {}).get('max_range_km', 0):.2f} km")
    print(f"💀 Estimated Deaths: {total_deaths:,}")
    print(f"⏱️  Computation Time: {results.get('computation_time', 0):.2f} seconds")
    
    # Comparisons
    if 'comparative_analysis' in results:
        comparisons = results['comparative_analysis']
        if comparisons['historical_events']:
            print(f"\n📊 Historical Comparison:")
            for event in comparisons['historical_events']:
                print(f"   {event['event']}: {event['comparison']}")

if __name__ == "__main__":
    main()
