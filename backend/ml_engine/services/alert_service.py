"""
Weather Alert Service for KisanMitra
Provides extreme weather alerts and farming advisories.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AlertLevel:
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    SEVERE = "severe"
    CRITICAL = "critical"


class WeatherAlertService:
    """
    Generates weather alerts based on current and forecast data.
    Thresholds are optimized for Indian agriculture.
    """
    
    # Temperature thresholds (Celsius)
    HEAT_WAVE_THRESHOLD = 42
    SEVERE_HEAT_THRESHOLD = 40
    HEAT_STRESS_THRESHOLD = 38
    FROST_WARNING_THRESHOLD = 5
    COLD_STRESS_THRESHOLD = 10
    
    # Rainfall thresholds (mm/day)
    HEAVY_RAIN_THRESHOLD = 100
    MODERATE_RAIN_THRESHOLD = 50
    
    # Humidity thresholds (%)
    DISEASE_RISK_HUMIDITY = 85
    DROUGHT_HUMIDITY = 30
    
    def __init__(self):
        self.alerts_cache = {}
    
    def generate_alerts(self, weather_data: Dict, forecast_data: Dict = None) -> List[Dict]:
        """
        Generate weather alerts based on current and forecast data.
        
        Args:
            weather_data: Current weather {temp, humidity, desc}
            forecast_data: 5-day forecast data
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        temp = weather_data.get("temp", 30)
        humidity = weather_data.get("humidity", 60)
        desc = weather_data.get("desc", "").lower()
        
        # Temperature Alerts
        alerts.extend(self._check_temperature_alerts(temp))
        
        # Humidity Alerts
        alerts.extend(self._check_humidity_alerts(humidity, temp))
        
        # Rainfall Alerts
        if "rain" in desc or "storm" in desc or "thunder" in desc:
            alerts.extend(self._check_rainfall_alerts(desc))
        
        # Forecast-based alerts
        if forecast_data:
            alerts.extend(self._check_forecast_alerts(forecast_data))
        
        # Sort by severity
        severity_order = {AlertLevel.CRITICAL: 0, AlertLevel.SEVERE: 1, 
                         AlertLevel.WARNING: 2, AlertLevel.INFO: 3}
        alerts.sort(key=lambda x: severity_order.get(x["level"], 4))
        
        return alerts
    
    def _check_temperature_alerts(self, temp: float) -> List[Dict]:
        """Check temperature conditions and generate alerts."""
        alerts = []
        
        if temp >= self.HEAT_WAVE_THRESHOLD:
            alerts.append({
                "type": "heat_wave",
                "level": AlertLevel.CRITICAL,
                "title": "HEAT WAVE ALERT",
                "message": f"Extreme heat {temp}°C. Avoid outdoor work 11AM-4PM.",
                "actions": [
                    "Provide shade for livestock",
                    "Irrigate crops early morning/late evening",
                    "Avoid pesticide spraying",
                    "Ensure adequate water for workers"
                ]
            })
        elif temp >= self.SEVERE_HEAT_THRESHOLD:
            alerts.append({
                "type": "severe_heat",
                "level": AlertLevel.SEVERE,
                "title": "Severe Heat Warning",
                "message": f"High temperature {temp}°C. Heat stress risk for crops.",
                "actions": [
                    "Increase irrigation frequency",
                    "Apply mulching to retain moisture",
                    "Avoid transplanting seedlings"
                ]
            })
        elif temp >= self.HEAT_STRESS_THRESHOLD:
            alerts.append({
                "type": "heat_stress",
                "level": AlertLevel.WARNING,
                "title": "Heat Stress Advisory",
                "message": f"Temperature {temp}°C may stress crops.",
                "actions": [
                    "Monitor crop wilting",
                    "Plan irrigation for cooler hours"
                ]
            })
        
        if temp <= self.FROST_WARNING_THRESHOLD:
            alerts.append({
                "type": "frost",
                "level": AlertLevel.CRITICAL,
                "title": "FROST WARNING",
                "message": f"Temperature {temp}°C. Frost damage risk.",
                "actions": [
                    "Cover sensitive crops with plastic/straw",
                    "Irrigate before nightfall (warm soil)",
                    "Delay harvesting if possible",
                    "Protect seedlings and nurseries"
                ]
            })
        elif temp <= self.COLD_STRESS_THRESHOLD:
            alerts.append({
                "type": "cold_stress",
                "level": AlertLevel.WARNING,
                "title": "Cold Weather Advisory",
                "message": f"Low temperature {temp}°C. Cold-sensitive crops at risk.",
                "actions": [
                    "Monitor for cold damage symptoms",
                    "Avoid early morning irrigation"
                ]
            })
        
        return alerts
    
    def _check_humidity_alerts(self, humidity: float, temp: float) -> List[Dict]:
        """Check humidity conditions for disease risk."""
        alerts = []
        
        if humidity >= self.DISEASE_RISK_HUMIDITY:
            alerts.append({
                "type": "disease_risk",
                "level": AlertLevel.WARNING,
                "title": "High Humidity - Disease Risk",
                "message": f"Humidity {humidity}% increases fungal disease risk.",
                "actions": [
                    "Scout for leaf spots/blight symptoms",
                    "Apply preventive fungicide if needed",
                    "Ensure proper plant spacing for airflow",
                    "Avoid overhead irrigation"
                ]
            })
        
        if humidity <= self.DROUGHT_HUMIDITY and temp > 35:
            alerts.append({
                "type": "drought_stress",
                "level": AlertLevel.SEVERE,
                "title": "Drought Stress Conditions",
                "message": f"Low humidity {humidity}% with high temp. Water stress likely.",
                "actions": [
                    "Increase irrigation frequency",
                    "Apply mulch to reduce evaporation",
                    "Consider foliar spray for nutrients"
                ]
            })
        
        return alerts
    
    def _check_rainfall_alerts(self, desc: str) -> List[Dict]:
        """Check rainfall conditions."""
        alerts = []
        
        if "heavy" in desc or "thunder" in desc or "storm" in desc:
            alerts.append({
                "type": "heavy_rain",
                "level": AlertLevel.SEVERE,
                "title": "Heavy Rainfall Alert",
                "message": "Heavy rain expected. Waterlogging risk.",
                "actions": [
                    "Clear drainage channels",
                    "Postpone fertilizer application",
                    "Harvest mature crops if possible",
                    "Protect stored produce from moisture"
                ]
            })
        elif "rain" in desc:
            alerts.append({
                "type": "rain_expected",
                "level": AlertLevel.INFO,
                "title": "Rain Expected",
                "message": "Rainfall predicted. Good for rain-fed crops.",
                "actions": [
                    "Avoid pesticide spraying",
                    "Good time for transplanting",
                    "Prepare for field operations post-rain"
                ]
            })
        
        return alerts
    
    def _check_forecast_alerts(self, forecast_data: Dict) -> List[Dict]:
        """Analyze forecast for upcoming alerts."""
        alerts = []
        daily = forecast_data.get("daily", [])
        
        if not daily:
            return alerts
        
        # Count rain days
        rain_days = 0
        dry_days = 0
        high_temp_days = 0
        
        for day in daily:
            desc = day.get("desc", "").lower()
            temp = day.get("temp", 30)
            
            if "rain" in desc:
                rain_days += 1
            else:
                dry_days += 1
            
            if temp >= 38:
                high_temp_days += 1
        
        # Extended rainfall warning
        if rain_days >= 4:
            alerts.append({
                "type": "extended_rain",
                "level": AlertLevel.WARNING,
                "title": "Extended Rainfall Period",
                "message": f"{rain_days} rain days expected in next 5 days.",
                "actions": [
                    "Ensure proper field drainage",
                    "Stock up on essentials",
                    "Plan indoor farm activities"
                ]
            })
        
        # Dry spell warning
        if dry_days >= 5:
            alerts.append({
                "type": "dry_spell",
                "level": AlertLevel.WARNING,
                "title": "Dry Spell Expected",
                "message": "No rain expected for 5 days. Plan irrigation.",
                "actions": [
                    "Schedule irrigation",
                    "Check water storage levels",
                    "Apply mulching to conserve moisture"
                ]
            })
        
        # Heat wave forecast
        if high_temp_days >= 3:
            alerts.append({
                "type": "heat_wave_forecast",
                "level": AlertLevel.SEVERE,
                "title": "Heat Wave Forecast",
                "message": f"{high_temp_days} extremely hot days expected.",
                "actions": [
                    "Prepare for sustained high temperatures",
                    "Stock irrigation water",
                    "Plan work for cooler hours"
                ]
            })
        
        return alerts
    
    def get_alert_summary(self, alerts: List[Dict]) -> str:
        """Generate text summary of alerts for SMS."""
        if not alerts:
            return "No weather alerts. Conditions normal for farming."
        
        summary = "WEATHER ALERTS:\n"
        for i, alert in enumerate(alerts[:3], 1):  # Top 3 alerts
            summary += f"{i}. {alert['title']}\n"
            summary += f"   {alert['message']}\n"
            if alert.get("actions"):
                summary += f"   Action: {alert['actions'][0]}\n"
        
        return summary


# Singleton
_alert_service = None

def get_alert_service() -> WeatherAlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = WeatherAlertService()
    return _alert_service
