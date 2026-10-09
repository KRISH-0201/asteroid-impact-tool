import folium  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config  # type: ignore

class Visualizer:
    def create_impact_map(self, lat, lon, crater_radius):
        """Create interactive map showing impact area"""
        
        # Create folium map
        impact_map = folium.Map(
            location=[lat, lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add impact center marker
        folium.Marker(
            [lat, lon],
            popup=f'Impact Center<br>Crater Radius: {crater_radius:.2f} km',
            tooltip='Impact Point',
            icon=folium.Icon(color='red', icon='exclamation-triangle')
        ).add_to(impact_map)
        
        # Add crater circle
        folium.Circle(
            [lat, lon],
            radius=crater_radius * 1000,  # Convert to meters
            popup=f'Crater Area ({crater_radius:.2f} km radius)',
            color='red',
            fillColor='red',
            fillOpacity=0.3
        ).add_to(impact_map)
        
        # Add damage zones
        damage_zones = [
            {'radius': crater_radius * 3, 'color': 'orange', 'name': 'Severe Damage'},
            {'radius': crater_radius * 5, 'color': 'yellow', 'name': 'Moderate Damage'},
            {'radius': crater_radius * 10, 'color': 'blue', 'name': 'Minor Effects'}
        ]
        
        for zone in damage_zones:
            folium.Circle(
                [lat, lon],
                radius=zone['radius'] * 1000,
                popup=f"{zone['name']} Zone ({zone['radius']:.2f} km)",
                color=zone['color'],
                fill=False,
                weight=2
            ).add_to(impact_map)
        
        # Save map
        impact_map.save('impact_visualization.html')
        print(f"Interactive map saved as 'impact_visualization.html'")
    
    def create_impact_chart(self, impact_data):
        """Create charts showing impact effects"""
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Energy comparison chart — correct reference values:
        # Hiroshima (Little Boy) = 0.015 MT, Tsar Bomba = 50 MT, Chicxulub ~100 million MT
        energies = [impact_data['energy_megatons'], 0.015, 50, 1e8]
        labels = ['This Impact', 'Hiroshima (0.015 MT)', 'Tsar Bomba (50 MT)', 'Chicxulub (~100M MT)']
        colors = ['red', 'orange', 'blue', 'purple']
        
        ax1.bar(labels, energies, color=colors)
        ax1.set_ylabel('Energy (Megatons)')
        ax1.set_title('Energy Comparison')
        ax1.set_yscale('log')
        
        # Damage zones pie chart
        zones = ['Direct Impact', 'Severe Damage', 'Moderate Damage', 'Minor Effects']
        areas = [
            np.pi * impact_data['crater_radius']**2,
            np.pi * (3 * impact_data['crater_radius'])**2,
            np.pi * (5 * impact_data['crater_radius'])**2,
            np.pi * (10 * impact_data['crater_radius'])**2
        ]
        
        ax2.pie(areas, labels=zones, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Damage Zone Areas')
        
        # Distance vs Effect
        distances = np.linspace(1, 100, 50)
        effects = impact_data['energy_megatons'] / (distances ** 2)
        
        ax3.plot(distances, effects)
        ax3.set_xlabel('Distance (km)')
        ax3.set_ylabel('Blast Pressure')
        ax3.set_title('Blast Effects vs Distance')
        ax3.set_yscale('log')
        
        # Population impact (dummy data)
        population_zones = ['Direct', 'Severe', 'Moderate', 'Minor']
        affected_pop = [100000, 500000, 1000000, 2000000]  # Dummy data
        
        ax4.bar(population_zones, affected_pop, color=['darkred', 'red', 'orange', 'yellow'])
        ax4.set_ylabel('Affected Population')
        ax4.set_title('Population Impact by Zone')
        
        plt.tight_layout()
        plt.savefig('impact_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_pdf_report(self, simulation_data):
        """
        Generate a simulation report saved to the configured REPORTS_DIR.
        Currently saves as a structured JSON report.
        Full PDF generation can be added with reportlab/weasyprint.
        """
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)
        
        simulation_id = simulation_data.get('simulation_id', 'unknown')
        report_filename = f"report_{simulation_id}.json"
        report_path = os.path.join(Config.REPORTS_DIR, report_filename)
        
        # Build a human-readable report summary
        report = {
            'report_type': 'Asteroid Impact Simulation Report',
            'simulation_id': simulation_id,
            'timestamp': simulation_data.get('timestamp'),
            'parameters': simulation_data.get('parameters', {}),
            'impact_energy_megatons': simulation_data.get('impact_basic', {}).get('energy_megatons', 0),
            'crater_diameter_km': simulation_data.get('crater', {}).get('diameter_km', 0),
            'fireball_radius_km': simulation_data.get('fireball', {}).get('radius_km', 0),
            'blast_range_km': simulation_data.get('shockwave', {}).get('max_range_km', 0),
            'economic_impact_usd': simulation_data.get('economic_impact', {}).get('total_economic_impact_usd', 0),
            'mitigation_options': simulation_data.get('mitigation_options', []),
            'computation_time_s': simulation_data.get('computation_time', 0)
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return report_path
