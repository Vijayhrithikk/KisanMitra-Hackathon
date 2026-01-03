"""
Daily Advisory Service for KisanMitra
Combines weather, pest, calendar, and recommendation services into daily farming advice.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from services.weather_service import WeatherService
from services.season_service import SeasonService
from services.alert_service import get_alert_service
from services.pest_warning_service import get_pest_warning_service
from services.crop_calendar_service import get_crop_calendar_service

logger = logging.getLogger(__name__)


class DailyAdvisoryService:
    """
    Generates comprehensive daily farming advisories by combining:
    - Weather alerts
    - Pest warnings
    - Crop calendar activities
    - Seasonal recommendations
    """
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.season_service = SeasonService()
        self.alert_service = get_alert_service()
        self.pest_service = get_pest_warning_service()
        self.calendar_service = get_crop_calendar_service()
    
    def get_daily_advisory(self, lat: float, lon: float, 
                           crop: str = None, sowing_date: datetime = None) -> Dict:
        """
        Generate comprehensive daily advisory.
        
        Args:
            lat: Latitude
            lon: Longitude
            crop: Optional crop name for specific advice
            sowing_date: Optional sowing date for calendar tracking
            
        Returns:
            Complete advisory dictionary
        """
        # Get current weather
        weather = self.weather_service.get_current_weather(lat, lon)
        forecast = self.weather_service.get_forecast(lat, lon)
        
        # Get season
        season = self.season_service.get_season()
        season_details = self.season_service.get_current_season_details()
        
        # Generate weather alerts
        alerts = self.alert_service.generate_alerts(weather, forecast)
        
        # Generate pest warnings if crop specified
        pest_warnings = []
        if crop:
            recent_rain = "rain" in weather.get("desc", "").lower()
            pest_warnings = self.pest_service.get_pest_warnings(
                crop, weather["temp"], weather["humidity"], season, recent_rain
            )
        
        # Get calendar activities if crop and sowing date specified
        calendar_info = None
        upcoming_activities = []
        if crop:
            calendar_info = self.calendar_service.get_optimal_sowing_window(crop, season)
            if sowing_date:
                upcoming_activities = self.calendar_service.get_upcoming_activities(
                    crop, sowing_date, season, days_ahead=7
                )
                harvest_info = self.calendar_service.get_harvest_date(crop, sowing_date, season)
            else:
                harvest_info = None
        else:
            harvest_info = None
        
        # Generate daily tasks
        daily_tasks = self._generate_daily_tasks(
            weather, alerts, pest_warnings, upcoming_activities, season
        )
        
        # Build advisory
        advisory = {
            "date": datetime.now().strftime("%d %B %Y"),
            "time": datetime.now().strftime("%I:%M %p"),
            "location": {"lat": lat, "lon": lon},
            "weather": {
                "current": weather,
                "forecast_5day": forecast.get("daily", [])[:5],
                "seasonal": forecast.get("seasonal", {})
            },
            "season": season_details,
            "alerts": alerts[:5],  # Top 5 alerts
            "daily_tasks": daily_tasks,
            "priority_action": self._get_priority_action(alerts, pest_warnings, daily_tasks)
        }
        
        if crop:
            advisory["crop_specific"] = {
                "crop": crop,
                "pest_warnings": pest_warnings[:3],  # Top 3 pest risks
                "calendar": calendar_info,
                "upcoming_activities": upcoming_activities,
                "harvest_info": harvest_info
            }
        
        return advisory
    
    def _generate_daily_tasks(self, weather: Dict, alerts: List[Dict],
                               pest_warnings: List[Dict], activities: List[Dict],
                               season: str) -> List[Dict]:
        """Generate prioritized daily tasks."""
        tasks = []
        
        # Weather-based tasks
        temp = weather.get("temp", 30)
        humidity = weather.get("humidity", 60)
        desc = weather.get("desc", "").lower()
        
        # Morning tasks
        if temp < 35:
            tasks.append({
                "priority": "high",
                "time": "6:00 - 9:00 AM",
                "task": "Field inspection and irrigation",
                "reason": "Cool morning hours ideal for field work"
            })
        
        if "rain" not in desc and humidity < 70:
            tasks.append({
                "priority": "medium",
                "time": "7:00 - 10:00 AM",
                "task": "Pesticide/Fertilizer application",
                "reason": "Dry conditions suitable for spraying"
            })
        elif "rain" in desc:
            tasks.append({
                "priority": "low",
                "time": "Morning",
                "task": "Postpone spraying - rain expected",
                "reason": "Rainfall will wash away chemicals"
            })
        
        # Add calendar activities
        for act in activities[:2]:
            tasks.append({
                "priority": "high",
                "time": f"Due in {act['days_until']} days",
                "task": act["activity"],
                "reason": f"As per crop calendar (Day {act['day_after_sowing']})"
            })
        
        # Add pest-related tasks
        high_risk_pests = [p for p in pest_warnings if p["risk_level"] in ["CRITICAL", "HIGH"]]
        for pest in high_risk_pests[:1]:
            tasks.append({
                "priority": "critical",
                "time": "Today",
                "task": f"Scout for {pest['pest']}",
                "reason": f"High risk based on current conditions. Look for: {pest['symptoms']}"
            })
        
        # Alert-based tasks
        for alert in alerts[:2]:
            if alert["level"] in ["critical", "severe"]:
                if alert.get("actions"):
                    tasks.append({
                        "priority": "critical",
                        "time": "Immediate",
                        "task": alert["actions"][0],
                        "reason": alert["message"]
                    })
        
        # Evening tasks
        tasks.append({
            "priority": "low",
            "time": "4:00 - 6:00 PM",
            "task": "Evening irrigation if needed",
            "reason": "Cooler hours reduce evaporation loss"
        })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return tasks[:6]  # Return top 6 tasks
    
    def _get_priority_action(self, alerts: List[Dict], pest_warnings: List[Dict],
                              tasks: List[Dict]) -> str:
        """Get the single most important action for today."""
        # Check for critical alerts first
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        if critical_alerts:
            return critical_alerts[0]["actions"][0] if critical_alerts[0].get("actions") else critical_alerts[0]["message"]
        
        # Check for critical pest risk
        critical_pests = [p for p in pest_warnings if p["risk_level"] == "CRITICAL"]
        if critical_pests:
            return f"SCOUT for {critical_pests[0]['pest']} - High outbreak risk!"
        
        # Check for high priority tasks
        high_tasks = [t for t in tasks if t["priority"] in ["critical", "high"]]
        if high_tasks:
            return high_tasks[0]["task"]
        
        return "Regular monitoring and field maintenance"
    
    def get_sms_advisory(self, lat: float, lon: float, crop: str = None) -> str:
        """Generate SMS-friendly daily advisory."""
        advisory = self.get_daily_advisory(lat, lon, crop)
        
        text = f"DAILY FARM ADVISORY\n"
        text += f"{advisory['date']}\n"
        text += "=" * 20 + "\n\n"
        
        # Weather summary
        weather = advisory["weather"]["current"]
        text += f"Weather: {weather['temp']:.0f}C, {weather['humidity']}% humidity\n"
        text += f"{weather['desc']}\n\n"
        
        # Priority action
        text += f"PRIORITY: {advisory['priority_action']}\n\n"
        
        # Top 3 tasks
        text += "TODAY'S TASKS:\n"
        for i, task in enumerate(advisory["daily_tasks"][:3], 1):
            text += f"{i}. {task['task']}\n"
            text += f"   ({task['time']})\n"
        
        # Alerts if any
        if advisory["alerts"]:
            text += f"\nALERT: {advisory['alerts'][0]['title']}\n"
        
        return text


# Singleton
_advisory_service = None

def get_daily_advisory_service() -> DailyAdvisoryService:
    global _advisory_service
    if _advisory_service is None:
        _advisory_service = DailyAdvisoryService()
    return _advisory_service
