import math
import numpy as np
from config import Config

class ImpactCalculator:
    def __init__(self):
        self.config = Config()
        
        # Asteroid density by type (kg/m³)
        self.densities = {
            'iron': 7800,
            'stone': 3000, 
            'carbon': 2000,
            'comet': 500
        }
    
    def calculate_impact(self, diameter, speed, lat, lon, angle=45, asteroid_type='stone'):
        """Calculate comprehensive impact effects Neal.fun style"""
        
        # Get density based on type
        density = self.densities.get(asteroid_type, 3000)
        
        # Calculate mass
        radius = diameter / 2
        volume = (4/3) * math.pi * (radius ** 3)
        mass = volume * density
        
        # Kinetic energy
        speed_ms = speed * 1000
        kinetic_energy = 0.5 * mass * (speed_ms ** 2)
        energy_megatons = kinetic_energy / (4.184e15)
        
        # Crater calculation (enhanced)
        crater_radius = self.calculate_crater_size(diameter, speed, angle, density)
        
        # Atmospheric effects
        atmospheric_factor = self.calculate_atmospheric_factor(diameter, speed, angle, density)
        
        return {
            'mass': mass,
            'kinetic_energy': kinetic_energy,
            'energy_megatons': energy_megatons,
            'crater_radius': crater_radius,
            'affected_area': math.pi * (crater_radius ** 2),
            'asteroid_type': asteroid_type,
            'atmospheric_factor': atmospheric_factor,
            'impact_location': {'lat': lat, 'lon': lon}
        }
    
    def calculate_crater_size(self, diameter, speed, angle, density):
        """Enhanced crater calculation"""
        # Holsapple scaling law with angle correction
        gravity = 9.81
        target_density = 2500  # Average rock density
        
        angle_factor = math.sin(math.radians(angle)) ** (1/3)
        
        crater_radius = 1.161 * ((density/target_density) ** 0.167) * \
                       ((speed * 1000) ** 0.333) * \
                       (diameter ** 0.333) * \
                       angle_factor / (gravity ** 0.167)
        
        return crater_radius / 1000  # Convert to km
    
    def calculate_enhanced_crater_effects(self, impact_data, lat, lon):
        """Return detailed crater effects dict expected by main.py and population_analyzer"""
        crater_radius_km = impact_data.get('crater_radius', 0)
        crater_diameter_km = crater_radius_km * 2
        energy_mt = impact_data.get('energy_megatons', 0)
        
        # Estimated people inside crater zone (realistic avg global density ~60/km²)
        crater_area = math.pi * (crater_radius_km ** 2)
        people_killed = int(crater_area * 60)  # conservative global average
        
        return {
            'radius_km': crater_radius_km,
            'diameter_km': crater_diameter_km,
            'depth_km': crater_radius_km * 0.2,
            'area_km2': crater_area,
            'people_killed': people_killed,
            'energy_mt': energy_mt,
            'description': f'Crater diameter: {crater_diameter_km:.2f} km'
        }
    
    def calculate_atmospheric_factor(self, diameter, speed, angle, density):
        """Calculate atmospheric breakup factor"""
        # Objects smaller than ~20m often break up in atmosphere
        if diameter < 20:
            breakup_factor = 0.3 + 0.7 * (diameter / 20)
        else:
            breakup_factor = 1.0
            
        return breakup_factor
    
    def calculate_fireball_effects(self, energy_megatons):
        """Calculate fireball effects Neal.fun style"""
        
        # Fireball radius (km) based on energy
        fireball_radius = 0.5 * (energy_megatons ** 0.4)
        
        # Temperature and thermal radiation
        thermal_radius = 2.5 * (energy_megatons ** 0.33)
        
        # Estimate deaths in fireball zone
        # Using ~8,000 people/km² as a realistic global average for populated areas
        fireball_deaths = int(fireball_radius ** 2 * math.pi * 8000)
        
        return {
            'radius_km': fireball_radius,
            'thermal_radius_km': thermal_radius,
            'temperature_celsius': 3000 + energy_megatons * 100,
            'duration_seconds': 10 + energy_megatons * 2,
            'deaths': fireball_deaths
        }
    
    def calculate_blast_effects(self, energy_megatons, lat, lon):
        """Calculate shockwave/blast effects"""
        
        # Blast pressure at different distances
        distances = [1, 5, 10, 25, 50, 100, 200]
        max_range = 20 * (energy_megatons ** 0.33)
        
        # Peak overpressure (psi) at 1 km
        peak_pressure = 50 * (energy_megatons ** 0.33)
        
        blast_deaths = int(max_range ** 2 * math.pi * 8000)  # Estimate with realistic density
        
        # Damage zone radii (required by population_analyzer.py)
        damage_zones = {
            'severe': max_range * 0.3,
            'moderate': max_range * 0.6,
            'light': max_range
        }
        
        return {
            'max_range_km': max_range,
            'pressure_psi': peak_pressure,
            'deaths': blast_deaths,
            'damage_radius_km': max_range * 0.7,
            'damage_zones': damage_zones
        }
    
    def calculate_wind_effects(self, energy_megatons, lat, lon):
        """Calculate wind blast effects"""
        
        # Wind speed based on energy
        max_wind_speed = 200 * (energy_megatons ** 0.25)  # km/h
        wind_range = 15 * (energy_megatons ** 0.33)
        
        wind_deaths = int(wind_range ** 2 * math.pi * 8000)  # Estimate with realistic density
        
        return {
            'max_speed_kmh': max_wind_speed,
            'range_km': wind_range,
            'deaths': wind_deaths,
            'tornado_equivalent': 'EF5' if max_wind_speed > 300 else 'EF4'
        }
    
    def calculate_earthquake_effects(self, energy_megatons, lat, lon):
        """Calculate seismic effects"""
        
        # Earthquake magnitude based on energy
        magnitude = 4.0 + 0.8 * math.log10(energy_megatons + 1)
        
        # Range where earthquake can be felt
        felt_range = 50 * (magnitude - 3) if magnitude > 3 else 0
        
        earthquake_deaths = int(magnitude ** 3 * 1000) if magnitude > 6 else 0
        
        return {
            'magnitude': magnitude,
            'range_km': felt_range,
            'deaths': earthquake_deaths,
            'richter_scale': magnitude
        }
