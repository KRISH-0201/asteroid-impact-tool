# Python 3.13 Compatible - Advanced Atmospheric Entry Model
import numpy as np
import math
import json
from datetime import datetime

class AtmosphericEntryModel:
    def __init__(self):
        self.g0 = 9.81  # m/s²
        self.R = 287.0  # J/(kg·K) - specific gas constant for air
        
        # US Standard Atmosphere layers
        self.atmosphere_layers = [
            {'h_max': 11000, 'T0': 288.15, 'L': -0.0065, 'p0': 101325, 'name': 'Troposphere'},
            {'h_max': 20000, 'T0': 216.65, 'L': 0.0, 'p0': 22632, 'name': 'Tropopause'},
            {'h_max': 32000, 'T0': 216.65, 'L': 0.001, 'p0': 5474, 'name': 'Stratosphere'},
            {'h_max': 47000, 'T0': 228.65, 'L': 0.0028, 'p0': 868, 'name': 'Stratosphere'},
            {'h_max': 51000, 'T0': 270.65, 'L': 0.0, 'p0': 110, 'name': 'Stratopause'},
            {'h_max': 71000, 'T0': 270.65, 'L': -0.0028, 'p0': 66, 'name': 'Mesosphere'},
            {'h_max': 86000, 'T0': 214.65, 'L': -0.002, 'p0': 4, 'name': 'Mesosphere'},
        ]
        
        # Asteroid material properties
        self.material_properties = {
            'iron': {'strength': 10e6, 'heat_capacity': 450, 'melting_point': 1811},
            'stone': {'strength': 1e6, 'heat_capacity': 800, 'melting_point': 1473}, 
            'carbon': {'strength': 0.1e6, 'heat_capacity': 710, 'melting_point': 3823},
            'comet': {'strength': 0.01e6, 'heat_capacity': 2100, 'melting_point': 273}
        }
    
    def atmospheric_density(self, altitude):
        """Calculate atmospheric density using US Standard Atmosphere model"""
        if altitude <= 0:
            return 1.225  # Sea level density
        elif altitude > 86000:
            # Exponential decrease above 86km
            return 6.967e-9 * math.exp(-(altitude - 86000) / 8500)
        
        # Find appropriate atmospheric layer
        for i, layer in enumerate(self.atmosphere_layers):
            if altitude <= layer['h_max']:
                h_base = 0 if i == 0 else self.atmosphere_layers[i-1]['h_max']
                
                # Temperature calculation
                if layer['L'] == 0:  # Isothermal layer
                    T = layer['T0']
                else:  # Linear temperature variation
                    T = layer['T0'] + layer['L'] * (altitude - h_base)
                
                # Pressure calculation
                if layer['L'] == 0:
                    p = layer['p0'] * math.exp(-self.g0 * (altitude - h_base) / (self.R * T))
                else:
                    p = layer['p0'] * (T / layer['T0']) ** (-self.g0 / (self.R * layer['L']))
                
                # Density from ideal gas law
                density = p / (self.R * T)
                return density
        
        return 0  # Above atmosphere
    
    def drag_coefficient(self, mach_number, shape_factor=1.2):
        """Calculate drag coefficient based on Mach number and shape"""
        if mach_number < 0.8:
            return 0.3 * shape_factor
        elif mach_number < 1.2:
            # Transonic region with sharp increase
            return (0.3 + 0.5 * (mach_number - 0.8) / 0.4) * shape_factor
        else:
            # Supersonic/hypersonic with gradual decrease
            return (0.8 + 0.2 / mach_number) * shape_factor
    
    def heat_transfer_rate(self, velocity, density, radius):
        """Calculate heating rate using Sutton-Graves equation (W/m²)"""
        if velocity < 1000:  # Below significant heating threshold
            return 0
        return 1.74e-4 * math.sqrt(density / radius) * (velocity ** 3)
    
    def simulate_entry(self, initial_conditions):
        """
        Advanced atmospheric entry simulation using numerical integration
        initial_conditions: dict with keys 'altitude', 'velocity', 'mass', 'radius', 'angle', 'type'
        """
        # Extract initial conditions
        alt = float(initial_conditions['altitude'])  # meters
        vel = float(initial_conditions['velocity'])  # m/s
        mass = float(initial_conditions['mass'])     # kg
        radius = float(initial_conditions['radius']) # meters
        angle = math.radians(float(initial_conditions.get('angle', 45)))  # radians
        asteroid_type = initial_conditions.get('type', 'stone')
        
        # Material properties
        material = self.material_properties.get(asteroid_type, self.material_properties['stone'])
        
        # Storage arrays
        time_array = []
        altitude_array = []
        velocity_array = []
        mass_array = []
        temperature_array = []
        mach_array = []
        
        # Integration parameters
        dt = 0.1  # Time step (seconds) - smaller for accuracy
        t = 0
        max_time = 600  # 10 minutes maximum
        
        # Initial values
        temperature = 300  # K, initial temperature
        
        while alt > 0 and mass > 0 and t < max_time and vel > 0:
            # Atmospheric properties
            rho = self.atmospheric_density(alt)
            
            if rho == 0:  # Above atmosphere
                # Free fall in vacuum
                alt_change = -vel * math.sin(angle) * dt
                vel_change = -self.g0 * math.sin(angle) * dt
            else:
                # Calculate aerodynamic properties
                area = math.pi * radius**2
                sound_speed = 343  # Approximate sound speed at altitude
                mach = vel / sound_speed
                cd = self.drag_coefficient(mach)
                
                # Forces
                drag_force = 0.5 * rho * vel**2 * area * cd
                gravity_force = mass * self.g0
                
                # Equations of motion (simplified Euler integration)
                drag_accel = drag_force / mass
                gravity_accel = self.g0 * math.sin(angle)
                
                # Velocity change
                vel_change = -(drag_accel + gravity_accel) * dt
                
                # Altitude change  
                alt_change = -vel * math.sin(angle) * dt
                
                # Heating and ablation
                heat_flux = self.heat_transfer_rate(vel, rho, radius)
                
                # Temperature increase
                if heat_flux > 0:
                    heat_input = heat_flux * area * dt  # Joules
                    temp_increase = heat_input / (mass * material['heat_capacity'])
                    temperature += temp_increase
                
                # Mass loss due to ablation
                if temperature > material['melting_point']:
                    # Simplified ablation model
                    ablation_rate = heat_flux / 2.5e6  # kg/(m²·s)
                    mass_loss = ablation_rate * area * dt
                    mass = max(0, mass - mass_loss)
                    
                    # Radius decreases as mass is lost (assuming constant density)
                    if mass > 0:
                        volume = mass / 3000  # Assume 3000 kg/m³ average density
                        radius = ((3 * volume) / (4 * math.pi)) ** (1/3)
                
                # Check for catastrophic fragmentation
                dynamic_pressure = 0.5 * rho * vel**2
                if dynamic_pressure > material['strength']:
                    # Fragmentation occurs - simplified by rapid mass loss
                    mass *= 0.1  # 90% of mass lost to fragmentation
                    if mass < 1:  # Completely disintegrated
                        mass = 0
                        break
            
            # Update state variables
            vel += vel_change
            alt += alt_change
            
            # Ensure physical constraints
            vel = max(0, vel)  # Velocity can't be negative
            alt = max(0, alt)  # Altitude can't be negative
            
            # Store results
            time_array.append(t)
            altitude_array.append(alt)
            velocity_array.append(vel)
            mass_array.append(mass)
            temperature_array.append(temperature)
            mach_array.append(vel / 343)  # Approximate Mach number
            
            t += dt
        
        # Determine survival status
        survived = mass > 0 and alt <= 0
        impact_velocity = vel if survived else 0
        impact_mass = mass if survived else 0
        
        # Calculate energy retention
        initial_ke = 0.5 * initial_conditions['mass'] * (initial_conditions['velocity'] ** 2)
        final_ke = 0.5 * impact_mass * (impact_velocity ** 2)
        energy_retention = final_ke / initial_ke if initial_ke > 0 else 0
        
        return {
            'time': time_array,
            'altitude': altitude_array,
            'velocity': velocity_array,
            'mass': mass_array,
            'temperature': temperature_array,
            'mach_number': mach_array,
            'survived': survived,
            'impact_velocity': impact_velocity,
            'impact_mass': impact_mass,
            'energy_retention': energy_retention,
            'max_temperature': max(temperature_array) if temperature_array else 300,
            'fragmentation_altitude': None,  # Would need more complex model
            'atmospheric_effects': {
                'peak_heating_rate': max([self.heat_transfer_rate(v, self.atmospheric_density(a), radius) 
                                        for v, a in zip(velocity_array, altitude_array)]) if velocity_array else 0,
                'total_energy_dissipated': initial_ke - final_ke
            }
        }
    
    def fragmentation_model(self, initial_conditions):
        """
        Enhanced fragmentation analysis with multiple breakup events
        """
        trajectory = self.simulate_entry(initial_conditions)
        
        asteroid_type = initial_conditions.get('type', 'stone')
        material = self.material_properties.get(asteroid_type, self.material_properties['stone'])
        threshold = material['strength']
        
        fragments = []
        fragmentation_events = []
        
        # Analyze trajectory for fragmentation events
        for i, (alt, vel, mass) in enumerate(zip(
            trajectory['altitude'][:200],  # First 200 points
            trajectory['velocity'][:200],
            trajectory['mass'][:200]
        )):
            if mass <= 0:
                break
                
            rho = self.atmospheric_density(alt)
            dynamic_pressure = 0.5 * rho * vel**2
            
            if dynamic_pressure > threshold and mass > 100:  # Significant fragmentation
                # Calculate number of fragments based on energy
                fragment_count = min(15, max(2, int(math.log10(dynamic_pressure / threshold) * 3)))
                
                # Create fragments with size distribution
                fragment_masses = self.generate_fragment_distribution(mass, fragment_count)
                
                for j, frag_mass in enumerate(fragment_masses):
                    # Fragments get scattered velocities
                    vel_scatter = vel * (0.7 + 0.6 * np.random.random())
                    angle_scatter = initial_conditions.get('angle', 45) + np.random.uniform(-25, 25)
                    altitude_scatter = alt + np.random.uniform(-2000, 2000)
                    
                    fragment = {
                        'id': f"frag_{i}_{j}",
                        'mass': frag_mass,
                        'altitude': max(0, altitude_scatter),
                        'velocity': vel_scatter,
                        'angle': angle_scatter,
                        'fragmentation_time': trajectory['time'][i] if i < len(trajectory['time']) else 0
                    }
                    fragments.append(fragment)
                
                # Record fragmentation event
                fragmentation_events.append({
                    'altitude': alt,
                    'velocity': vel,
                    'dynamic_pressure': dynamic_pressure,
                    'fragments_created': fragment_count,
                    'time': trajectory['time'][i] if i < len(trajectory['time']) else 0
                })
                
                # Major fragmentation - stop looking for more
                if fragment_count > 5:
                    break
        
        return {
            'fragmented': len(fragments) > 0,
            'fragments': fragments,
            'fragmentation_events': fragmentation_events,
            'fragmentation_altitude': fragmentation_events[0]['altitude'] if fragmentation_events else None,
            'total_fragments': len(fragments),
            'largest_fragment_mass': max([f['mass'] for f in fragments]) if fragments else 0
        }
    
    def generate_fragment_distribution(self, total_mass, fragment_count):
        """Generate realistic fragment mass distribution"""
        # Power law distribution for fragment sizes
        fragments = []
        
        # Generate random sizes following power law
        sizes = np.random.power(2, fragment_count)  # Power law with exponent 2
        sizes = sizes / np.sum(sizes) * total_mass  # Normalize to total mass
        
        # Sort from largest to smallest
        sizes = np.sort(sizes)[::-1]
        
        return sizes.tolist()
    
    def calculate_airburst_effects(self, fragmentation_data):
        """Calculate effects of atmospheric airburst"""
        if not fragmentation_data['fragmented']:
            return {'airburst': False}
        
        # Find the major fragmentation event
        main_event = fragmentation_data['fragmentation_events'][0]
        
        # Estimate airburst energy (simplified)
        total_fragment_energy = sum([0.5 * f['mass'] * (f['velocity'] ** 2) 
                                   for f in fragmentation_data['fragments']])
        
        airburst_energy_mt = total_fragment_energy / 4.184e15  # Convert to megatons
        
        # Airburst effects are different from ground impact
        airburst_radius = 2.5 * (airburst_energy_mt ** 0.4)  # km
        
        return {
            'airburst': True,
            'airburst_altitude': main_event['altitude'],
            'airburst_energy_mt': airburst_energy_mt,
            'airburst_radius_km': airburst_radius,
            'overpressure_range_km': airburst_radius * 3,
            'thermal_range_km': airburst_radius * 2.5
        }
