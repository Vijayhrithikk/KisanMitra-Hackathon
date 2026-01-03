import json
import os

# Soil type mapping from research output to crop profile format
SOIL_MAPPING = {
    "Black Cotton": ["Black", "Clayey"],
    "Black Soil": ["Black", "Clayey"],
    "Red Soil": ["Red"],
    "Red Sandy Loam": ["Red", "Sandy", "Loamy"],
    "Red Loam": ["Red", "Loamy"],
    "Alluvial": ["Alluvial", "Loamy"],
    "Laterite": ["Red", "Sandy"],
    "Sandy Loam": ["Sandy", "Loamy"],
    "Sandy": ["Sandy"],
    "Loamy": ["Loamy"],
    "Clay": ["Clayey"],
    "Forest Soil": ["Loamy"],
    "Mountain Soil": ["Loamy", "Sandy"],
    "Saline": ["Clayey"],
    "Alkaline": ["Clayey", "Loamy"],
}


class RecommendationService:
    def __init__(self):
        self.profiles_path = os.path.join(os.path.dirname(__file__), '../data/crop_profiles.json')
        self.profiles = self._load_profiles()

    def _load_profiles(self):
        try:
            with open(self.profiles_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading crop profiles: {e}")
            return {}

    def _normalize_soil_type(self, soil_type):
        """Map researched soil type to profile-compatible types."""
        if not soil_type:
            return ["Loamy"]
        
        # Try exact match
        if soil_type in SOIL_MAPPING:
            return SOIL_MAPPING[soil_type]
        
        # Try partial match
        soil_lower = soil_type.lower()
        for key, values in SOIL_MAPPING.items():
            if key.lower() in soil_lower or soil_lower in key.lower():
                return values
        
        # Fallback
        return ["Loamy"]

    def _analyze_forecast(self, forecast_data):
        """Analyze 5-day forecast for crop recommendations."""
        if not forecast_data or 'daily' not in forecast_data:
            return {"rain_days": 0, "avg_temp": 28, "temp_trend": "stable", "weather_risk": "Low"}
        
        daily = forecast_data['daily']
        if not daily:
            return {"rain_days": 0, "avg_temp": 28, "temp_trend": "stable", "weather_risk": "Low"}
        
        # Count rain days
        rain_keywords = ['rain', 'drizzle', 'shower', 'thunderstorm']
        rain_days = sum(1 for d in daily if any(r in d.get('desc', '').lower() for r in rain_keywords))
        
        # Average temperature
        temps = [d.get('temp', 28) for d in daily]
        avg_temp = sum(temps) / len(temps) if temps else 28
        
        # Temperature trend
        if len(temps) >= 3:
            first_half = sum(temps[:len(temps)//2]) / (len(temps)//2)
            second_half = sum(temps[len(temps)//2:]) / (len(temps) - len(temps)//2)
            if second_half > first_half + 2:
                temp_trend = "rising"
            elif second_half < first_half - 2:
                temp_trend = "falling"
            else:
                temp_trend = "stable"
        else:
            temp_trend = "stable"
        
        # Weather risk assessment
        if rain_days >= 4:
            weather_risk = "High" if avg_temp > 30 else "Medium"
        elif rain_days == 0 and avg_temp > 35:
            weather_risk = "High"
        else:
            weather_risk = "Low"
        
        return {
            "rain_days": rain_days,
            "avg_temp": round(avg_temp, 1),
            "temp_trend": temp_trend,
            "weather_risk": weather_risk
        }

    def get_recommendations(self, soil_type, season, temp=None, humidity=None, 
                           soil_ph=7.0, soil_n=150, soil_p=50, soil_k=150,
                           forecast=None, soil_source="database"):
        """
        Enhanced crop recommendations with weather forecast awareness.
        
        Args:
            soil_type: Soil type (will be normalized)
            season: Current season
            temp: Current temperature
            humidity: Current humidity
            soil_ph, soil_n, soil_p, soil_k: Soil parameters
            forecast: 5-day weather forecast data
            soil_source: Source of soil data ("database", "ai_researched", "fallback")
        """
        recommendations = []
        
        # Normalize soil type for matching
        normalized_soils = self._normalize_soil_type(soil_type)
        
        # Analyze forecast
        forecast_analysis = self._analyze_forecast(forecast)
        
        for crop_name, profile in self.profiles.items():
            score = 100
            reasons = []
            warnings = []
            forecast_insight = None
            
            # 1. Season Filter (Strict)
            if season not in profile["season"]:
                continue

            # 2. Soil Suitability - Check DIRECT match first, then normalized
            profile_soils = profile["soil_suitability"]
            soil_match = False
            
            # Direct match (e.g., "Black Cotton" in ["Black Cotton", "Loamy"])
            if soil_type in profile_soils:
                soil_match = True
            else:
                # Normalized match (e.g., "Black Cotton" -> ["Black", "Clayey"])
                soil_match = any(s in profile_soils for s in normalized_soils)
            
            if not soil_match:
                score -= 25
                warnings.append(f"Not ideal for {soil_type} soil")
            else:
                reasons.append(f"Excellent match for {soil_type} soil")
            
            # 3. pH Suitability
            if not (profile["ph_min"] <= soil_ph <= profile["ph_max"]):
                score -= 20
                warnings.append(f"pH {soil_ph} outside optimal ({profile['ph_min']}-{profile['ph_max']})")
            else:
                reasons.append(f"pH {soil_ph} is optimal")
            
            # 4. Temperature Suitability (current + forecast trend)
            if temp:
                if not (profile["min_temp"] - 5 <= temp <= profile["max_temp"] + 5):
                    score -= 30
                    warnings.append(f"Temp {temp}°C risky (Optimal: {profile['min_temp']}-{profile['max_temp']}°C)")
                
                # Factor in forecast trend
                if forecast_analysis["temp_trend"] == "rising" and temp > profile["max_temp"] - 5:
                    score -= 10
                    warnings.append("Temperature rising - heat stress risk")
                elif forecast_analysis["temp_trend"] == "falling" and temp < profile["min_temp"] + 5:
                    score -= 10
                    warnings.append("Temperature dropping - cold stress risk")
            
            # 5. Rainfall/Water needs alignment
            water_needs = profile["water_needs"]
            rain_days = forecast_analysis["rain_days"]
            
            if water_needs == "High" and rain_days >= 3:
                score += 10
                forecast_insight = f"Favorable: {rain_days} rain days expected"
            elif water_needs == "Low" and rain_days >= 4:
                score -= 15
                warnings.append(f"Too much rain expected ({rain_days} days)")
                forecast_insight = f"Caution: {rain_days} rain days may cause issues"
            elif water_needs == "High" and rain_days == 0:
                warnings.append("No rain expected - plan for irrigation")
                forecast_insight = "Irrigation needed: No rain predicted"
            
            # 6. Nutrient Analysis
            fertilizer_tip = profile.get("fertilizer_recommendation", "")
            
            if soil_n < 150 and profile["n_needs"] == "High":
                score -= 10
                fertilizer_tip += " Soil N is low; Apply extra Urea."
            elif soil_n > 300 and profile["n_needs"] == "Low":
                score += 5
                reasons.append("Good choice to utilize high Soil N.")

            if soil_p < 30 and profile["p_needs"] == "High":
                fertilizer_tip += " Soil P is low; Use DAP/SSP."

            if soil_k < 150 and profile["k_needs"] == "High":
                fertilizer_tip += " Soil K is low; Apply MOP."

            # 7. Crop Rotation / Soil Health Bonus
            if soil_n < 120 and crop_name in ["Pulses", "Ground Nuts"]:
                score += 20
                reasons.append("Fixes atmospheric Nitrogen, improving soil health.")

            # 8. AI-researched soil confidence boost
            if soil_source == "ai_researched" and soil_match:
                score += 5  # Trust bonus for intelligent matching
                reasons.append("Verified soil match from AI research")

            # Final Decision
            if score > 40:
                rec = {
                    "crop": crop_name,
                    "confidence": max(0, min(100, score)),
                    "yield_potential": profile["yield_potential"],
                    "risk_factor": profile["risk"],
                    "water_needs": profile["water_needs"],
                    "reason": ". ".join(reasons) if reasons else profile["description"],
                    "fertilizer_recommendation": fertilizer_tip.strip(),
                    "warnings": warnings
                }
                
                if forecast_insight:
                    rec["forecast_insight"] = forecast_insight
                
                recommendations.append(rec)

        # Sort by Confidence -> Yield -> Risk
        recommendations.sort(key=lambda x: (
            x["confidence"], 
            x["yield_potential"] == "High", 
            x["risk_factor"] == "Low"
        ), reverse=True)

        return recommendations

    def get_weather_summary(self, forecast_analysis):
        """Generate human-readable weather summary."""
        rain = forecast_analysis["rain_days"]
        temp = forecast_analysis["avg_temp"]
        trend = forecast_analysis["temp_trend"]
        
        if rain >= 3:
            rain_text = "Heavy rain expected"
        elif rain >= 1:
            rain_text = "Moderate rain expected"
        else:
            rain_text = "Dry conditions expected"
        
        if temp > 35:
            temp_text = "very hot"
        elif temp > 30:
            temp_text = "warm"
        elif temp > 20:
            temp_text = "moderate"
        else:
            temp_text = "cool"
        
        trend_text = f"({trend} trend)" if trend != "stable" else ""
        
        return f"{rain_text}. {temp_text.capitalize()} temperatures {trend_text}".strip()
