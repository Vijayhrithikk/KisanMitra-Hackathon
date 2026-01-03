"""
ML-Based Crop Recommendation Service
Uses trained RandomForest model for predictions.
Falls back to rule-based system if model unavailable.
Includes fertilizer optimization recommendations.
"""

import json
import os
import numpy as np
import joblib
import logging
from services.fertilizer_optimizer_service import fertilizer_optimizer

logger = logging.getLogger(__name__)

# Paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/crop_recommender_ml.joblib')
PROFILES_PATH = os.path.join(os.path.dirname(__file__), '../data/crop_profiles.json')


class MLRecommendationService:
    def __init__(self):
        self.model_data = None
        self.profiles = self._load_profiles()
        self._load_model()
    
    def _load_profiles(self):
        try:
            with open(PROFILES_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
            return {}
    
    def _load_model(self):
        try:
            self.model_data = joblib.load(MODEL_PATH)
            logger.info(f"ML model loaded. Accuracy: {self.model_data['accuracy']:.2%}")
        except Exception as e:
            logger.warning(f"ML model not found, will use rule-based: {e}")
            self.model_data = None
    
    def _encode_input(self, soil_type, season, temp, humidity, ph, n, p, k, rain_days, crop_name):
        """Encode input features for model prediction."""
        if not self.model_data:
            return None
        
        soil_encoder = self.model_data['soil_encoder']
        season_encoder = self.model_data['season_encoder']
        crop_encoder = self.model_data['crop_encoder']
        scaler = self.model_data['scaler']
        
        # Encode soil (handle unknown types)
        try:
            soil_enc = soil_encoder.transform([soil_type])[0]
        except:
            soil_enc = 0  # Default
        
        # Encode season
        try:
            season_enc = season_encoder.transform([season])[0]
        except:
            season_enc = 0
        
        # Encode crop
        try:
            crop_enc = crop_encoder.transform([crop_name])[0]
        except:
            return None  # Unknown crop
        
        # Create feature vector
        features = np.array([[
            soil_enc, season_enc, temp, humidity, ph, n, p, k, rain_days, crop_enc
        ]])
        
        # Scale
        features_scaled = scaler.transform(features)
        
        return features_scaled
    
    def predict_suitability(self, soil_type, season, temp, humidity, ph, n, p, k, rain_days, crop_name):
        """
        Predict crop suitability using ML model.
        Returns: (suitable: bool, confidence: float)
        """
        if not self.model_data:
            return None, None
        
        features = self._encode_input(
            soil_type, season, temp, humidity, ph, n, p, k, rain_days, crop_name
        )
        
        if features is None:
            return None, None
        
        model = self.model_data['model']
        
        # Predict
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
        
        return bool(prediction), confidence
    
    def get_recommendations(self, soil_type, season, temp=28, humidity=60, 
                           soil_ph=7.0, soil_n=150, soil_p=50, soil_k=150,
                           forecast=None, soil_source="database"):
        """
        Get ML-based crop recommendations.
        
        Returns list of suitable crops with confidence scores.
        """
        recommendations = []
        rain_days = forecast.get('rain_days', 2) if forecast else 2
        
        if not self.model_data:
            logger.warning("ML model not available, using rule-based fallback")
            return self._rule_based_recommendations(
                soil_type, season, temp, humidity, soil_ph, soil_n, soil_p, soil_k
            )
        
        crops = self.model_data['crops']
        
        for crop_name in crops:
            suitable, ml_confidence = self.predict_suitability(
                soil_type, season, temp, humidity, 
                soil_ph, soil_n, soil_p, soil_k, rain_days, crop_name
            )
            
            # Soft prediction: Use probability threshold 0.30 (30%)
            if ml_confidence >= 30:
                profile = self.profiles.get(crop_name, {})
                
                # Generate reasons
                reasons = []
                warnings = []
                
                if soil_type in profile.get('soil_suitability', []):
                    reasons.append(f"Excellent match for {soil_type} soil")
                
                if profile.get('ph_min', 0) <= soil_ph <= profile.get('ph_max', 14):
                    reasons.append(f"pH {soil_ph} is optimal")
                
                if profile.get('min_temp', 0) <= temp <= profile.get('max_temp', 50):
                    reasons.append(f"Temperature {temp}°C is suitable")
                
                # Forecast insight
                forecast_insight = None
                water_needs = profile.get('water_needs', 'Medium')
                if water_needs == 'High' and rain_days >= 3:
                    forecast_insight = f"Favorable: {rain_days} rain days expected"
                elif water_needs == 'Low' and rain_days >= 4:
                    warnings.append("Excessive rain expected")
                
                # Get detailed fertilizer recommendation
                fertilizer_plan = None
                try:
                    fertilizer_plan = fertilizer_optimizer.get_complete_recommendation(
                        crop_name=crop_name,
                        current_npk={'n': soil_n, 'p': soil_p, 'k': soil_k},
                        soil_type=soil_type,
                        farming_type='balanced'
                    )
                except Exception as e:
                    logger.warning(f"Fertilizer optimization failed for {crop_name}: {e}")
                
                rec = {
                    "crop": crop_name,
                    "confidence": int(ml_confidence),
                    "ml_prediction": True,
                    "yield_potential": profile.get("yield_potential", "Medium"),
                    "risk_factor": profile.get("risk", "Medium"),
                    "water_needs": profile.get("water_needs", "Medium"),
                    "market_price": profile.get("market_price", {}),
                    "reason": ". ".join(reasons) if reasons else profile.get("description", ""),
                    "fertilizer_recommendation": profile.get("fertilizer_recommendation", ""),
                    "warnings": warnings
                }
                
                # Add detailed fertilizer plan if available
                if fertilizer_plan and 'error' not in fertilizer_plan:
                    rec["fertilizer_plan"] = fertilizer_plan
                
                if forecast_insight:
                    rec["forecast_insight"] = forecast_insight
                
                recommendations.append(rec)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Return only top 5 BEST crops
        return recommendations[:5]
    
    def _rule_based_recommendations(self, soil_type, season, temp, humidity, ph, n, p, k):
        """Fallback rule-based recommendations."""
        recommendations = []
        
        for crop_name, profile in self.profiles.items():
            if season not in profile.get("season", []):
                continue
            
            score = 100
            reasons = []
            
            if soil_type in profile.get("soil_suitability", []):
                reasons.append(f"Good for {soil_type} soil")
            else:
                score -= 25
            
            if profile.get("ph_min", 0) <= ph <= profile.get("ph_max", 14):
                reasons.append("pH optimal")
            else:
                score -= 20
            
            if score > 40:
                recommendations.append({
                    "crop": crop_name,
                    "confidence": score,
                    "ml_prediction": False,
                    "yield_potential": profile.get("yield_potential", "Medium"),
                    "risk_factor": profile.get("risk", "Medium"),
                    "water_needs": profile.get("water_needs", "Medium"),
                    "market_price": profile.get("market_price", {}),
                    "reason": ". ".join(reasons),
                    "fertilizer_recommendation": profile.get("fertilizer_recommendation", ""),
                    "warnings": []
                })
        
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations[:5]  # Top 5 only
    
    def get_model_info(self):
        """Get model information."""
        if not self.model_data:
            return {"loaded": False, "type": "rule-based"}
        
        return {
            "loaded": True,
            "type": "RandomForestClassifier",
            "accuracy": self.model_data['accuracy'],
            "n_crops": len(self.model_data['crops']),
            "crops": self.model_data['crops']
        }


# Convenience function
def get_ml_recommender():
    return MLRecommendationService()
