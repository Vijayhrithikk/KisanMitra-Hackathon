import requests
import os
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENWEATHER_KEY")
        self.base_url = "http://api.openweathermap.org/geo/1.0/direct"

    def get_coordinates(self, location_name):
        """
        Resolves a city/village name to Lat/Lon.
        """
        if not self.api_key:
            logger.warning("No OpenWeather API Key found. Using mock coordinates.")
            return {"lat": 16.5062, "lon": 80.6480, "name": "Vijayawada (Mock)"}

        try:
            # Limit to 1 result, search in India (IN)
            params = {
                "q": f"{location_name},IN",
                "limit": 1,
                "appid": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"Location not found: {location_name}")
                return None

            result = data[0]
            return {
                "lat": result["lat"],
                "lon": result["lon"],
                "name": result["name"],
                "state": result.get("state", "")
            }

        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
