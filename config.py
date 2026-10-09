import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # NASA API
    NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    NASA_NEO_API = 'https://api.nasa.gov/neo/rest/v1'
    NASA_SENTRY_API = 'https://cneos.jpl.nasa.gov/sentry/details.html'
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'asteroid-defense-system-2025')
    DEBUG = False
    
    # Simulation parameters
    MAX_ASTEROID_SIZE = 2000  # meters
    MIN_ASTEROID_SIZE = 10    # meters
    MAX_VELOCITY = 72         # km/s
    MIN_VELOCITY = 5          # km/s
    
    # Real-time tracking
    TRACKING_INTERVAL = 21600  # 6 hours in seconds
    CACHE_DURATION = 3600      # 1 hour
    
    # Output directories
    OUTPUT_DIR = 'outputs'
    SIMULATION_DIR = os.path.join(OUTPUT_DIR, 'simulations')
    CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
    REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
