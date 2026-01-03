"""
Crop Advisory Service

Generates comprehensive, week-by-week farming advisories based on:
1. Crop growth stages from database
2. Historical weather patterns from NASA POWER
3. IMD rainfall data integration
4. Pest and disease risk assessment

Provides advisories in both Telugu and English.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .nasa_power_service import get_nasa_power_service

logger = logging.getLogger(__name__)

# Load crop stages database
CROP_STAGES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'crop_stages.json')

def load_crop_stages():
    try:
        with open(CROP_STAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load crop stages: {e}")
        return {"crops": {}}

CROP_DATABASE = load_crop_stages()


class CropAdvisoryService:
    """
    Service to generate comprehensive crop advisories based on
    historical weather patterns and crop growth stages.
    """
    
    def __init__(self):
        self.nasa_service = get_nasa_power_service()
        self.crop_db = CROP_DATABASE.get("crops", {})
    
    def generate_advisory(
        self, 
        crop: str, 
        lat: float, 
        lon: float,
        sowing_date: datetime = None,
        language: str = "both"  # "en", "te", or "both"
    ) -> Dict:
        """
        Generate a comprehensive crop advisory.
        
        Args:
            crop: Crop name (Rice, Cotton, etc.)
            lat: Latitude of farm location
            lon: Longitude of farm location
            sowing_date: When the crop was/will be sown (default: today)
            language: Language for advisory ("en", "te", or "both")
        
        Returns:
            Complete advisory with week-by-week guidance
        """
        if sowing_date is None:
            sowing_date = datetime.now()
        
        # Get crop data
        crop_data = self._get_crop_data(crop)
        if not crop_data:
            return {"error": f"Crop '{crop}' not found in database"}
        
        # Get historical weather patterns
        duration_months = (crop_data["duration_days"] // 30) + 1
        weather_forecast = self.nasa_service.get_growing_season_forecast(
            lat, lon, 
            start_month=sowing_date.month,
            duration_months=duration_months
        )
        
        # Generate week-by-week advisory
        weekly_advisory = self._generate_weekly_advisory(
            crop_data, 
            weather_forecast,
            sowing_date,
            language
        )
        
        # Generate summary
        summary = self._generate_summary(crop_data, weather_forecast, language)
        
        # Generate pest/disease alerts
        alerts = self._generate_alerts(crop_data, weather_forecast, language)
        
        return {
            "crop": {
                "name_en": crop_data["name_en"],
                "name_te": crop_data["name_te"],
                "duration_days": crop_data["duration_days"],
                "water_requirement": crop_data["water_requirement"]
            },
            "location": {"lat": lat, "lon": lon},
            "sowing_date": sowing_date.strftime("%Y-%m-%d"),
            "harvest_date": (sowing_date + timedelta(days=crop_data["duration_days"])).strftime("%Y-%m-%d"),
            "summary": summary,
            "weekly_advisory": weekly_advisory,
            "alerts": alerts,
            "weather_source": weather_forecast.get("source", "NASA_POWER"),
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_crop_data(self, crop: str) -> Optional[Dict]:
        """Get crop data from database, handling case variations and aliases."""
        # Crop name aliases/normalizations to match crop_stages.json keys
        name_map = {
            # Rice variations
            "ground nuts": "Groundnut",
            "groundnuts": "Groundnut",
            "paddy": "Rice",
            "paddy (rice)": "Rice",
            "peanut": "Groundnut",
            "peanuts": "Groundnut",
            
            # Chilli variations
            "mirchi": "Chilli",
            "red chilli": "Chilli",
            "chili": "Chilli",
            
            # Maize variations  
            "corn": "Maize",
            
            # Additional crops - map to existing or use generic
            "millets": "Maize",  # Similar cultivation
            "tobacco": "Chilli",  # Similar cultivation pattern
            "oil seeds": "Groundnut",  # Similar to groundnut
            "barley": "Wheat",  # Similar to wheat
            "soybean": "Pulses",  # Legume
            "bengal gram": "Pulses",  # Legume/pulse
            "red gram": "Pulses",
            "black gram": "Pulses",
            "green gram": "Pulses",
            "chickpea": "Pulses",
            "pigeon pea": "Pulses",
        }
        
        # Normalize crop name
        crop_lower = crop.lower().strip()
        if crop_lower in name_map:
            crop = name_map[crop_lower]
        
        # Try exact match first
        if crop in self.crop_db:
            return self.crop_db[crop]
        
        # Try case-insensitive match
        for key in self.crop_db:
            if key.lower() == crop.lower():
                return self.crop_db[key]
        
        # If still not found, return None (will use generic fallback in caller)
        logger.warning(f"Crop '{crop}' not found in advisory database")
        return None
    
    def _generate_weekly_advisory(
        self, 
        crop_data: Dict, 
        weather: Dict, 
        sowing_date: datetime,
        language: str
    ) -> List[Dict]:
        """Generate week-by-week farming tasks with weather integration."""
        
        stages = crop_data.get("stages", [])
        weekly_weather = weather.get("weekly_forecast", [])
        
        advisory = []
        
        for stage in stages:
            week_start = stage["week_start"]
            week_end = stage["week_end"]
            
            for week in range(week_start, week_end + 1):
                week_date = sowing_date + timedelta(weeks=week - 1)
                
                # Get weather for this week
                week_weather = {}
                if week - 1 < len(weekly_weather):
                    week_weather = weekly_weather[week - 1]
                
                # Build task list based on language
                tasks = []
                if language in ["en", "both"]:
                    for task in stage.get("tasks_en", []):
                        tasks.append({"text": task, "lang": "en"})
                if language in ["te", "both"]:
                    for task in stage.get("tasks_te", []):
                        tasks.append({"text": task, "lang": "te"})
                
                # Irrigation advice
                irrigation = {}
                if language in ["en", "both"]:
                    irrigation["en"] = stage.get("irrigation", "")
                if language in ["te", "both"]:
                    irrigation["te"] = stage.get("irrigation_te", "")
                
                # Weather-based adjustments
                weather_notes = self._get_weather_notes(week_weather, stage, language)
                
                advisory.append({
                    "week": week,
                    "date_range": {
                        "start": week_date.strftime("%Y-%m-%d"),
                        "end": (week_date + timedelta(days=6)).strftime("%Y-%m-%d")
                    },
                    "stage": {
                        "name_en": stage.get("name_en", ""),
                        "name_te": stage.get("name_te", "")
                    },
                    "tasks": tasks,
                    "irrigation": irrigation,
                    "weather": {
                        "temp_max": week_weather.get("temp_max", "N/A"),
                        "temp_min": week_weather.get("temp_min", "N/A"),
                        "rainfall_mm": round(week_weather.get("rainfall_mm", 0), 1),
                        "humidity": week_weather.get("humidity", "N/A"),
                        "risks": week_weather.get("risks", [])
                    },
                    "weather_notes": weather_notes
                })
        
        return advisory
    
    def _get_weather_notes(self, weather: Dict, stage: Dict, language: str) -> List[Dict]:
        """Generate weather-based farming notes."""
        notes = []
        
        risks = weather.get("risks", [])
        rainfall = weather.get("rainfall_mm", 0)
        temp_max = weather.get("temp_max", 30)
        humidity = weather.get("humidity", 60)
        
        if "heat_stress" in risks:
            if language in ["en", "both"]:
                notes.append({"text": "⚠️ High temperature expected. Provide shade/mulching. Irrigate in evening.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": "⚠️ అధిక ఉష్ణోగ్రత. నీడ/మల్చింగ్ ఇవ్వండి. సాయంత్రం నీరు పెట్టండి.", "lang": "te"})
        
        if "drought_risk" in risks:
            if language in ["en", "both"]:
                notes.append({"text": "🏜️ Drought conditions likely. Increase irrigation frequency.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": "🏜️ కరువు పరిస్థితులు. నీటిపారుదల పెంచండి.", "lang": "te"})
        
        if "flood_risk" in risks:
            if language in ["en", "both"]:
                notes.append({"text": "🌊 Heavy rainfall expected. Ensure drainage. Delay fertilizer application.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": "🌊 భారీ వర్షం అవకాశం. డ్రైనేజ్ చూడండి. ఎరువులు ఆపండి.", "lang": "te"})
        
        if "fungal_disease_risk" in risks:
            if language in ["en", "both"]:
                notes.append({"text": "🍄 High humidity - fungal disease risk. Preventive spray recommended.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": "🍄 అధిక తేమ - శిలీంద్ర వ్యాధి ప్రమాదం. నివారణ మందు పిచికారి చేయండి.", "lang": "te"})
        
        if "cold_stress" in risks:
            if language in ["en", "both"]:
                notes.append({"text": "❄️ Low temperature expected. Protect young plants.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": "❄️ తక్కువ ఉష్ణోగ్రత. చిన్న మొక్కలను రక్షించండి.", "lang": "te"})
        
        # Rainfall-based irrigation adjustment
        if rainfall > 50:
            if language in ["en", "both"]:
                notes.append({"text": f"🌧️ Expected rainfall: {rainfall:.0f}mm. Skip irrigation.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": f"🌧️ అంచనా వర్షపాతం: {rainfall:.0f}mm. నీరు అక్కర్లేదు.", "lang": "te"})
        elif rainfall > 20:
            if language in ["en", "both"]:
                notes.append({"text": f"🌦️ Moderate rainfall: {rainfall:.0f}mm. Reduce irrigation.", "lang": "en"})
            if language in ["te", "both"]:
                notes.append({"text": f"🌦️ మోస్తరు వర్షం: {rainfall:.0f}mm. నీరు తగ్గించండి.", "lang": "te"})
        
        return notes
    
    def _generate_summary(self, crop_data: Dict, weather: Dict, language: str) -> Dict:
        """Generate overall advisory summary."""
        weekly = weather.get("weekly_forecast", [])
        
        # Calculate totals
        total_rainfall = sum(w.get("rainfall_mm", 0) for w in weekly)
        avg_temp = sum(w.get("temp_max", 30) for w in weekly) / max(len(weekly), 1)
        
        # Risk assessment
        all_risks = []
        for w in weekly:
            all_risks.extend(w.get("risks", []))
        
        risk_counts = {}
        for r in all_risks:
            risk_counts[r] = risk_counts.get(r, 0) + 1
        
        dominant_risk = max(risk_counts.keys(), key=lambda k: risk_counts[k]) if risk_counts else "none"
        
        summary = {}
        
        if language in ["en", "both"]:
            summary["en"] = {
                "crop_duration": f"{crop_data['duration_days']} days",
                "expected_rainfall": f"{total_rainfall:.0f} mm",
                "average_temp": f"{avg_temp:.1f}°C",
                "main_risk": dominant_risk.replace("_", " ").title() if dominant_risk != "none" else "None",
                "recommendation": self._get_recommendation_en(crop_data, dominant_risk, total_rainfall)
            }
        
        if language in ["te", "both"]:
            summary["te"] = {
                "crop_duration": f"{crop_data['duration_days']} రోజులు",
                "expected_rainfall": f"{total_rainfall:.0f} మి.మీ.",
                "average_temp": f"{avg_temp:.1f}°C",
                "main_risk": self._translate_risk_te(dominant_risk),
                "recommendation": self._get_recommendation_te(crop_data, dominant_risk, total_rainfall)
            }
        
        return summary
    
    def _get_recommendation_en(self, crop_data: Dict, risk: str, rainfall: float) -> str:
        """Generate English recommendation based on conditions."""
        water_req = crop_data.get("water_requirement", "Medium")
        
        if risk == "drought_risk":
            return f"Plan for additional irrigation. {crop_data['name_en']} needs {water_req.lower()} water. Consider drip irrigation."
        elif risk == "flood_risk":
            return "Ensure proper drainage. Prepare raised beds if possible. Keep pesticides ready for disease outbreak."
        elif risk == "heat_stress":
            return "Schedule irrigations for early morning or evening. Mulching recommended."
        elif risk == "fungal_disease_risk":
            return "Keep fungicide sprays ready. Avoid dense planting. Ensure good air circulation."
        else:
            return f"Favorable conditions expected. Follow standard practices for {crop_data['name_en']}."
    
    def _get_recommendation_te(self, crop_data: Dict, risk: str, rainfall: float) -> str:
        """Generate Telugu recommendation based on conditions."""
        water_req = crop_data.get("water_requirement", "Medium")
        
        if risk == "drought_risk":
            return f"అదనపు నీటిపారుదల ప్లాన్ చేయండి. {crop_data['name_te']}కు నీరు అవసరం. డ్రిప్ ఇరిగేషన్ పరిశీలించండి."
        elif risk == "flood_risk":
            return "సరైన డ్రైనేజ్ ఉండేలా చూడండి. వీలైతే ఎత్తు మడులు వేయండి. వ్యాధుల కోసం మందులు సిద్ధంగా ఉంచండి."
        elif risk == "heat_stress":
            return "ఉదయం లేదా సాయంత్రం నీరు పెట్టండి. మల్చింగ్ చేయండి."
        elif risk == "fungal_disease_risk":
            return "శిలీంద్ర నాశినులు సిద్ధంగా ఉంచండి. దట్టంగా నాటకండి. గాలి వచ్చేలా చూడండి."
        else:
            return f"అనుకూల పరిస్థితులు. {crop_data['name_te']} సాధారణ పద్ధతులు అనుసరించండి."
    
    def _translate_risk_te(self, risk: str) -> str:
        """Translate risk names to Telugu."""
        translations = {
            "drought_risk": "కరువు ప్రమాదం",
            "flood_risk": "వరద ప్రమాదం",
            "heat_stress": "వేడి ఒత్తిడి",
            "cold_stress": "చలి ఒత్తిడి",
            "fungal_disease_risk": "శిలీంద్ర వ్యాధి ప్రమాదం",
            "none": "ఏమీ లేదు"
        }
        return translations.get(risk, risk)
    
    def _generate_alerts(self, crop_data: Dict, weather: Dict, language: str) -> List[Dict]:
        """Generate pest and disease alerts based on weather and crop stage."""
        alerts = []
        weekly = weather.get("weekly_forecast", [])
        
        pests = crop_data.get("pests", [])
        diseases = crop_data.get("diseases", [])
        
        current_month = datetime.now().month
        
        # Check pest risks
        for pest in pests:
            if current_month in pest.get("risk_months", []):
                alert = {"type": "pest", "severity": "warning"}
                if language in ["en", "both"]:
                    alert["name_en"] = pest["name"]
                    alert["message_en"] = f"High risk period for {pest['name']}. Scout fields regularly."
                if language in ["te", "both"]:
                    alert["name_te"] = pest.get("name_te", pest["name"])
                    alert["message_te"] = f"{pest.get('name_te', pest['name'])} ప్రమాదం ఎక్కువ. క్రమం తప్పకుండా చూడండి."
                alerts.append(alert)
        
        # Check disease conditions
        for disease in diseases:
            conditions = disease.get("conditions", "").lower()
            
            # Check if weather matches disease conditions
            triggered = False
            for week in weekly:
                humidity = week.get("humidity", 60)
                rainfall = week.get("rainfall_mm", 0)
                
                if "humidity" in conditions and humidity > 80:
                    triggered = True
                if "rain" in conditions and rainfall > 50:
                    triggered = True
                if "waterlogging" in conditions and rainfall > 100:
                    triggered = True
            
            if triggered:
                alert = {"type": "disease", "severity": "caution"}
                if language in ["en", "both"]:
                    alert["name_en"] = disease["name"]
                    alert["message_en"] = f"Conditions favorable for {disease['name']}. Take preventive measures."
                if language in ["te", "both"]:
                    alert["name_te"] = disease.get("name_te", disease["name"])
                    alert["message_te"] = f"{disease.get('name_te', disease['name'])}కు అనుకూల పరిస్థితులు. నివారణ చర్యలు తీసుకోండి."
                alerts.append(alert)
        
        return alerts


# Singleton instance
_advisory_service = None

def get_crop_advisory_service() -> CropAdvisoryService:
    global _advisory_service
    if _advisory_service is None:
        _advisory_service = CropAdvisoryService()
    return _advisory_service
