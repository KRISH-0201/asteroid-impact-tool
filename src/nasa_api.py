import requests  # type: ignore
import json
import math
import time
from datetime import datetime, timedelta
from config import Config  # type: ignore
import logging

logger = logging.getLogger(__name__)

class NASADataFetcher:
    def __init__(self):
        self.api_key = Config.NASA_API_KEY
        self.base_url = Config.NASA_NEO_API
        self.session = requests.Session()
        self.cache = {}
        self.cache_timeout = Config.CACHE_DURATION
        
    def get_asteroids_by_date_range(self, start_date, end_date):
        """Fetch asteroids from NASA NEO API for date range"""
        cache_key = f"asteroids_{start_date}_{end_date}"
        
        # Check cache
        if self.is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        url = f"{self.base_url}/feed"
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'api_key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Process NEO data
            asteroids = []
            neo_data = data.get('near_earth_objects', {})
            
            for date, date_asteroids in neo_data.items():
                for asteroid in date_asteroids:
                    processed = self.process_asteroid_data(asteroid)
                    asteroids.append(processed)
            
            # Cache results
            self.cache[cache_key] = {
                'data': asteroids,
                'timestamp': time.time()
            }
            
            logger.info(f"Fetched {len(asteroids)} asteroids from NASA API")
            return asteroids
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NASA API request failed: {e}")
            return self.get_fallback_data()
        except Exception as e:
            logger.error(f"NASA API processing failed: {e}")
            return self.get_fallback_data()
    
    def process_asteroid_data(self, raw_data):
        """Process raw NASA asteroid data into standardized format"""
        try:
            # Basic information
            processed = {
                'id': raw_data['id'],
                'name': raw_data.get('name', 'Unknown'),
                'designation': raw_data.get('designation', ''),
                'nasa_jpl_url': raw_data.get('nasa_jpl_url', ''),
                'is_hazardous': raw_data.get('is_potentially_hazardous_asteroid', False),
                'absolute_magnitude': raw_data.get('absolute_magnitude_h', 0)
            }
            
            # Diameter estimates
            diameter_data = raw_data.get('estimated_diameter', {}).get('kilometers', {})
            processed['estimated_diameter_min'] = diameter_data.get('estimated_diameter_min', 0) * 1000  # Convert to meters
            processed['estimated_diameter_max'] = diameter_data.get('estimated_diameter_max', 0) * 1000
            processed['estimated_diameter_avg'] = (processed['estimated_diameter_min'] + processed['estimated_diameter_max']) / 2
            
            # Close approach data
            if raw_data.get('close_approach_data'):
                approach = raw_data['close_approach_data'][0]  # Most recent approach
                
                processed['close_approach'] = {
                    'date': approach.get('close_approach_date', ''),
                    'date_full': approach.get('close_approach_date_full', ''),
                    'epoch': approach.get('epoch_date_close_approach', 0),
                    'velocity_km_s': float(approach.get('relative_velocity', {}).get('kilometers_per_second', 0)),
                    'velocity_km_h': float(approach.get('relative_velocity', {}).get('kilometers_per_hour', 0)),
                    'miss_distance_km': float(approach.get('miss_distance', {}).get('kilometers', 0)),
                    'miss_distance_au': float(approach.get('miss_distance', {}).get('astronomical', 0)),
                    'miss_distance_lunar': float(approach.get('miss_distance', {}).get('lunar', 0)),
                    'orbiting_body': approach.get('orbiting_body', 'Earth')
                }
                
                # Calculate threat level
                processed['threat_level'] = self.calculate_threat_level(processed)
                
                # Add simulation readiness
                processed['simulation_ready'] = True
                processed['suggested_parameters'] = {
                    'diameter': processed['estimated_diameter_avg'],
                    'velocity': processed['close_approach']['velocity_km_s'],
                    'angle': 45,  # Default impact angle
                    'type': self.estimate_asteroid_type(processed)
                }
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing asteroid data: {e}")
            return None
    
    def calculate_threat_level(self, asteroid_data):
        """Calculate threat level based on size, velocity, and distance"""
        diameter = asteroid_data['estimated_diameter_avg']
        velocity = asteroid_data['close_approach']['velocity_km_s']
        miss_distance = asteroid_data['close_approach']['miss_distance_lunar']
        is_hazardous = asteroid_data['is_hazardous']
        
        # Threat scoring
        threat_score = 0
        
        # Size factor
        if diameter > 1000:  # > 1km
            threat_score += 50
        elif diameter > 500:
            threat_score += 30
        elif diameter > 100:
            threat_score += 15
        elif diameter > 50:
            threat_score += 8
        else:
            threat_score += 2
        
        # Velocity factor
        if velocity > 50:
            threat_score += 20
        elif velocity > 30:
            threat_score += 15
        elif velocity > 20:
            threat_score += 10
        else:
            threat_score += 5
        
        # Distance factor (closer = more threatening)
        if miss_distance < 1:  # Less than 1 lunar distance
            threat_score += 30
        elif miss_distance < 5:
            threat_score += 20
        elif miss_distance < 20:
            threat_score += 10
        else:
            threat_score += 0
        
        # Hazardous designation
        if is_hazardous:
            threat_score += 25
        
        # Convert to threat level
        if threat_score >= 80:
            return "EXTREME"
        elif threat_score >= 60:
            return "HIGH"
        elif threat_score >= 40:
            return "MODERATE"
        elif threat_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def estimate_asteroid_type(self, asteroid_data):
        """Estimate asteroid composition based on available data"""
        diameter = asteroid_data['estimated_diameter_avg']
        absolute_magnitude = asteroid_data['absolute_magnitude']
        
        # Simple estimation based on size and brightness
        if diameter > 1000:
            return 'stone'  # Large asteroids are typically stony
        elif absolute_magnitude < 18 and diameter < 100:
            return 'iron'   # Small, bright objects might be metallic
        elif diameter < 50:
            return 'carbon' # Small, dark objects
        else:
            return 'stone'  # Default
    
    def get_asteroid_details(self, asteroid_id):
        """Get detailed information for specific asteroid"""
        cache_key = f"asteroid_details_{asteroid_id}"
        
        if self.is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        url = f"{self.base_url}/neo/{asteroid_id}"
        params = {'api_key': self.api_key}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            detailed = self.process_asteroid_data(data)
            
            # Add additional details
            detailed['orbital_data'] = data.get('orbital_data', {})
            detailed['close_approach_history'] = data.get('close_approach_data', [])
            
            # Cache results
            self.cache[cache_key] = {
                'data': detailed,
                'timestamp': time.time()
            }
            
            return detailed
            
        except Exception as e:
            logger.error(f"Failed to fetch asteroid details: {e}")
            raise
    
    def get_sentry_objects(self):
        """Get NASA Sentry risk objects (simulated for now)"""
        # Note: NASA doesn't have a public Sentry API, so we simulate this
        sentry_objects = [
            {
                'designation': '29075 (1950 DA)',
                'year_range_max': 2880,
                'impact_probability': '0.00033',
                'palermo_scale_max': '-1.42',
                'torino_scale': '1',
                'estimated_diameter': 1100,
                'potential_impacts': 51,
                'threat_level': 'MODERATE'
            },
            {
                'designation': '101955 Bennu',
                'year_range_max': 2300,
                'impact_probability': '0.00024',
                'palermo_scale_max': '-1.70',
                'torino_scale': '1',
                'estimated_diameter': 492,
                'potential_impacts': 78,
                'threat_level': 'MODERATE'
            },
            {
                'designation': '99942 Apophis',
                'year_range_max': 2068,
                'impact_probability': '0.00002',
                'palermo_scale_max': '-3.22',
                'torino_scale': '0',
                'estimated_diameter': 370,
                'potential_impacts': 12,
                'threat_level': 'LOW'
            }
        ]
        
        return sentry_objects
    
    def enhance_asteroid_data(self, asteroid):
        """Enhance asteroid data with additional calculated fields"""
        try:
            # Calculate impact energy estimate
            if asteroid.get('close_approach'):
                diameter_m = asteroid['estimated_diameter_avg']
                velocity_ms = asteroid['close_approach']['velocity_km_s'] * 1000
                
                # Assume stone asteroid density
                density = 3000  # kg/m³
                radius = diameter_m / 2
                volume = (4/3) * math.pi * (radius ** 3)
                mass = volume * density
                
                kinetic_energy = 0.5 * mass * (velocity_ms ** 2)
                energy_megatons = kinetic_energy / (4.184e15)  # Convert to MT TNT
                
                asteroid['impact_energy_mt'] = energy_megatons
                asteroid['mass_kg'] = mass
                
                # Add Tunguska comparison
                if energy_megatons > 15:
                    asteroid['tunguska_comparison'] = f"{energy_megatons/15:.1f}x Tunguska"
                else:
                    asteroid['tunguska_comparison'] = f"{energy_megatons/15:.2f}x Tunguska"
            
            return asteroid
            
        except Exception as e:
            logger.error(f"Error enhancing asteroid data: {e}")
            return asteroid
    
    def is_cached(self, cache_key):
        """Check if data is cached and not expired"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return (time.time() - cached_time) < self.cache_timeout
    
    def get_fallback_data(self):
        """Return fallback data when NASA API is unavailable"""
        return [
            {
                'id': 'fallback_1',
                'name': '(2025 AB) Demo Asteroid',
                'designation': '2025 AB',
                'is_hazardous': False,
                'estimated_diameter_min': 80,
                'estimated_diameter_max': 120,
                'estimated_diameter_avg': 100,
                'close_approach': {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'velocity_km_s': 17.2,
                    'miss_distance_km': 450000,
                    'miss_distance_lunar': 1.17
                },
                'threat_level': 'LOW',
                'simulation_ready': True,
                'fallback_data': True
            }
        ]
