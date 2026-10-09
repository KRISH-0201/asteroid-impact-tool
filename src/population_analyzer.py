import math
import os

# Try to import geopandas - it's optional
try:
    import geopandas as gpd  # type: ignore
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

class PopulationAnalyzer:
    def __init__(self):
        self.pop_gdf = None
        
        # Load population density data if available
        geojson_path = 'data/population/population_density.geojson'
        if GEOPANDAS_AVAILABLE and os.path.exists(geojson_path):
            try:
                self.pop_gdf = gpd.read_file(geojson_path)
            except Exception:
                self.pop_gdf = None
        
        # Average population density by region (people/km²) for fallback estimates
        self.regional_density = {
            # (lat_min, lat_max, lon_min, lon_max): density
            'north_america': {'bounds': (25, 80, -170, -50), 'density': 18},
            'europe': {'bounds': (35, 75, -15, 50), 'density': 108},
            'east_asia': {'bounds': (0, 55, 100, 150), 'density': 145},
            'south_asia': {'bounds': (5, 40, 60, 100), 'density': 380},
            'africa': {'bounds': (-35, 40, -20, 55), 'density': 45},
            'south_america': {'bounds': (-60, 15, -85, -30), 'density': 25},
            'oceania': {'bounds': (-50, -10, 110, 180), 'density': 3},
            'middle_east': {'bounds': (10, 45, 25, 65), 'density': 35},
        }

    def estimate_density(self, lat, lon):
        """Estimate population density (people/km²) from coordinates."""
        for region, data in self.regional_density.items():
            lat_min, lat_max, lon_min, lon_max = data['bounds']
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return data['density']
        return 5  # Ocean / sparse areas

    def estimate_zone_population(self, lat, lon, radius_km):
        """Estimate population in a circular zone of given radius."""
        area = math.pi * (radius_km ** 2)
        density = self.estimate_density(lat, lon)
        return int(area * density)

    def analyze_comprehensive_impact(self, lat, lon, crater, fireball, shockwave, winds, earthquake):
        """
        Estimate population in each damage zone.
        Falls back to area × regional density estimates when GeoJSON data is unavailable.
        """
        # Try GeoDataFrame spatial analysis first
        if self.pop_gdf is not None:
            try:
                return self._analyze_with_geodata(lat, lon, crater, fireball, shockwave, winds, earthquake)
            except Exception:
                pass  # Fall through to estimate mode

        # Fallback: area × density estimates
        crater_r_km = crater.get('diameter_km', 0) / 2
        fireball_r_km = fireball.get('radius_km', 0)
        shock_severe_km = shockwave.get('damage_zones', {}).get('severe', 0)
        shock_moderate_km = shockwave.get('damage_zones', {}).get('moderate', 0)
        shock_light_km = shockwave.get('damage_zones', {}).get('light', 0)
        winds_km = winds.get('range_km', 0)
        quake_km = earthquake.get('range_km', 0)

        return {
            'crater': self.estimate_zone_population(lat, lon, crater_r_km),
            'fireball': self.estimate_zone_population(lat, lon, fireball_r_km),
            'shock_severe': self.estimate_zone_population(lat, lon, shock_severe_km),
            'shock_moderate': self.estimate_zone_population(lat, lon, shock_moderate_km),
            'shock_light': self.estimate_zone_population(lat, lon, shock_light_km),
            'winds': self.estimate_zone_population(lat, lon, winds_km),
            'quake': self.estimate_zone_population(lat, lon, quake_km),
            'estimated': True  # Flag that these are estimates
        }

    def _analyze_with_geodata(self, lat, lon, crater, fireball, shockwave, winds, earthquake):
        """Spatial analysis using loaded GeoDataFrame."""
        import geopandas as gpd  # type: ignore
        
        pop_gdf = self.pop_gdf
        if pop_gdf is None:
            return {}

        impact_point = gpd.GeoDataFrame(
            geometry=[gpd.points_from_xy([lon], [lat])[0]],
            crs="EPSG:4326"
        )
        impact_point = impact_point.to_crs(pop_gdf.crs)

        zones = {
            'crater': crater.get('diameter_km', 0) * 1000 / 2,
            'fireball': fireball.get('radius_km', 0) * 1000,
            'shock_severe': shockwave.get('damage_zones', {}).get('severe', 0) * 1000,
            'shock_moderate': shockwave.get('damage_zones', {}).get('moderate', 0) * 1000,
            'shock_light': shockwave.get('damage_zones', {}).get('light', 0) * 1000,
            'winds': winds.get('range_km', 0) * 1000,
            'quake': earthquake.get('range_km', 0) * 1000
        }

        results = {}
        for zone_name, radius_m in zones.items():
            circle = impact_point.buffer(radius_m)[0]
            pts = pop_gdf[pop_gdf.geometry.within(circle)]
            results[zone_name] = int(pts['population'].sum())

        return results
