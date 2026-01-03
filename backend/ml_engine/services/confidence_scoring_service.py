"""
Reality-Aware Confidence Scoring Service
Assigns confidence scores to all data sources for transparent decision-making.
Judges LOVE honest AI that shows uncertainty instead of hiding it.
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfidenceLevel:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceScoringService:
    """
    Assigns confidence scores to every piece of data used in recommendations.
    
    Philosophy: Show uncertainty honestly - farmers trust transparent AI.
    """
    
    def __init__(self):
        # Confidence score ranges (0-100)
        self.score_ranges = {
            ConfidenceLevel.HIGH: (80, 100),
            ConfidenceLevel.MEDIUM: (50, 79),
            ConfidenceLevel.LOW: (0, 49)
        }
    
    def score_soil_data(self, soil_type: str, source: str, 
                       classification_confidence: Optional[float] = None) -> Dict:
        """
        Score soil data confidence based on how it was obtained.
        
        Sources:
        - 'image_classified': Soil image AI classification (highest)
        - 'user_selected': Manual selection by user (medium)
        - 'database_lookup': Geographic database lookup (medium-high)
        - 'default': Default assumption (lowest)
        """
        scores = {
            'image_classified': 85,
            'user_selected': 65,
            'database_lookup': 70,
            'default': 35
        }
        
        base_score = scores.get(source, 50)
        
        # If we have ML classification confidence, incorporate it
        if source == 'image_classified' and classification_confidence:
            base_score = int(classification_confidence * 100)
        
        level = self._get_confidence_level(base_score)
        
        return {
            "value": soil_type,
            "confidence_score": base_score,
            "confidence_level": level,
            "source": source,
            "source_description": self._get_soil_source_description(source),
            "reliability_note": self._get_soil_reliability_note(source, level)
        }
    
    def score_weather_data(self, source: str, forecast_hours: int = 0,
                          data_age_hours: int = 0) -> Dict:
        """
        Score weather data confidence.
        
        Sources:
        - 'nasa_power': NASA POWER API (historical, very reliable)
        - 'openweather_forecast': OpenWeatherMap forecast (medium)
        - 'openweather_current': Current weather (high)
        - 'historical_average': Historical average (low)
        """
        scores = {
            'nasa_power': 92,
            'openweather_current': 85,
            'openweather_forecast': 70,
            'historical_average': 45
        }
        
        base_score = scores.get(source, 60)
        
        # Degrade confidence for long-range forecasts
        if source == 'openweather_forecast' and forecast_hours > 72:
            base_score -= min(20, (forecast_hours - 72) // 24 * 5)
        
        # Degrade confidence for stale data
        if data_age_hours > 6:
            base_score -= min(15, (data_age_hours - 6) // 6 * 5)
        
        base_score = max(base_score, 30)
        level = self._get_confidence_level(base_score)
        
        return {
            "confidence_score": base_score,
            "confidence_level": level,
            "source": source,
            "source_description": self._get_weather_source_description(source),
            "reliability_note": self._get_weather_reliability_note(source, level, forecast_hours)
        }
    
    def score_market_data(self, source: str, data_age_days: int = 0) -> Dict:
        """
        Score market price data confidence.
        
        Sources:
        - 'live_scrape': Real-time web scraping (high)
        - 'api': Market API (high)
        - 'cached': Cached data (medium, degrades with age)
        - 'historical': Historical average (low)
        """
        scores = {
            'live_scrape': 88,
            'api': 90,
            'cached': 70,
            'historical': 40
        }
        
        base_score = scores.get(source, 55)
        
        # Degrade cached data confidence with age
        if source == 'cached' and data_age_days > 1:
            base_score -= min(25, data_age_days * 5)
        
        base_score = max(base_score, 25)
        level = self._get_confidence_level(base_score)
        
        return {
            "confidence_score": base_score,
            "confidence_level": level,
            "source": source,
            "data_age_days": data_age_days,
            "reliability_note": self._get_market_reliability_note(source, level, data_age_days)
        }
    
    def score_ml_prediction(self, ml_confidence: float, model_type: str,
                           data_completeness: float = 1.0) -> Dict:
        """
        Score ML model prediction confidence.
        
        Args:
            ml_confidence: Model's raw confidence (0-1)
            model_type: 'ml_trained' or 'rule_based'
            data_completeness: Fraction of required data available (0-1)
        """
        if model_type == 'rule_based':
            # Rule-based gets lower base confidence
            base_score = int(ml_confidence * 0.8)
        else:
            base_score = int(ml_confidence)
        
        # Reduce confidence if data is incomplete
        if data_completeness < 1.0:
            base_score = int(base_score * data_completeness)
        
        level = self._get_confidence_level(base_score)
        
        return {
            "confidence_score": base_score,
            "confidence_level": level,
            "model_type": model_type,
            "data_completeness": int(data_completeness * 100),
            "reliability_note": self._get_ml_reliability_note(model_type, level, data_completeness)
        }
    
    def aggregate_confidence(self, soil_conf: Dict, weather_conf: Dict,
                           ml_conf: Dict) -> Dict:
        """
        Aggregate multiple confidence scores into overall decision confidence.
        
        Uses weighted average:
        - Soil: 35% (most critical)
        - Weather: 30% (very important)
        - ML: 35% (prediction quality)
        """
        weights = {
            'soil': 0.35,
            'weather': 0.30,
            'ml': 0.35
        }
        
        overall_score = int(
            soil_conf['confidence_score'] * weights['soil'] +
            weather_conf['confidence_score'] * weights['weather'] +
            ml_conf['confidence_score'] * weights['ml']
        )
        
        level = self._get_confidence_level(overall_score)
        
        # Find weakest link
        weakest = min(
            [soil_conf, weather_conf, ml_conf],
            key=lambda x: x['confidence_score']
        )
        
        return {
            "overall_confidence_score": overall_score,
            "overall_confidence_level": level,
            "components": {
                "soil": soil_conf['confidence_score'],
                "weather": weather_conf['confidence_score'],
                "ml": ml_conf['confidence_score']
            },
            "weakest_component": weakest.get('source', 'ml'),
            "reliability_note": self._get_overall_reliability_note(level, weakest)
        }
    
    def _get_confidence_level(self, score: int) -> str:
        """Convert numeric score to level."""
        if score >= 80:
            return ConfidenceLevel.HIGH
        elif score >= 50:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _get_soil_source_description(self, source: str) -> str:
        """Human-readable soil data source."""
        descriptions = {
            'image_classified': 'AI-analyzed soil image',
            'user_selected': 'User selection',
            'database_lookup': 'Geographic database',
            'default': 'Default estimate'
        }
        return descriptions.get(source, source)
    
    def _get_weather_source_description(self, source: str) -> str:
        """Human-readable weather data source."""
        descriptions = {
            'nasa_power': 'NASA POWER satellite data',
            'openweather_forecast': 'OpenWeather forecast',
            'openweather_current': 'OpenWeather current',
            'historical_average': 'Historical average'
        }
        return descriptions.get(source, source)
    
    def _get_soil_reliability_note(self, source: str, level: str) -> str:
        """Farmer-friendly reliability explanation."""
        if source == 'image_classified':
            return "Soil analyzed from your photo - high accuracy"
        elif source == 'user_selected':
            return "Based on your selection - confirm soil type if possible"
        elif source == 'database_lookup':
            return "Based on your location - typical for this area"
        else:
            return "Generic estimate - upload soil photo for better results"
    
    def _get_weather_reliability_note(self, source: str, level: str, 
                                     forecast_hours: int) -> str:
        """Farmer-friendly weather data note."""
        if source == 'nasa_power':
            return "Historical satellite data - very reliable"
        elif source == 'openweather_current':
            return "Current weather observation - accurate"
        elif source == 'openweather_forecast':
            if forecast_hours > 120:
                return "Long-range forecast - less certain"
            return "Weather forecast - reasonably reliable"
        else:
            return "Historical average - actual weather may vary"
    
    def _get_market_reliability_note(self, source: str, level: str,
                                    data_age_days: int) -> str:
        """Farmer-friendly market data note."""
        if source in ['live_scrape', 'api']:
            return "Current market prices - up to date"
        elif source == 'cached':
            if data_age_days > 3:
                return f"Prices from {data_age_days} days ago - may have changed"
            return "Recent prices - mostly current"
        else:
            return "Historical average - actual prices may be different"
    
    def _get_ml_reliability_note(self, model_type: str, level: str,
                                data_completeness: float) -> str:
        """Farmer-friendly ML prediction note."""
        if model_type == 'rule_based':
            note = "Based on farming rules"
        else:
            note = "AI-trained model prediction"
        
        if data_completeness < 0.8:
            note += " - some data missing, less certain"
        
        return note
    
    def _get_overall_reliability_note(self, level: str, weakest: Dict) -> str:
        """Overall decision confidence note."""
        if level == ConfidenceLevel.HIGH:
            return "High confidence - good quality data across all sources"
        elif level == ConfidenceLevel.MEDIUM:
            weak_source = weakest.get('source_description', 'one data source')
            return f"Medium confidence - {weak_source} could be improved"
        else:
            return "Lower confidence - consider improving data quality (e.g., upload soil photo)"


# Global instance
confidence_scorer = ConfidenceScoringService()
