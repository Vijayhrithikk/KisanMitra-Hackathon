"""
NASA POWER API Service for Historical Weather Data

Fetches 5 years of historical weather data for agricultural advisory.
Uses the NASA POWER Agroclimatology (AG) community data.

API Documentation: https://power.larc.nasa.gov/docs/services/api/
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

logger = logging.getLogger(__name__)

# Cache directory for storing fetched data
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'weather_cache')
os.makedirs(CACHE_DIR, exist_ok=True)


class NASAPowerService:
    """
    Service to fetch historical weather data from NASA POWER API.
    Provides 5-year historical averages for agricultural planning.
    """
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Key parameters for agriculture
    PARAMETERS = [
        "T2M_MAX",      # Max Temperature at 2m (°C)
        "T2M_MIN",      # Min Temperature at 2m (°C)
        "T2M",          # Average Temperature at 2m (°C)
        "PRECTOTCORR",  # Precipitation Corrected (mm/day)
        "RH2M",         # Relative Humidity at 2m (%)
        "ALLSKY_SFC_SW_DWN",  # Solar Radiation (MJ/m²/day)
        "WS2M",         # Wind Speed at 2m (m/s)
    ]
    
    def __init__(self):
        self.cache = {}
    
    def get_historical_weather(
        self, 
        lat: float, 
        lon: float, 
        years: int = 5,
        target_months: List[int] = None
    ) -> Dict:
        """
        Fetch historical weather data for the past N years.
        
        Args:
            lat: Latitude
            lon: Longitude
            years: Number of years of historical data (default 5)
            target_months: Specific months to analyze (1-12), or None for all
        
        Returns:
            Dictionary with monthly averages and patterns
        """
        cache_key = f"{lat:.2f}_{lon:.2f}_{years}"
        
        # Check cache
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        if os.path.exists(cache_file):
            cache_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if cache_age < 86400 * 7:  # Cache for 7 days
                logger.info(f"Using cached weather data for {lat}, {lon}")
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        logger.info(f"Fetching {years}-year historical weather for ({lat}, {lon})")
        
        # Calculate date range
        end_date = datetime.now() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=365 * years)
        
        try:
            params = {
                "parameters": ",".join(self.PARAMETERS),
                "community": "AG",
                "longitude": lon,
                "latitude": lat,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON"
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Process and aggregate data
            result = self._process_historical_data(data, target_months)
            
            # Cache the result
            with open(cache_file, 'w') as f:
                json.dump(result, f)
            
            return result
            
        except Exception as e:
            logger.error(f"NASA POWER API error: {e}")
            return self._get_fallback_data(lat, lon)
    
    def _process_historical_data(self, raw_data: Dict, target_months: List[int] = None) -> Dict:
        """
        Process raw NASA POWER data into monthly averages and patterns.
        """
        properties = raw_data.get("properties", {})
        parameters = properties.get("parameter", {})
        
        if not parameters:
            logger.warning("No parameters in NASA POWER response")
            return self._get_fallback_data(0, 0)
        
        # Organize data by month
        monthly_data = {m: {p: [] for p in self.PARAMETERS} for m in range(1, 13)}
        
        # Get one parameter to iterate dates
        sample_param = list(parameters.keys())[0]
        dates = list(parameters.get(sample_param, {}).keys())
        
        for date_str in dates:
            try:
                date = datetime.strptime(date_str, "%Y%m%d")
                month = date.month
                
                for param in self.PARAMETERS:
                    value = parameters.get(param, {}).get(date_str)
                    if value is not None and value > -999:  # Filter missing values
                        monthly_data[month][param].append(value)
            except:
                continue
        
        # Calculate monthly statistics
        monthly_averages = {}
        for month in range(1, 13):
            if target_months and month not in target_months:
                continue
                
            month_stats = {}
            for param in self.PARAMETERS:
                values = monthly_data[month][param]
                if values:
                    month_stats[param] = {
                        "avg": round(sum(values) / len(values), 1),
                        "min": round(min(values), 1),
                        "max": round(max(values), 1)
                    }
                else:
                    month_stats[param] = {"avg": None, "min": None, "max": None}
            
            monthly_averages[month] = month_stats
        
        return {
            "source": "NASA_POWER",
            "monthly_averages": monthly_averages,
            "parameters": self.PARAMETERS,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_growing_season_forecast(
        self, 
        lat: float, 
        lon: float, 
        start_month: int, 
        duration_months: int = 3
    ) -> Dict:
        """
        Get weather forecast for a crop growing season based on historical patterns.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_month: Month when growing season starts (1-12)
            duration_months: Length of growing season
        
        Returns:
            Weekly weather predictions based on 5-year historical averages
        """
        # Get target months
        target_months = []
        for i in range(duration_months):
            month = ((start_month - 1 + i) % 12) + 1
            target_months.append(month)
        
        historical = self.get_historical_weather(lat, lon, years=5, target_months=target_months)
        
        # Generate weekly breakdown
        weeks = []
        current_date = datetime.now()
        
        for week_num in range(duration_months * 4):  # ~4 weeks per month
            week_start = current_date + timedelta(weeks=week_num)
            month = week_start.month
            
            # Handle both int and string keys (JSON cache uses strings)
            month_data = historical.get("monthly_averages", {}).get(month) or historical.get("monthly_averages", {}).get(str(month), {})
            
            week_forecast = {
                "week": week_num + 1,
                "start_date": week_start.strftime("%Y-%m-%d"),
                "month": week_start.strftime("%B"),
                "temp_max": month_data.get("T2M_MAX", {}).get("avg", 30),
                "temp_min": month_data.get("T2M_MIN", {}).get("avg", 20),
                "rainfall_mm": month_data.get("PRECTOTCORR", {}).get("avg", 0) * 7,  # Weekly
                "humidity": month_data.get("RH2M", {}).get("avg", 60),
                "solar_radiation": month_data.get("ALLSKY_SFC_SW_DWN", {}).get("avg", 18),
            }
            
            # Add weather risk assessment
            week_forecast["risks"] = self._assess_weather_risks(week_forecast)
            
            weeks.append(week_forecast)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "growing_season": {
                "start_month": start_month,
                "duration_months": duration_months
            },
            "weekly_forecast": weeks,
            "source": "NASA_POWER_5YR_HISTORICAL"
        }
    
    def _assess_weather_risks(self, week_data: Dict) -> List[str]:
        """Assess weather-related risks for farming."""
        risks = []
        
        temp_max = week_data.get("temp_max", 30)
        temp_min = week_data.get("temp_min", 20)
        rainfall = week_data.get("rainfall_mm", 0)
        humidity = week_data.get("humidity", 60)
        
        if temp_max > 40:
            risks.append("heat_stress")
        if temp_min < 10:
            risks.append("cold_stress")
        if rainfall > 100:
            risks.append("flood_risk")
        if rainfall < 5 and temp_max > 35:
            risks.append("drought_risk")
        if humidity > 85:
            risks.append("fungal_disease_risk")
        
        return risks
    
    def _get_fallback_data(self, lat: float, lon: float) -> Dict:
        """Return fallback data when API fails."""
        logger.warning("Using fallback weather data")
        
        # Generic Indian agricultural weather patterns
        return {
            "source": "FALLBACK",
            "monthly_averages": {
                1: {"T2M_MAX": {"avg": 28}, "T2M_MIN": {"avg": 15}, "PRECTOTCORR": {"avg": 5}, "RH2M": {"avg": 55}},
                2: {"T2M_MAX": {"avg": 31}, "T2M_MIN": {"avg": 17}, "PRECTOTCORR": {"avg": 8}, "RH2M": {"avg": 50}},
                3: {"T2M_MAX": {"avg": 35}, "T2M_MIN": {"avg": 21}, "PRECTOTCORR": {"avg": 10}, "RH2M": {"avg": 45}},
                4: {"T2M_MAX": {"avg": 38}, "T2M_MIN": {"avg": 25}, "PRECTOTCORR": {"avg": 15}, "RH2M": {"avg": 40}},
                5: {"T2M_MAX": {"avg": 40}, "T2M_MIN": {"avg": 28}, "PRECTOTCORR": {"avg": 25}, "RH2M": {"avg": 45}},
                6: {"T2M_MAX": {"avg": 36}, "T2M_MIN": {"avg": 26}, "PRECTOTCORR": {"avg": 120}, "RH2M": {"avg": 70}},
                7: {"T2M_MAX": {"avg": 32}, "T2M_MIN": {"avg": 25}, "PRECTOTCORR": {"avg": 180}, "RH2M": {"avg": 80}},
                8: {"T2M_MAX": {"avg": 31}, "T2M_MIN": {"avg": 24}, "PRECTOTCORR": {"avg": 160}, "RH2M": {"avg": 82}},
                9: {"T2M_MAX": {"avg": 32}, "T2M_MIN": {"avg": 24}, "PRECTOTCORR": {"avg": 140}, "RH2M": {"avg": 78}},
                10: {"T2M_MAX": {"avg": 32}, "T2M_MIN": {"avg": 22}, "PRECTOTCORR": {"avg": 60}, "RH2M": {"avg": 65}},
                11: {"T2M_MAX": {"avg": 30}, "T2M_MIN": {"avg": 18}, "PRECTOTCORR": {"avg": 20}, "RH2M": {"avg": 55}},
                12: {"T2M_MAX": {"avg": 28}, "T2M_MIN": {"avg": 14}, "PRECTOTCORR": {"avg": 8}, "RH2M": {"avg": 55}},
            },
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_nasa_service = None

def get_nasa_power_service() -> NASAPowerService:
    global _nasa_service
    if _nasa_service is None:
        _nasa_service = NASAPowerService()
    return _nasa_service
