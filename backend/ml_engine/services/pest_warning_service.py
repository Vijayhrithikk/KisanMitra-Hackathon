"""
Pest Warning Service for KisanMitra
Predicts pest outbreaks based on weather, season, and crop conditions.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# Pest database for Andhra Pradesh / Telangana crops
PEST_DATABASE = {
    "Paddy": {
        "Brown Plant Hopper (BPH)": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 80, "season": ["Kharif"]},
            "severity": "High",
            "symptoms": "Hopper burn, circular yellowing patches",
            "control": "Avoid excess nitrogen. Spray Imidacloprid 200ml/acre. Drain water periodically."
        },
        "Stem Borer": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 70, "season": ["Kharif", "Rabi"]},
            "severity": "High", 
            "symptoms": "Dead hearts, white heads",
            "control": "Install pheromone traps. Apply Carbofuran granules. Remove affected tillers."
        },
        "Blast (Fungal)": {
            "triggers": {"temp_min": 20, "temp_max": 30, "humidity_min": 85, "season": ["Kharif"]},
            "severity": "Severe",
            "symptoms": "Diamond-shaped lesions on leaves, neck rot",
            "control": "Spray Tricyclazole 300g/acre. Avoid excess nitrogen. Use resistant varieties."
        },
        "Leaf Folder": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 75, "season": ["Kharif", "Rabi"]},
            "severity": "Medium",
            "symptoms": "Folded leaves with caterpillars inside",
            "control": "Spray Chlorantraniliprole. Release Trichogramma egg parasites."
        }
    },
    "Cotton": {
        "Pink Bollworm": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 60, "season": ["Kharif"]},
            "severity": "Severe",
            "symptoms": "Rosette flowers, lint damage in bolls",
            "control": "Pheromone traps (5/acre). Destroy crop residue. Spray Emamectin benzoate."
        },
        "American Bollworm": {
            "triggers": {"temp_min": 20, "temp_max": 35, "humidity_min": 50, "season": ["Kharif"]},
            "severity": "Severe",
            "symptoms": "Bored squares and bolls, frass visible",
            "control": "Install light traps. Spray NPV (250LE/acre). Apply Spinosad."
        },
        "Whitefly": {
            "triggers": {"temp_min": 28, "temp_max": 40, "humidity_min": 40, "season": ["Kharif"]},
            "severity": "High",
            "symptoms": "Sticky honeydew, sooty mold, leaf curl",
            "control": "Yellow sticky traps. Spray Diafenthiuron. Avoid monoculture."
        },
        "Sucking Pests (Jassids, Aphids)": {
            "triggers": {"temp_min": 25, "temp_max": 38, "humidity_min": 50, "season": ["Kharif"]},
            "severity": "Medium",
            "symptoms": "Leaf curling, yellowing margins",
            "control": "Spray Dimethoate or neem oil. Encourage natural predators."
        }
    },
    "Chilli": {
        "Thrips": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 50, "season": ["Kharif", "Rabi"]},
            "severity": "High",
            "symptoms": "Leaf curl, upward curling, bronzing",
            "control": "Blue sticky traps. Spray Fipronil. Mulching with straw."
        },
        "Fruit Borer": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 60, "season": ["Kharif", "Rabi"]},
            "severity": "High",
            "symptoms": "Bored fruits with entry holes",
            "control": "Pheromone traps. Spray Chlorantraniliprole. Remove affected fruits."
        },
        "Mites": {
            "triggers": {"temp_min": 30, "temp_max": 40, "humidity_min": 30, "season": ["Zaid"]},
            "severity": "Medium",
            "symptoms": "Leaf crinkling, webbing underneath",
            "control": "Spray Dicofol or Propargite. Increase humidity with sprinklers."
        }
    },
    "Maize": {
        "Fall Armyworm": {
            "triggers": {"temp_min": 20, "temp_max": 35, "humidity_min": 50, "season": ["Kharif", "Rabi"]},
            "severity": "Severe",
            "symptoms": "Ragged feeding on whorl, sawdust-like frass",
            "control": "Scout early. Spray Spinetoram. Apply Metarhizium bio-pesticide. Destroy crop residue."
        },
        "Stem Borer": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 60, "season": ["Kharif"]},
            "severity": "High",
            "symptoms": "Dead heart in early stage, broken tassels",
            "control": "Release Trichogramma. Apply Carbofuran in whorl."
        },
        "Aphids": {
            "triggers": {"temp_min": 20, "temp_max": 30, "humidity_min": 70, "season": ["Rabi"]},
            "severity": "Medium",
            "symptoms": "Colonies on tassels and ears, honeydew",
            "control": "Spray Imidacloprid. Encourage ladybirds."
        }
    },
    "Wheat": {
        "Aphids": {
            "triggers": {"temp_min": 15, "temp_max": 25, "humidity_min": 60, "season": ["Rabi"]},
            "severity": "High",
            "symptoms": "Yellowing, honeydew on leaves",
            "control": "Spray Dimethoate at ETL of 10-15/ear. Release Chrysoperla."
        },
        "Yellow Rust": {
            "triggers": {"temp_min": 10, "temp_max": 18, "humidity_min": 80, "season": ["Rabi"]},
            "severity": "Severe",
            "symptoms": "Yellow stripes on leaves",
            "control": "Spray Propiconazole 25EC @ 0.1%. Use resistant varieties."
        },
        "Termites": {
            "triggers": {"temp_min": 20, "temp_max": 35, "humidity_min": 40, "season": ["Rabi"]},
            "severity": "Medium",
            "symptoms": "Wilting, roots eaten",
            "control": "Soil application of Chlorpyriphos. Adequate irrigation."
        }
    },
    "Pulses": {
        "Pod Borer": {
            "triggers": {"temp_min": 20, "temp_max": 30, "humidity_min": 60, "season": ["Rabi"]},
            "severity": "Severe",
            "symptoms": "Bored pods, larvae feeding on seeds",
            "control": "Spray HaNPV 250LE/acre. Pheromone traps. Bird perches."
        },
        "Aphids": {
            "triggers": {"temp_min": 15, "temp_max": 25, "humidity_min": 70, "season": ["Rabi"]},
            "severity": "High",
            "symptoms": "Stunted growth, honeydew, sooty mold",
            "control": "Spray neem oil 5ml/L. Release Chrysoperla."
        }
    },
    "Ground Nuts": {
        "Leaf Miner": {
            "triggers": {"temp_min": 25, "temp_max": 35, "humidity_min": 50, "season": ["Kharif"]},
            "severity": "Medium",
            "symptoms": "Serpentine mines on leaves",
            "control": "Spray Profenofos. Remove affected leaves."
        },
        "Tikka Disease (Fungal)": {
            "triggers": {"temp_min": 25, "temp_max": 30, "humidity_min": 80, "season": ["Kharif"]},
            "severity": "High",
            "symptoms": "Circular brown spots on leaves",
            "control": "Spray Mancozeb or Chlorothalonil. Crop rotation."
        }
    }
}


class PestWarningService:
    """
    Predicts pest outbreaks based on weather and crop conditions.
    """
    
    def __init__(self):
        self.pest_db = PEST_DATABASE
    
    def get_pest_warnings(self, crop: str, temp: float, humidity: float, 
                          season: str, recent_rain: bool = False) -> List[Dict]:
        """
        Get pest warnings for a specific crop based on conditions.
        
        Args:
            crop: Crop name (Paddy, Cotton, etc.)
            temp: Current temperature
            humidity: Current humidity  
            season: Current season (Kharif, Rabi, Zaid)
            recent_rain: Whether there was recent rainfall
            
        Returns:
            List of pest warning dictionaries
        """
        warnings = []
        
        # Normalize crop name
        crop = self._normalize_crop_name(crop)
        crop_pests = self.pest_db.get(crop, {})
        
        if not crop_pests:
            return warnings
        
        for pest_name, pest_info in crop_pests.items():
            triggers = pest_info["triggers"]
            risk_score = self._calculate_risk(temp, humidity, season, triggers, recent_rain)
            
            if risk_score > 0:
                risk_level = self._get_risk_level(risk_score)
                warnings.append({
                    "pest": pest_name,
                    "crop": crop,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "severity": pest_info["severity"],
                    "symptoms": pest_info["symptoms"],
                    "control": pest_info["control"],
                    "conditions_met": self._get_conditions_met(temp, humidity, season, triggers)
                })
        
        # Sort by risk score
        warnings.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return warnings
    
    def _normalize_crop_name(self, crop: str) -> str:
        """Normalize crop name to match database keys."""
        crop_mapping = {
            "rice": "Paddy",
            "paddy": "Paddy",
            "cotton": "Cotton",
            "chilli": "Chilli",
            "chili": "Chilli",
            "maize": "Maize",
            "corn": "Maize",
            "wheat": "Wheat",
            "pulses": "Pulses",
            "groundnut": "Ground Nuts",
            "groundnuts": "Ground Nuts",
            "peanut": "Ground Nuts",
        }
        return crop_mapping.get(crop.lower(), crop)
    
    def _calculate_risk(self, temp: float, humidity: float, season: str,
                        triggers: Dict, recent_rain: bool) -> int:
        """Calculate pest risk score (0-100)."""
        risk = 0
        
        # Season match (mandatory)
        if season not in triggers.get("season", []):
            return 0
        
        risk += 30  # Base risk if season matches
        
        # Temperature match
        temp_min = triggers.get("temp_min", 0)
        temp_max = triggers.get("temp_max", 50)
        
        if temp_min <= temp <= temp_max:
            risk += 30
        elif temp_min - 5 <= temp <= temp_max + 5:
            risk += 15  # Near optimal range
        
        # Humidity match
        humidity_min = triggers.get("humidity_min", 0)
        
        if humidity >= humidity_min:
            risk += 30
        elif humidity >= humidity_min - 10:
            risk += 15  # Close to threshold
        
        # Rain boost for fungal diseases
        if recent_rain and humidity >= 70:
            risk += 10
        
        return min(100, risk)
    
    def _get_risk_level(self, score: int) -> str:
        """Convert risk score to risk level."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_conditions_met(self, temp: float, humidity: float, 
                            season: str, triggers: Dict) -> List[str]:
        """List which conditions are met for pest risk."""
        conditions = []
        
        if season in triggers.get("season", []):
            conditions.append(f"Season: {season}")
        
        temp_min = triggers.get("temp_min", 0)
        temp_max = triggers.get("temp_max", 50)
        if temp_min <= temp <= temp_max:
            conditions.append(f"Temperature: {temp}°C (optimal range)")
        
        humidity_min = triggers.get("humidity_min", 0)
        if humidity >= humidity_min:
            conditions.append(f"Humidity: {humidity}% (above {humidity_min}%)")
        
        return conditions
    
    def get_all_crop_warnings(self, temp: float, humidity: float, 
                               season: str, crops: List[str] = None) -> Dict[str, List[Dict]]:
        """Get pest warnings for multiple crops."""
        if crops is None:
            crops = list(self.pest_db.keys())
        
        all_warnings = {}
        for crop in crops:
            warnings = self.get_pest_warnings(crop, temp, humidity, season)
            if warnings:
                all_warnings[crop] = warnings
        
        return all_warnings
    
    def get_summary_sms(self, crop: str, temp: float, humidity: float, season: str) -> str:
        """Generate SMS-friendly pest warning summary."""
        warnings = self.get_pest_warnings(crop, temp, humidity, season)
        
        if not warnings:
            return f"No major pest risks for {crop} in current conditions."
        
        high_risk = [w for w in warnings if w["risk_level"] in ["CRITICAL", "HIGH"]]
        
        if not high_risk:
            return f"Low pest risk for {crop}. Continue regular scouting."
        
        text = f"PEST ALERT - {crop.upper()}\n"
        text += "=" * 20 + "\n\n"
        
        for w in high_risk[:2]:  # Top 2 risks
            text += f"* {w['pest']} ({w['risk_level']})\n"
            text += f"  Look for: {w['symptoms']}\n"
            text += f"  Action: {w['control'][:80]}...\n\n"
        
        return text


# Singleton
_pest_service = None

def get_pest_warning_service() -> PestWarningService:
    global _pest_service
    if _pest_service is None:
        _pest_service = PestWarningService()
    return _pest_service
