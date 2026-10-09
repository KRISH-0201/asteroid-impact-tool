"""
Advanced Asteroid Impact Simulator
A comprehensive tool for simulating asteroid impacts with real NASA data integration.

Author: Asteroid Defense Team
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Asteroid Defense Team"
__email__ = "contact@asteroiddefense.org"

# Import main modules
from .main import AsteroidLauncher
from .impact_calculator import ImpactCalculator  
from .population_analyzer import PopulationAnalyzer
from .mitigation_solver import MitigationSolver
from .visualization import Visualizer
from .real_time_tracker import RealTimeAsteroidTracker
from .atmospheric_model import AtmosphericEntryModel
from .economic_impact import EconomicImpactCalculator
from .nasa_api import NASADataFetcher

__all__ = [
    'AsteroidLauncher',
    'ImpactCalculator',
    'PopulationAnalyzer', 
    'MitigationSolver',
    'Visualizer',
    'RealTimeAsteroidTracker',
    'AtmosphericEntryModel',
    'EconomicImpactCalculator',
    'NASADataFetcher'
]
