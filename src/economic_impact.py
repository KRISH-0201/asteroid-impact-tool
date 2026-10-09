# Advanced Economic Impact Calculator
import pandas as pd
import numpy as np
from datetime import datetime
import json
import math

class EconomicImpactCalculator:
    def __init__(self):
        # Global economic data (2025 estimates)
        self.global_gdp = 118e12  # $118 trillion USD (2025 estimate)
        self.earth_surface_area = 510.1e6  # km²
        self.ocean_coverage = 0.71
        self.land_area = self.earth_surface_area * (1 - self.ocean_coverage)
        
        # Economic density by region (GDP per km²)
        self.regional_economic_density = {
            'north_america': {'gdp_per_km2': 185000, 'infrastructure_multiplier': 8.5},
            'europe': {'gdp_per_km2': 220000, 'infrastructure_multiplier': 9.2},
            'east_asia': {'gdp_per_km2': 280000, 'infrastructure_multiplier': 7.8},
            'south_asia': {'gdp_per_km2': 95000, 'infrastructure_multiplier': 4.2},
            'africa': {'gdp_per_km2': 35000, 'infrastructure_multiplier': 2.8},
            'south_america': {'gdp_per_km2': 68000, 'infrastructure_multiplier': 3.5},
            'oceania': {'gdp_per_km2': 145000, 'infrastructure_multiplier': 6.8},
            'middle_east': {'gdp_per_km2': 125000, 'infrastructure_multiplier': 5.5},
            'ocean': {'gdp_per_km2': 0, 'infrastructure_multiplier': 0}
        }
        
        # Sector-specific damage multipliers
        self.sector_damage_factors = {
            'residential': {'complete': 1.0, 'severe': 0.7, 'moderate': 0.3, 'light': 0.05},
            'commercial': {'complete': 1.2, 'severe': 0.8, 'moderate': 0.4, 'light': 0.08},
            'industrial': {'complete': 1.5, 'severe': 0.9, 'moderate': 0.5, 'light': 0.12},
            'infrastructure': {'complete': 2.0, 'severe': 1.2, 'moderate': 0.6, 'light': 0.15}
        }
        
        # Recovery timeline estimates (years)
        self.recovery_timelines = {
            'complete': 15,
            'severe': 8,
            'moderate': 4,
            'light': 1
        }
    
    def get_region_by_coordinates(self, lat, lon):
        """Determine economic region from coordinates with higher precision"""
        # North America
        if (25 <= lat <= 80) and (-170 <= lon <= -50):
            return 'north_america'
        # Europe
        elif (35 <= lat <= 75) and (-15 <= lon <= 50):
            return 'europe'
        # East Asia (China, Japan, Korea)
        elif (0 <= lat <= 55) and (70 <= lon <= 150):
            return 'east_asia'
        # South Asia (India, Pakistan, etc.)
        elif (5 <= lat <= 40) and (60 <= lon <= 95):
            return 'south_asia'
        # Africa
        elif (-35 <= lat <= 40) and (-20 <= lon <= 55):
            return 'africa'
        # South America
        elif (-60 <= lat <= 15) and (-85 <= lon <= -30):
            return 'south_america'
        # Oceania
        elif (-50 <= lat <= -10) and (110 <= lon <= 180):
            return 'oceania'
        # Middle East
        elif (10 <= lat <= 45) and (25 <= lon <= 65):
            return 'middle_east'
        else:
            return 'ocean'
    
    def calculate_direct_damage(self, crater_radius_km, lat, lon):
        """Calculate direct infrastructure damage within crater"""
        crater_area = math.pi * (crater_radius_km ** 2)
        region = self.get_region_by_coordinates(lat, lon)
        
        if region == 'ocean':
            return {
                'area_destroyed_km2': crater_area,
                'direct_damage_usd': 0,
                'region': region,
                'damage_breakdown': {},
                'description': 'Ocean impact - minimal direct infrastructure damage'
            }
        
        region_data = self.regional_economic_density[region]
        base_gdp_density = region_data['gdp_per_km2']
        infrastructure_mult = region_data['infrastructure_multiplier']
        
        # Calculate damage by sector
        damage_breakdown = {}
        total_direct_damage = 0
        
        for sector, factors in self.sector_damage_factors.items():
            sector_value = crater_area * base_gdp_density * (0.25 if sector != 'infrastructure' else 0.1)
            sector_damage = sector_value * infrastructure_mult * factors['complete']
            damage_breakdown[sector] = {
                'value_at_risk': sector_value,
                'damage_amount': sector_damage,
                'damage_factor': factors['complete']
            }
            total_direct_damage += sector_damage
        
        return {
            'area_destroyed_km2': crater_area,
            'direct_damage_usd': total_direct_damage,
            'region': region,
            'damage_breakdown': damage_breakdown,
            'description': f'Complete infrastructure destruction in {crater_area:.1f} km² ({region})'
        }
    
    def calculate_secondary_damage(self, damage_zones, lat, lon):
        """Calculate secondary damage from various blast effects"""
        region = self.get_region_by_coordinates(lat, lon)
        region_data = self.regional_economic_density.get(region, self.regional_economic_density['africa'])
        base_gdp_density = region_data['gdp_per_km2']
        infrastructure_mult = region_data['infrastructure_multiplier']
        
        secondary_damage = 0
        damage_zones_breakdown = {}
        
        # Define damage zones with their effects
        zone_definitions = [
            {'name': 'severe', 'radius': damage_zones.get('severe', 0), 'damage_level': 'severe'},
            {'name': 'moderate', 'radius': damage_zones.get('moderate', 0), 'damage_level': 'moderate'},
            {'name': 'light', 'radius': damage_zones.get('light', 0), 'damage_level': 'light'}
        ]
        
        previous_radius = 0
        for zone in zone_definitions:
            if zone['radius'] > previous_radius:
                # Calculate ring area (exclude inner zones)
                outer_area = math.pi * (zone['radius'] ** 2)
                inner_area = math.pi * (previous_radius ** 2)
                ring_area = outer_area - inner_area
                
                # Calculate damage for this ring
                zone_damage_total = 0
                zone_breakdown = {}
                
                for sector, factors in self.sector_damage_factors.items():
                    sector_value = ring_area * base_gdp_density * (0.25 if sector != 'infrastructure' else 0.1)
                    damage_factor = factors[zone['damage_level']]
                    sector_damage = sector_value * infrastructure_mult * damage_factor
                    
                    zone_breakdown[sector] = {
                        'value_at_risk': sector_value,
                        'damage_amount': sector_damage,
                        'damage_factor': damage_factor
                    }
                    zone_damage_total += sector_damage
                
                damage_zones_breakdown[zone['name']] = {
                    'area_km2': ring_area,
                    'total_damage_usd': zone_damage_total,
                    'sector_breakdown': zone_breakdown
                }
                
                secondary_damage += zone_damage_total
                previous_radius = zone['radius']
        
        return {
            'total_secondary_damage_usd': secondary_damage,
            'damage_zones': damage_zones_breakdown,
            'region': region
        }
    
    def calculate_economic_disruption(self, affected_radius_km, lat, lon, disruption_duration_months=12):
        """Calculate broader economic disruption effects"""
        region = self.get_region_by_coordinates(lat, lon)
        region_data = self.regional_economic_density.get(region, self.regional_economic_density['africa'])
        
        affected_area = math.pi * (affected_radius_km ** 2)
        
        # Adjust for land vs ocean
        if region == 'ocean':
            land_factor = 0.1  # Some shipping/fishing impact
        else:
            land_factor = min(1.0, max(0.3, 1 - self.ocean_coverage * 0.7))
        
        effective_area = affected_area * land_factor
        
        # Calculate disruption by economic sector
        disruption_breakdown = {
            'supply_chain': {},
            'transportation': {},
            'utilities': {},
            'financial_services': {},
            'tourism': {}
        }
        
        base_annual_gdp = effective_area * region_data['gdp_per_km2']
        total_disruption = 0
        
        # Supply chain disruption
        supply_chain_factor = min(0.8, affected_radius_km / 100)  # More disruption for larger areas
        supply_chain_loss = base_annual_gdp * supply_chain_factor * (disruption_duration_months / 12)
        disruption_breakdown['supply_chain'] = {
            'annual_gdp_affected': base_annual_gdp,
            'disruption_factor': supply_chain_factor,
            'total_loss': supply_chain_loss
        }
        total_disruption += supply_chain_loss
        
        # Transportation disruption
        transport_factor = min(0.6, affected_radius_km / 150)
        transport_loss = base_annual_gdp * 0.15 * transport_factor * (disruption_duration_months / 12)
        disruption_breakdown['transportation'] = {
            'sector_gdp_share': 0.15,
            'disruption_factor': transport_factor,
            'total_loss': transport_loss
        }
        total_disruption += transport_loss
        
        # Utilities disruption
        utilities_factor = min(0.9, affected_radius_km / 50)
        utilities_loss = base_annual_gdp * 0.08 * utilities_factor * (disruption_duration_months / 12)
        disruption_breakdown['utilities'] = {
            'sector_gdp_share': 0.08,
            'disruption_factor': utilities_factor,
            'total_loss': utilities_loss
        }
        total_disruption += utilities_loss
        
        return {
            'affected_area_km2': affected_area,
            'effective_area_km2': effective_area,
            'disruption_duration_months': disruption_duration_months,
            'base_annual_gdp': base_annual_gdp,
            'total_disruption_cost_usd': total_disruption,
            'disruption_breakdown': disruption_breakdown,
            'region': region
        }
    
    def calculate_global_effects(self, energy_megatons, lat, lon):
        """Calculate global economic effects for large impacts"""
        if energy_megatons < 50:
            return {
                'global_effects': False,
                'description': 'Impact too small for significant global effects'
            }
        
        # Climate and global effects scaling
        climate_disruption_years = min(20, energy_megatons / 500)
        
        # Global GDP reduction based on impact energy
        if energy_megatons > 100000:  # Extinction-level
            gdp_reduction_percent = min(80, energy_megatons / 2000)
            description = "Civilization-threatening impact with mass extinction potential"
        elif energy_megatons > 10000:  # Continental devastation
            gdp_reduction_percent = min(25, energy_megatons / 2000)
            description = "Continental-scale devastation with global climate effects"
        elif energy_megatons > 1000:  # Regional catastrophe
            gdp_reduction_percent = min(8, energy_megatons / 2000)
            description = "Regional catastrophe with significant global climate disruption"
        else:  # Large local impact
            gdp_reduction_percent = min(2, energy_megatons / 1000)
            description = "Large local impact with minor global climate effects"
        
        annual_global_loss = self.global_gdp * (gdp_reduction_percent / 100)
        total_global_loss = annual_global_loss * climate_disruption_years
        
        # Calculate sector-specific global impacts
        global_sector_impacts = {
            'agriculture': annual_global_loss * 0.25,  # Agriculture hit hardest by climate
            'manufacturing': annual_global_loss * 0.20,
            'services': annual_global_loss * 0.30,
            'energy': annual_global_loss * 0.15,
            'other': annual_global_loss * 0.10
        }
        
        return {
            'global_effects': True,
            'energy_threshold_mt': energy_megatons,
            'climate_disruption_years': climate_disruption_years,
            'gdp_reduction_percent': gdp_reduction_percent,
            'annual_global_loss_usd': annual_global_loss,
            'total_global_loss_usd': total_global_loss,
            'global_sector_impacts': global_sector_impacts,
            'description': description,
            'comparable_events': self.get_comparable_economic_events(total_global_loss)
        }
    
    def get_comparable_economic_events(self, total_loss):
        """Compare economic impact to historical events"""
        comparisons = []
        
        # Historical economic disasters (adjusted to 2025 dollars)
        historical_events = [
            {'name': '2008 Financial Crisis', 'cost': 22e12},
            {'name': 'COVID-19 Pandemic (2020-2022)', 'cost': 28e12},
            {'name': 'World War II Total Cost', 'cost': 35e12},
            {'name': 'Great Depression (1929-1939)', 'cost': 15e12}
        ]
        
        for event in historical_events:
            if total_loss >= event['cost'] * 0.5:
                ratio = total_loss / event['cost']
                comparisons.append({
                    'event': event['name'],
                    'comparison': f"{ratio:.1f}x the economic cost",
                    'historical_cost': event['cost']
                })
        
        return comparisons
    
    def comprehensive_economic_analysis(self, impact_data, lat, lon):
        """Complete economic impact assessment"""
        energy_mt = impact_data.get('energy_megatons', 0)
        crater_radius = impact_data.get('crater_radius', 0)
        
        # Define damage zones based on impact energy and crater size
        damage_zones = {
            'severe': crater_radius * 4,      # Severe structural damage
            'moderate': crater_radius * 12,   # Moderate damage
            'light': crater_radius * 35       # Light damage/disruption
        }
        
        # Calculate all damage components
        direct_damage = self.calculate_direct_damage(crater_radius, lat, lon)
        secondary_damage = self.calculate_secondary_damage(damage_zones, lat, lon)
        economic_disruption = self.calculate_economic_disruption(crater_radius * 50, lat, lon)
        global_effects = self.calculate_global_effects(energy_mt, lat, lon)
        
        # Calculate recovery costs and timeline
        recovery_analysis = self.calculate_recovery_timeline(
            direct_damage, secondary_damage, economic_disruption
        )
        
        # Total economic impact
        total_economic_impact = (
            direct_damage['direct_damage_usd'] + 
            secondary_damage['total_secondary_damage_usd'] + 
            economic_disruption['total_disruption_cost_usd'] + 
            (global_effects.get('total_global_loss_usd', 0) if global_effects.get('global_effects') else 0)
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'impact_location': {'latitude': lat, 'longitude': lon},
            'impact_energy_mt': energy_mt,
            'crater_radius_km': crater_radius,
            'direct_damage': direct_damage,
            'secondary_damage': secondary_damage,
            'economic_disruption': economic_disruption,
            'global_effects': global_effects,
            'recovery_analysis': recovery_analysis,
            'total_economic_impact_usd': total_economic_impact,
            'summary': {
                'total_damage_usd': total_economic_impact,
                'total_damage_billion_usd': total_economic_impact / 1e9,
                'total_damage_trillion_usd': total_economic_impact / 1e12,
                'percent_global_gdp': (total_economic_impact / self.global_gdp) * 100,
                'impact_classification': self.classify_economic_impact(total_economic_impact),
                'recovery_timeline_years': recovery_analysis.get('total_recovery_years', 0)
            }
        }
    
    def calculate_recovery_timeline(self, direct_damage, secondary_damage, economic_disruption):
        """Calculate recovery timeline and associated costs"""
        region = direct_damage.get('region', 'unknown')
        
        # Base recovery multiplier by region (infrastructure quality factor)
        recovery_multipliers = {
            'north_america': 1.2,
            'europe': 1.1,
            'east_asia': 1.0,
            'south_asia': 0.7,
            'africa': 0.5,
            'south_america': 0.8,
            'oceania': 1.1,
            'middle_east': 0.9,
            'ocean': 1.0
        }
        
        recovery_mult = recovery_multipliers.get(region, 0.8)
        
        # Calculate recovery timeline
        direct_recovery_years = self.recovery_timelines['complete'] / recovery_mult
        secondary_recovery_years = self.recovery_timelines['moderate'] / recovery_mult
        disruption_recovery_years = economic_disruption['disruption_duration_months'] / 12
        
        total_recovery_years = max(direct_recovery_years, secondary_recovery_years, disruption_recovery_years)
        
        # Recovery costs (typically 20-50% more than initial damage)
        recovery_cost_multiplier = 1.3  # 30% more than damage cost
        total_recovery_cost = (
            direct_damage['direct_damage_usd'] + 
            secondary_damage['total_secondary_damage_usd']
        ) * recovery_cost_multiplier
        
        return {
            'direct_recovery_years': direct_recovery_years,
            'secondary_recovery_years': secondary_recovery_years,
            'disruption_recovery_years': disruption_recovery_years,
            'total_recovery_years': total_recovery_years,
            'recovery_cost_usd': total_recovery_cost,
            'recovery_multiplier': recovery_mult,
            'region': region
        }
    
    def classify_economic_impact(self, total_impact_usd):
        """Classify the economic impact severity"""
        if total_impact_usd > 50e12:  # > $50 trillion
            return "CIVILIZATION-THREATENING"
        elif total_impact_usd > 10e12:  # > $10 trillion
            return "GLOBAL CATASTROPHE"
        elif total_impact_usd > 1e12:   # > $1 trillion
            return "MAJOR DISASTER"
        elif total_impact_usd > 100e9:  # > $100 billion
            return "SIGNIFICANT DISASTER"
        elif total_impact_usd > 10e9:   # > $10 billion
            return "REGIONAL DISASTER"
        elif total_impact_usd > 1e9:    # > $1 billion
            return "LOCAL DISASTER"
        else:
            return "MINOR IMPACT"
