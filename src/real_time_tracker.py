import requests
import json
import time
import threading
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class RealTimeAsteroidTracker:
    def __init__(self):
        self.api_key = Config.NASA_API_KEY
        self.base_url = Config.NASA_NEO_API
        self.monitoring = False
        self.monitoring_thread = None
        self.callback_func = None
        
    def get_today_asteroids(self):
        """Get asteroids approaching today from NASA API"""
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/feed"
        params = {
            'start_date': today,
            'end_date': tomorrow,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            asteroids = []
            for date, objects in data.get('near_earth_objects', {}).items():
                for obj in objects:
                    asteroid = self.process_asteroid(obj)
                    asteroids.append(asteroid)
            
            return asteroids
            
        except Exception as e:
            logger.error(f"NASA API error: {e}")
            return self.get_fallback_asteroids()
    
    def process_asteroid(self, raw_data):
        """Process raw NASA asteroid data"""
        try:
            approach = raw_data.get('close_approach_data', [{}])[0]
            diameter = raw_data.get('estimated_diameter', {}).get('kilometers', {})
            
            return {
                'id': raw_data.get('id', ''),
                'name': raw_data.get('name', 'Unknown'),
                'designation': raw_data.get('designation', ''),
                'is_hazardous': raw_data.get('is_potentially_hazardous_asteroid', False),
                'diameter_min_m': diameter.get('estimated_diameter_min', 0) * 1000,
                'diameter_max_m': diameter.get('estimated_diameter_max', 0) * 1000,
                'velocity_km_s': float(approach.get('relative_velocity', {}).get('kilometers_per_second', 0)),
                'miss_distance_km': float(approach.get('miss_distance', {}).get('kilometers', 0)),
                'approach_date': approach.get('close_approach_date', ''),
                'nasa_url': raw_data.get('nasa_jpl_url', '')
            }
        except Exception as e:
            logger.error(f"Error processing asteroid: {e}")
            return None
    
    def get_fallback_asteroids(self):
        """Fallback data when NASA API is unavailable"""
        return [
            {
                'id': 'demo_1',
                'name': '(2025 AA) Demo Asteroid',
                'designation': '2025 AA',
                'is_hazardous': False,
                'diameter_min_m': 80,
                'diameter_max_m': 150,
                'velocity_km_s': 18.2,
                'miss_distance_km': 580000,
                'approach_date': datetime.now().strftime('%Y-%m-%d'),
                'nasa_url': '',
                'fallback': True
            }
        ]
    
    def get_sentry_objects(self):
        """Get NASA Sentry risk objects (simulated)"""
        return {
            "sentry_objects": [
                {
                    "designation": "29075 (1950 DA)",
                    "year_range_max": 2880,
                    "impact_probability": "0.00033",
                    "palermo_scale_max": "-1.42",
                    "torino_scale": "1",
                    "estimated_diameter": 1100
                },
                {
                    "designation": "101955 Bennu",
                    "year_range_max": 2300,
                    "impact_probability": "0.00024", 
                    "palermo_scale_max": "-1.70",
                    "torino_scale": "1",
                    "estimated_diameter": 492
                }
            ]
        }
    
    def start_real_time_monitoring(self, callback):
        """Start real-time monitoring in background thread"""
        self.callback_func = callback
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    asteroids = self.get_today_asteroids()
                    sentry_data = self.get_sentry_objects()
                    
                    update_data = {
                        'asteroids': asteroids,
                        'sentry_objects': sentry_data.get('sentry_objects', []),
                        'tracking_stats': {
                            'total_tracked': len(asteroids),
                            'hazardous_count': sum(1 for a in asteroids if a.get('is_hazardous')),
                            'today_count': len(asteroids),
                            'last_update': datetime.now().isoformat()
                        }
                    }
                    
                    if self.callback_func:
                        self.callback_func(update_data)
                    
                    logger.info(f"Monitored {len(asteroids)} asteroids")
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                
                # Wait for next update (6 hours)
                time.sleep(Config.TRACKING_INTERVAL)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        return self.monitoring_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
