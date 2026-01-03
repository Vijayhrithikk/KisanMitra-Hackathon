"""
Decision Simulator Service - The Hackathon Game-Changer
Multi-option risk comparison engine that prevents farming losses.

Philosophy: Don't just recommend - simulate outcomes and prevent mistakes.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class DecisionSimulatorService:
    """
    Core Innovation: Pre-farming risk simulator for small farmers.
    
    Like flight simulators for pilots, but for agriculture decisions.
    Shows side-by-side comparison of crop options with loss probabilities.
    """
    
    def __init__(self):
        # Risk calculation parameters
        self.risk_weights = {
            'weather_failure': 0.40,  # 40% weight to weather risk
            'market_volatility': 0.25,  # 25% weight to market risk
            'pest_disease': 0.20,      # 20% weight to pest risk
            'input_cost': 0.15         # 15% weight to cost risk
        }
    
    def simulate_decision(self, recommendations: List[Dict], 
                         weather_forecast: Dict,
                         soil_params: Dict,
                         context: Dict) -> List[Dict]:
        """
        Core method: Simulate outcomes for all crop options.
        
        Args:
            recommendations: List of crop recommendations from ML service
            weather_forecast: Weather forecast data
            soil_params: Soil parameters (pH, NPK)
            context: Additional context (location, season, etc.)
        
        Returns:
            Enhanced recommendations with risk analysis and loss probabilities
        """
        enhanced_recs = []
        
        for rec in recommendations:
            # Calculate comprehensive risk profile
            risk_profile = self._calculate_risk_profile(
                crop=rec['crop'],
                weather_forecast=weather_forecast,
                soil_params=soil_params,
                yield_potential=rec.get('yield_potential', 'Medium'),
                water_needs=rec.get('water_needs', 'Medium')
            )
            
            # Calculate loss probability
            loss_probability = self._calculate_loss_probability(
                risk_profile=risk_profile,
                confidence=rec.get('confidence', 70)
            )
            
            # Generate comparative insight
            comparative_insight = self._generate_comparative_insight(
                crop=rec['crop'],
                risk_profile=risk_profile,
                loss_probability=loss_probability
            )
            
            # Enhance recommendation
            enhanced_rec = {
                **rec,
                'risk_analysis': {
                    'loss_probability': loss_probability,
                    'loss_probability_category': self._categorize_loss_probability(loss_probability),
                    'risk_breakdown': risk_profile,
                    'dominant_risk': self._get_dominant_risk(risk_profile),
                    'risk_level': self._categorize_overall_risk(loss_probability)
                },
                'decision_grade': {
                    'recommendation_strength': self._get_recommendation_strength(loss_probability, rec.get('confidence', 70)),
                    'comparative_insight': comparative_insight,
                    'suitability_score': self._calculate_suitability_score(loss_probability, rec.get('confidence', 70))
                }
            }
            
            enhanced_recs.append(enhanced_rec)
        
        # Sort by suitability score (best first)
        enhanced_recs.sort(
            key=lambda x: x['decision_grade']['suitability_score'],
            reverse=True
        )
        
        # Add relative comparison
        for idx, rec in enumerate(enhanced_recs):
            rec['decision_grade']['rank'] = idx + 1
            rec['decision_grade']['rank_label'] = self._get_rank_label(idx + 1)
        
        return enhanced_recs
    
    def _calculate_risk_profile(self, crop: str, weather_forecast: Dict,
                               soil_params: Dict, yield_potential: str,
                               water_needs: str) -> Dict:
        """
        Calculate comprehensive risk breakdown.
        
        Returns risk scores for: weather, market, pest, input cost
        """
        # Weather Risk Calculation
        weather_risk = self._calculate_weather_risk(
            crop=crop,
            forecast=weather_forecast,
            water_needs=water_needs
        )
        
        # Market Risk Calculation
        market_risk = self._calculate_market_risk(
            crop=crop,
            yield_potential=yield_potential
        )
        
        # Pest & Disease Risk
        pest_risk = self._calculate_pest_risk(
            crop=crop,
            weather_forecast=weather_forecast
        )
        
        # Input Cost Risk
        cost_risk = self._calculate_cost_risk(
            crop=crop,
            soil_params=soil_params
        )
        
        return {
            'weather_risk': weather_risk,
            'market_risk': market_risk,
            'pest_risk': pest_risk,
            'cost_risk': cost_risk
        }
    
    def _calculate_weather_risk(self, crop: str, forecast: Dict,
                               water_needs: str) -> Dict:
        """
        Calculate weather-related risk.
        
        Considers:
        - Rainfall adequacy
        - Temperature extremes
        - Humidity issues
        """
        risk_score = 30  # Base risk
        risk_factors = []
        
        # Rainfall analysis
        rain_days = forecast.get('rain_days', 0)
        total_rainfall = forecast.get('total_rainfall', 0)
        
        if water_needs == 'High':
            if rain_days < 3:
                risk_score += 30
                risk_factors.append("Insufficient rainfall expected")
            elif total_rainfall < 50:
                risk_score += 20
                risk_factors.append("Low total rainfall")
        elif water_needs == 'Low':
            if rain_days > 6:
                risk_score += 15
                risk_factors.append("Excessive rain expected")
        
        # Temperature analysis
        avg_temp = forecast.get('avg_temp', 28)
        if avg_temp > 35:
            risk_score += 15
            risk_factors.append("High temperature stress")
        elif avg_temp < 15:
            risk_score += 10
            risk_factors.append("Low temperature risk")
        
        risk_score = min(risk_score, 100)
        
        return {
            'score': risk_score,
            'level': self._score_to_level(risk_score),
            'factors': risk_factors,
            'description': self._get_weather_risk_description(risk_score, water_needs, rain_days)
        }
    
    def _calculate_market_risk(self, crop: str, yield_potential: str) -> Dict:
        """
        Calculate market price volatility risk.
        
        High-value crops tend to have higher price volatility.
        """
        # Market volatility by crop type (simplified model)
        volatility_map = {
            'Cotton': 65,
            'Tobacco': 70,
            'Chilli': 60,
            'Turmeric': 55,
            'Sunflower': 50,
            'Rice': 30,
            'Maize': 35,
            'Pulses': 40,
            'Groundnut': 45
        }
        
        base_risk = volatility_map.get(crop, 45)
        
        # High yield crops have more market exposure
        if yield_potential == 'High':
            base_risk += 10
        
        risk_factors = []
        if base_risk > 60:
            risk_factors.append("High price volatility")
        if yield_potential == 'High':
            risk_factors.append("Higher market exposure")
        
        return {
            'score': base_risk,
            'level': self._score_to_level(base_risk),
            'factors': risk_factors,
            'description': self._get_market_risk_description(base_risk, crop)
        }
    
    def _calculate_pest_risk(self, crop: str, weather_forecast: Dict) -> Dict:
        """
        Calculate pest and disease risk.
        
        Higher humidity and temperature favor pest outbreaks.
        """
        base_risk = {
            'Cotton': 60,  # Bollworm, whitefly
            'Rice': 50,    # Brown planthopper, blast
            'Chilli': 55,  # Thrips, mites
            'Tomato': 65,  # Multiple pests
            'Maize': 40,
            'Pulses': 35
        }.get(crop, 40)
        
        # Weather impact on pest risk
        humidity = weather_forecast.get('avg_humidity', 60)
        temp = weather_forecast.get('avg_temp', 28)
        
        if humidity > 70 and 25 < temp < 32:
            base_risk += 15
            risk_factor = "High humidity favors pests"
        else:
            risk_factor = "Moderate pest pressure"
        
        return {
            'score': min(base_risk, 100),
            'level': self._score_to_level(base_risk),
            'factors': [risk_factor],
            'description': self._get_pest_risk_description(base_risk, crop)
        }
    
    def _calculate_cost_risk(self, crop: str, soil_params: Dict) -> Dict:
        """
        Calculate input cost risk.
        
        Poor soil requires more fertilizer = higher cost risk.
        """
        base_cost_risk = {
            'Cotton': 55,
            'Sugarcane': 60,
            'Banana': 65,
            'Rice': 50,
            'Pulses': 30,
            'Millets': 25
        }.get(crop, 40)
        
        # Soil quality impact
        n_level = soil_params.get('n', 150)
        p_level = soil_params.get('p', 50)
        k_level = soil_params.get('k', 150)
        
        # Low nutrients = higher fertilizer cost
        if n_level < 100 or p_level < 30 or k_level < 100:
            base_cost_risk += 15
            risk_factor = "Low soil nutrients increase fertilizer costs"
        else:
            risk_factor = "Adequate soil nutrients"
        
        return {
            'score': min(base_cost_risk, 100),
            'level': self._score_to_level(base_cost_risk),
            'factors': [risk_factor],
            'description': self._get_cost_risk_description(base_cost_risk, crop)
        }
    
    def _calculate_loss_probability(self, risk_profile: Dict, confidence: int) -> int:
        """
        Calculate overall loss probability (0-100%).
        
        Weighted aggregation of all risk factors.
        """
        weighted_risk = (
            risk_profile['weather_risk']['score'] * self.risk_weights['weather_failure'] +
            risk_profile['market_risk']['score'] * self.risk_weights['market_volatility'] +
            risk_profile['pest_risk']['score'] * self.risk_weights['pest_disease'] +
            risk_profile['cost_risk']['score'] * self.risk_weights['input_cost']
        )
        
        # Adjust by prediction confidence
        # Low confidence = higher uncertainty = higher perceived risk
        confidence_adjustment = (100 - confidence) * 0.2
        
        loss_prob = int(weighted_risk + confidence_adjustment)
        return min(max(loss_prob, 5), 95)  # Keep in 5-95% range
    
    def _categorize_loss_probability(self, loss_prob: int) -> str:
        """Categorize loss probability for UI display."""
        if loss_prob < 25:
            return "Very Low"
        elif loss_prob < 40:
            return "Low"
        elif loss_prob < 60:
            return "Moderate"
        elif loss_prob < 75:
            return "High"
        else:
            return "Very High"
    
    def _categorize_overall_risk(self, loss_prob: int) -> str:
        """Map loss probability to risk level."""
        if loss_prob < 30:
            return "Low"
        elif loss_prob < 60:
            return "Medium"
        else:
            return "High"
    
    def _get_dominant_risk(self, risk_profile: Dict) -> str:
        """Identify the highest risk factor."""
        risks = {
            'Weather': risk_profile['weather_risk']['score'],
            'Market': risk_profile['market_risk']['score'],
            'Pest': risk_profile['pest_risk']['score'],
            'Cost': risk_profile['cost_risk']['score']
        }
        return max(risks, key=risks.get)
    
    def _calculate_suitability_score(self, loss_prob: int, confidence: int) -> int:
        """
        Calculate overall suitability score (0-100).
        
        Higher score = better option.
        """
        # Inverse of loss probability + confidence
        return int(((100 - loss_prob) * 0.6) + (confidence * 0.4))
    
    def _get_recommendation_strength(self, loss_prob: int, confidence: int) -> str:
        """Get human-readable recommendation strength."""
        suitability = self._calculate_suitability_score(loss_prob, confidence)
        
        if suitability >= 75:
            return "Strongly Recommended"
        elif suitability >= 60:
            return "Recommended"
        elif suitability >= 45:
            return "Consider with Caution"
        else:
            return "Not Recommended"
    
    def _get_rank_label(self, rank: int) -> str:
        """Get rank label for display."""
        labels = {
            1: "Best Option",
            2: "Good Alternative",
            3: "Viable Option"
        }
        return labels.get(rank, "Alternative")
    
    def _generate_comparative_insight(self, crop: str, risk_profile: Dict,
                                     loss_probability: int) -> str:
        """
        Generate comparative insight for farmers.
        
        Examples:
        - "Safest option with lowest loss risk"
        - "Higher yield but weather-dependent"
        """
        dominant_risk = self._get_dominant_risk(risk_profile)
        
        if loss_probability < 25:
            return f"Safest choice with minimal {dominant_risk.lower()} risk"
        elif loss_probability < 40:
            return f"Good option, watch for {dominant_risk.lower()} conditions"
        elif loss_probability < 60:
            return f"Moderate risk due to {dominant_risk.lower()} uncertainty"
        else:
            return f"Higher risk - {dominant_risk.lower()} conditions unfavorable"
    
    def _score_to_level(self, score: int) -> str:
        """Convert numeric risk score to level."""
        if score < 30:
            return "Low"
        elif score < 60:
            return "Medium"
        else:
            return "High"
    
    def _get_weather_risk_description(self, score: int, water_needs: str,
                                     rain_days: int) -> str:
        """Farmer-friendly weather risk description."""
        if water_needs == 'High' and rain_days < 3:
            return f"High water needs but only {rain_days} rain days expected"
        elif score < 30:
            return "Weather conditions favorable"
        elif score < 60:
            return "Some weather uncertainty expected"
        else:
            return "Weather conditions may be challenging"
    
    def _get_market_risk_description(self, score: int, crop: str) -> str:
        """Farmer-friendly market risk description."""
        if score >= 60:
            return f"{crop} prices can fluctuate significantly"
        elif score >= 40:
            return "Moderate price stability expected"
        else:
            return "Stable market prices likely"
    
    def _get_pest_risk_description(self, score: int, crop: str) -> str:
        """Farmer-friendly pest risk description."""
        if score >= 60:
            return f"{crop} requires regular pest monitoring"
        elif score >= 40:
            return "Standard pest management needed"
        else:
            return "Low pest pressure expected"
    
    def _get_cost_risk_description(self, score: int, crop: str) -> str:
        """Farmer-friendly cost risk description."""
        if score >= 60:
            return f"{crop} requires significant input investment"
        elif score >= 40:
            return "Moderate input costs expected"
        else:
            return "Lower input costs required"


# Global instance
decision_simulator = DecisionSimulatorService()
