import requests  # type: ignore
import logging

logger = logging.getLogger(__name__)

class USGSElevationAPI:
    def get_elevation(self, lat, lon):
        """
        Fetch terrestrial elevation data from USGS Elevation Point Query Service (EPQS).
        """
        url = "https://epqs.nationalmap.gov/v1/json"
        params = {
            'x': lon,
            'y': lat,
            'units': 'Meters',
            'output': 'json'
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                elevation = data.get('value')
                if elevation is not None:
                    return float(elevation)
        except Exception as e:
            logger.error(f"USGS API error: {e}")
        return 0.0 # Default to sea level
