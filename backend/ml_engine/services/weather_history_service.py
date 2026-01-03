"""
Weather History Service - Historical rainfall patterns for enhanced risk analysis

Provides district-wise normal rainfall data, seasonal patterns, and drought risk assessment.
Uses static dataset compiled from IMD normals with OpenWeatherMap history as supplement.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

# OpenWeatherMap config (from existing weather service)
OWM_API_KEY = os.getenv('OWM_API_KEY', 'dd587855fbdac207034b854ea3e03c00')

# District-wise normal annual rainfall (mm) - compiled from IMD data
# Source: IMD Climatological Normals 1991-2020
DISTRICT_RAINFALL_NORMALS = {
    "Andhra Pradesh": {
        "Srikakulam": {"annual": 1050, "kharif": 750, "rabi": 180, "summer": 120, "monsoon_duration": 4},
        "Vizianagaram": {"annual": 1100, "kharif": 780, "rabi": 200, "summer": 120, "monsoon_duration": 4},
        "Visakhapatnam": {"annual": 1150, "kharif": 820, "rabi": 210, "summer": 120, "monsoon_duration": 4},
        "East Godavari": {"annual": 1200, "kharif": 850, "rabi": 220, "summer": 130, "monsoon_duration": 4},
        "West Godavari": {"annual": 1100, "kharif": 780, "rabi": 200, "summer": 120, "monsoon_duration": 4},
        "Krishna": {"annual": 950, "kharif": 680, "rabi": 170, "summer": 100, "monsoon_duration": 4},
        "Guntur": {"annual": 850, "kharif": 600, "rabi": 150, "summer": 100, "monsoon_duration": 3},
        "Prakasam": {"annual": 650, "kharif": 450, "rabi": 120, "summer": 80, "monsoon_duration": 3},
        "Nellore": {"annual": 1050, "kharif": 650, "rabi": 280, "summer": 120, "monsoon_duration": 4},
        "Chittoor": {"annual": 850, "kharif": 550, "rabi": 200, "summer": 100, "monsoon_duration": 3},
        "Kadapa": {"annual": 650, "kharif": 420, "rabi": 150, "summer": 80, "monsoon_duration": 3},
        "Anantapur": {"annual": 550, "kharif": 380, "rabi": 100, "summer": 70, "monsoon_duration": 3},
        "Kurnool": {"annual": 600, "kharif": 400, "rabi": 130, "summer": 70, "monsoon_duration": 3}
    },
    "Telangana": {
        "Hyderabad": {"annual": 800, "kharif": 580, "rabi": 120, "summer": 100, "monsoon_duration": 4},
        "Rangareddy": {"annual": 780, "kharif": 560, "rabi": 120, "summer": 100, "monsoon_duration": 4},
        "Medak": {"annual": 850, "kharif": 620, "rabi": 130, "summer": 100, "monsoon_duration": 4},
        "Nizamabad": {"annual": 950, "kharif": 700, "rabi": 150, "summer": 100, "monsoon_duration": 4},
        "Karimnagar": {"annual": 950, "kharif": 700, "rabi": 150, "summer": 100, "monsoon_duration": 4},
        "Warangal": {"annual": 1000, "kharif": 750, "rabi": 150, "summer": 100, "monsoon_duration": 4},
        "Khammam": {"annual": 1100, "kharif": 800, "rabi": 180, "summer": 120, "monsoon_duration": 4},
        "Nalgonda": {"annual": 680, "kharif": 480, "rabi": 120, "summer": 80, "monsoon_duration": 3},
        "Mahbubnagar": {"annual": 650, "kharif": 450, "rabi": 120, "summer": 80, "monsoon_duration": 3},
        "Adilabad": {"annual": 1100, "kharif": 800, "rabi": 180, "summer": 120, "monsoon_duration": 4}
    },
    "Karnataka": {
        "Bangalore Urban": {"annual": 900, "kharif": 580, "rabi": 200, "summer": 120, "monsoon_duration": 4},
        "Bangalore Rural": {"annual": 850, "kharif": 550, "rabi": 190, "summer": 110, "monsoon_duration": 4},
        "Mysore": {"annual": 780, "kharif": 500, "rabi": 180, "summer": 100, "monsoon_duration": 4},
        "Bellary": {"annual": 550, "kharif": 380, "rabi": 100, "summer": 70, "monsoon_duration": 3},
        "Gulbarga": {"annual": 750, "kharif": 550, "rabi": 120, "summer": 80, "monsoon_duration": 4}
    },
    "Tamil Nadu": {
        "Chennai": {"annual": 1400, "kharif": 400, "rabi": 800, "summer": 200, "monsoon_duration": 5},
        "Coimbatore": {"annual": 650, "kharif": 280, "rabi": 280, "summer": 90, "monsoon_duration": 3},
        "Madurai": {"annual": 850, "kharif": 250, "rabi": 480, "summer": 120, "monsoon_duration": 4}
    },
    "Maharashtra": {
        "Mumbai": {"annual": 2400, "kharif": 2100, "rabi": 50, "summer": 250, "monsoon_duration": 4},
        "Pune": {"annual": 750, "kharif": 600, "rabi": 50, "summer": 100, "monsoon_duration": 4},
        "Nagpur": {"annual": 1100, "kharif": 950, "rabi": 50, "summer": 100, "monsoon_duration": 4}
    }
}

# Crop water requirements (mm per crop cycle)
CROP_WATER_NEEDS = {
    "Paddy": {"min": 1200, "optimal": 1500, "max": 2000, "critical_stage": "flowering"},
    "Wheat": {"min": 300, "optimal": 450, "max": 600, "critical_stage": "grain_filling"},
    "Cotton": {"min": 500, "optimal": 700, "max": 1000, "critical_stage": "boll_formation"},
    "Maize": {"min": 400, "optimal": 600, "max": 800, "critical_stage": "tasseling"},
    "Groundnut": {"min": 350, "optimal": 500, "max": 700, "critical_stage": "pegging"},
    "Sugarcane": {"min": 1500, "optimal": 2000, "max": 2500, "critical_stage": "tillering"},
    "Chilli": {"min": 400, "optimal": 600, "max": 800, "critical_stage": "flowering"},
    "Turmeric": {"min": 800, "optimal": 1200, "max": 1600, "critical_stage": "rhizome"},
    "Bengal Gram": {"min": 200, "optimal": 350, "max": 500, "critical_stage": "flowering"},
    "Tomato": {"min": 350, "optimal": 500, "max": 700, "critical_stage": "fruiting"},
    "Onion": {"min": 350, "optimal": 500, "max": 650, "critical_stage": "bulb_formation"},
    "Banana": {"min": 1200, "optimal": 1800, "max": 2200, "critical_stage": "bunch_formation"},
    "Soybean": {"min": 400, "optimal": 600, "max": 800, "critical_stage": "pod_filling"},
    "Millets": {"min": 200, "optimal": 350, "max": 500, "critical_stage": "grain_filling"}
}


class WeatherHistoryService:
    """
    Provides historical weather patterns and rainfall analysis.
    """
    
    def __init__(self):
        logger.info("Weather History Service initialized")
    
    def get_normal_rainfall(self, state: str, district: str) -> Dict:
        """
        Get normal rainfall data for a district.
        
        Returns:
            Dict with annual, seasonal rainfall norms
        """
        state_data = DISTRICT_RAINFALL_NORMALS.get(state, {})
        district_data = state_data.get(district)
        
        if district_data:
            return {
                "district": district,
                "state": state,
                "source": "IMD Climatological Normals",
                **district_data
            }
        
        # Fallback: state average if district not found
        if state_data:
            avg_annual = sum(d.get('annual', 800) for d in state_data.values()) / len(state_data)
            return {
                "district": district,
                "state": state,
                "annual": int(avg_annual),
                "kharif": int(avg_annual * 0.7),
                "rabi": int(avg_annual * 0.2),
                "summer": int(avg_annual * 0.1),
                "monsoon_duration": 4,
                "source": "State Average Estimate"
            }
        
        # Ultimate fallback
        return {
            "district": district,
            "state": state,
            "annual": 800,
            "kharif": 560,
            "rabi": 160,
            "summer": 80,
            "monsoon_duration": 4,
            "source": "National Average Estimate"
        }
    
    def get_seasonal_rainfall(self, state: str, district: str, season: str) -> Dict:
        """
        Get expected rainfall for a specific season.
        
        Args:
            state: State name
            district: District name
            season: "Kharif", "Rabi", or "Zaid/Summer"
        """
        normals = self.get_normal_rainfall(state, district)
        
        season_map = {
            "Kharif": "kharif",
            "Rabi": "rabi",
            "Zaid": "summer",
            "Summer": "summer"
        }
        
        season_key = season_map.get(season, "kharif")
        expected = normals.get(season_key, 500)
        
        return {
            "season": season,
            "expected_rainfall_mm": expected,
            "classification": self._classify_rainfall(expected, season),
            "monsoon_months": self._get_monsoon_months(season)
        }
    
    def _classify_rainfall(self, rainfall_mm: int, season: str) -> str:
        """Classify rainfall amount."""
        if season in ["Kharif", "kharif"]:
            if rainfall_mm > 900:
                return "High"
            elif rainfall_mm > 500:
                return "Medium"
            else:
                return "Low"
        else:  # Rabi/Summer
            if rainfall_mm > 200:
                return "High"
            elif rainfall_mm > 100:
                return "Medium"
            else:
                return "Low"
    
    def _get_monsoon_months(self, season: str) -> List[str]:
        """Get key rainfall months for season."""
        if season in ["Kharif", "kharif"]:
            return ["June", "July", "August", "September"]
        elif season in ["Rabi", "rabi"]:
            return ["October", "November", "December"]
        else:
            return ["March", "April", "May"]
    
    def calculate_rainfall_deviation(self, state: str, district: str,
                                    current_rainfall_mm: float,
                                    season: str = "Kharif") -> Dict:
        """
        Calculate deviation from normal rainfall.
        
        Returns:
            Dict with deviation percentage and risk assessment
        """
        seasonal = self.get_seasonal_rainfall(state, district, season)
        normal = seasonal['expected_rainfall_mm']
        
        if normal == 0:
            normal = 500  # Fallback
        
        deviation_percent = ((current_rainfall_mm - normal) / normal) * 100
        
        # Classify deviation
        if deviation_percent < -50:
            category = "Severe Deficit"
            risk = "High"
        elif deviation_percent < -20:
            category = "Deficit"
            risk = "Medium"
        elif deviation_percent > 50:
            category = "Excess"
            risk = "Medium"  # Flooding risk
        elif deviation_percent > 20:
            category = "Above Normal"
            risk = "Low"
        else:
            category = "Normal"
            risk = "Low"
        
        return {
            "normal_mm": normal,
            "actual_mm": current_rainfall_mm,
            "deviation_percent": round(deviation_percent, 1),
            "category": category,
            "risk_level": risk
        }
    
    def assess_crop_water_adequacy(self, crop_name: str, state: str, 
                                   district: str, season: str) -> Dict:
        """
        Assess if rainfall will be adequate for a specific crop.
        
        Returns:
            Dict with adequacy assessment and recommendations
        """
        crop_needs = CROP_WATER_NEEDS.get(crop_name, {
            "min": 400, "optimal": 600, "max": 800
        })
        
        seasonal = self.get_seasonal_rainfall(state, district, season)
        expected_rainfall = seasonal['expected_rainfall_mm']
        
        min_need = crop_needs['min']
        optimal = crop_needs['optimal']
        max_need = crop_needs['max']
        
        # Assess adequacy
        if expected_rainfall >= optimal:
            adequacy = "Adequate"
            irrigation_needed = "Minimal supplemental irrigation"
            risk_score = 10
        elif expected_rainfall >= min_need:
            adequacy = "Marginal"
            irrigation_needed = "Moderate irrigation required"
            risk_score = 35
        else:
            adequacy = "Inadequate"
            deficit = min_need - expected_rainfall
            irrigation_needed = f"Heavy irrigation needed (~{deficit}mm deficit)"
            risk_score = 65
        
        # Excess check
        if expected_rainfall > max_need:
            adequacy = "Excess Risk"
            irrigation_needed = "Drainage required, waterlogging risk"
            risk_score = 50
        
        return {
            "crop": crop_name,
            "expected_rainfall_mm": expected_rainfall,
            "crop_water_need_mm": f"{min_need}-{optimal}",
            "adequacy": adequacy,
            "irrigation_advice": irrigation_needed,
            "water_risk_score": risk_score,
            "critical_stage": crop_needs.get('critical_stage', 'unknown')
        }
    
    def calculate_weather_risk(self, crop_name: str, state: str, district: str,
                              season: str, current_forecast: Dict = None) -> int:
        """
        Calculate comprehensive weather risk score (0-100).
        
        Args:
            crop_name: Name of the crop
            state: State name
            district: District name
            season: Current season
            current_forecast: Optional current weather forecast
            
        Returns:
            Risk score 0 (low risk) to 100 (high risk)
        """
        # Base risk from water adequacy
        adequacy = self.assess_crop_water_adequacy(crop_name, state, district, season)
        water_risk = adequacy['water_risk_score']
        
        # Adjust for current forecast if available
        forecast_risk = 0
        if current_forecast:
            rain_days = current_forecast.get('rain_days', 0)
            weather_risk_level = current_forecast.get('weather_risk', 'Low')
            
            # Extreme weather adjustment
            if weather_risk_level == 'High':
                forecast_risk = 30
            elif weather_risk_level == 'Medium':
                forecast_risk = 15
            
            # Rain days adjustment for water-needing crops
            crop_needs = CROP_WATER_NEEDS.get(crop_name, {})
            if crop_needs.get('min', 0) > 800 and rain_days < 3:  # High water crop, few rain days
                forecast_risk += 20
        
        # Seasonal risk (summer is riskier for most crops)
        season_risk = {
            'Kharif': 0,
            'Rabi': 10,
            'Zaid': 25,
            'Summer': 25
        }.get(season, 10)
        
        # Combine risks
        total_risk = min(100, int(water_risk * 0.5 + forecast_risk * 0.3 + season_risk * 0.2))
        
        return total_risk
    
    def get_district_weather_summary(self, state: str, district: str) -> Dict:
        """
        Get comprehensive weather summary for a district.
        """
        normals = self.get_normal_rainfall(state, district)
        
        # Classify district by rainfall
        annual = normals.get('annual', 800)
        if annual > 1200:
            zone = "High Rainfall Zone"
            suitable_crops = ["Paddy", "Sugarcane", "Banana", "Turmeric"]
        elif annual > 750:
            zone = "Medium Rainfall Zone"
            suitable_crops = ["Cotton", "Maize", "Chilli", "Groundnut"]
        else:
            zone = "Low Rainfall Zone"
            suitable_crops = ["Millets", "Pulses", "Groundnut", "Sorghum"]
        
        return {
            "district": district,
            "state": state,
            "annual_rainfall_mm": annual,
            "rainfall_zone": zone,
            "monsoon_duration_months": normals.get('monsoon_duration', 4),
            "naturally_suitable_crops": suitable_crops,
            "irrigation_dependency": "Low" if annual > 900 else "Medium" if annual > 600 else "High"
        }


# Singleton instance
_weather_history_service = None

def get_weather_history_service() -> WeatherHistoryService:
    """Get or create weather history service singleton."""
    global _weather_history_service
    if _weather_history_service is None:
        _weather_history_service = WeatherHistoryService()
    return _weather_history_service
