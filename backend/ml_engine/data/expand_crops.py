"""
Script to expand crop_profiles.json with fruits and vegetables
"""
import json
import os

# Path to crop profiles
PROFILES_PATH = os.path.join(os.path.dirname(__file__), 'crop_profiles.json')

# Load existing profiles
with open(PROFILES_PATH, 'r') as f:
    profiles = json.load(f)

# Add more fruits and vegetables
new_crops = {
    # Vegetables
    "Tomato": {
        "season": ["Kharif", "Rabi", "Zaid"],
        "water_needs": "Medium",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 2500, "unit": "₹/quintal", "msp": False, "trend": "volatile"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Clayey", "Alluvial"],
        "min_temp": 18,
        "max_temp": 27,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "n_needs": "High",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "Highly versatile vegetable. Needs staking and pest management.",
        "fertilizer_recommendation": "NPK 100:50:50. Calcium for blossom end rot prevention."
    },
    "Onion": {
        "season": ["Rabi", "Kharif"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 2000, "unit": "₹/quintal", "msp": false, "trend": "volatile"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial"],
        "min_temp": 13,
        "max_temp": 24,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "n_needs": "High",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "Major vegetable crop. Sensitive to water logging.",
        "fertilizer_recommendation": "Split N application. Sulphur fortified fertilizers."
    },
    "Potato": {
        "season": ["Rabi"],
        "water_needs": "High",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 1500, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Sandy Loam", "Loamy", "Alluvial"],
        "min_temp": 15,
        "max_temp": 25,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "n_needs": "High",
        "p_needs": "High",
        "k_needs": "High",
        "description": "Tuber crop. Grows best in cool weather.",
        "fertilizer_recommendation": "NPK 120:80:100. Potash critical for tuber quality."
    },
    "Cabbage": {
        "season": ["Rabi"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 1200, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial"],
        "min_temp": 15,
        "max_temp": 20,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "n_needs": "High",
        "p_needs": "Medium",
        "k_needs": "Medium",
        "description": "Cole crop. Requires cool weather for head formation.",
        "fertilizer_recommendation": "NPK 150:75:75. Boron supplementation needed."
    },
    "Cauliflower": {
        "season": ["Rabi"],
        "water_needs": "Medium",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 1800, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Clayey"],
        "min_temp": 12,
       "max_temp": 22,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "n_needs": "High",
        "p_needs": "High",
        "k_needs": "Medium",
        "description": "Cole crop. Very sensitive to temperature fluctuations.",
        "fertilizer_recommendation": "NPK 120:60:60. Boron and molybdenum micronutrients."
    },
    "Brinjal": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Medium",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 2200, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Clayey", "Alluvial"],
        "min_temp": 22,
        "max_temp": 30,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "n_needs": "Medium",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "Eggplant. Susceptible to fruit and shoot borer.",
        "fertilizer_recommendation": "NPK 100:50:50. Regular pest monitoring needed."
    },
    "Okra": {
        "season": ["Kharif", "Zaid"],
        "water_needs": "Low",
        "risk": "Low",
        "yield_potential": "Medium",
        "market_price": {"price": 3000, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial"],
        "min_temp": 25,
        "max_temp": 37,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "n_needs": "Medium",
        "p_needs": "Medium",
        "k_needs": "Medium",
        "description": "Lady finger. Warm season crop. Drought tolerant.",
        "fertilizer_recommendation": "NPK 80:40:40. Organic manure beneficial."
    },
    "Carrot": {
        "season": ["Rabi"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "Medium",
        "market_price": {"price": 2500, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Sandy Loam", "Loamy", "Alluvial"],
        "min_temp": 16,
        "max_temp": 20,
        "ph_min": 5.5,
        "ph_max": 6.5,
        "n_needs": "Medium",
        "p_needs": "High",
        "k_needs": "High",
        "description": "Root vegetable. Requires deep, loose soil.",
        "fertilizer_recommendation": "Avoid fresh manure. NPK 50:50:75."
    },
    # Fruits
    "Mango": {
        "season": ["Kharif"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 4000, "unit": "₹/quintal", "msp": false, "trend": "seasonal"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial", "Red Soil"],
        "min_temp": 24,
        "max_temp": 35,
        "ph_min": 5.5,
        "ph_max": 7.5,
        "n_needs": "Medium",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "King of fruits. Perennial tree crop.",
        "fertilizer_recommendation": "NPK 100:50:100 per tree. Micronutrients in dormant season."
    },
    "Banana": {
        "season": ["Kharif", "Rabi", "Zaid"],
        "water_needs": "High",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 2500, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Alluvial", "Clayey", "Red Soil"],
        "min_temp": 15,
        "max_temp": 35,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "n_needs": "High",
        "p_needs": "High",
        "k_needs": "High",
        "description": "Year-round crop. High water and nutrient requirements.",
        "fertilizer_recommendation": "NPK 200:60:200 per clump. Regular organic mulching."
    },
    "Papaya": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 2000, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial"],
        "min_temp": 20,
        "max_temp": 35,
        "ph_min": 6.5,
        "ph_max": 7.0,
        "n_needs": "High",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "Fast-growing fruit. Sensitive to waterlogging.",
        "fertilizer_recommendation": "NPK 200:200:400 per plant. Split applications."
    },
    "Guava": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 3000, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial", "Red Soil"],
        "min_temp": 20,
        "max_temp": 35,
        "ph_min": 5.0,
        "ph_max": 8.0,
        "n_needs": "Medium",
        "p_needs": "Medium",
        "k_needs": "Medium",
        "description": "Hardy fruit tree. Tolerates various soils.",
        "fertilizer_recommendation": "NPK 600:250:500 per tree per year."
    },
    "Pomegranate": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Low",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 6000, "unit": "₹/quintal", "msp": false, "trend": "up"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Black"],
        "min_temp": 15,
        "max_temp": 38,
        "ph_min": 6.5,
        "ph_max": 7.5,
        "n_needs": "Medium",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "High-value fruit. Drought tolerant once established.",
        "fertilizer_recommendation": "NPK 500:250:250 per tree. Drip irrigation ideal."
    },
    "Grapes": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Medium",
        "risk": "High",
        "yield_potential": "High",
        "market_price": {"price": 5000, "unit": "₹/quintal", "msp": false, "trend": "up"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Black"],
        "min_temp": 15,
        "max_temp": 40,
        "ph_min": 6.5,
        "ph_max": 8.0,
        "n_needs": "High",
        "p_needs": "High",
        "k_needs": "High",
        "description": "Premium fruit. Requires trellising and pruning.",
        "fertilizer_recommendation": "NPK 400:400:500 per hectare. Micronutrients essential."
    },
    "Watermelon": {
        "season": ["Zaid", "Kharif"],
        "water_needs": "Medium",
        "risk": "Low",
        "yield_potential": "High",
        "market_price": {"price": 1500, "unit": "₹/quintal", "msp": false, "trend": "seasonal"},
        "soil_suitability": ["Sandy Loam", "Loamy", "Alluvial"],
        "min_temp": 24,
        "max_temp": 30,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "n_needs": "Medium",
        "p_needs": "High",
        "k_needs": "High",
        "description": "Summer fruit. Requires warm weather.",
        "fertilizer_recommendation": "NPK 50:25:50. Potash for sweetness."
    },
    "Orange": {
        "season": ["Kharif", "Rabi"],
        "water_needs": "Medium",
        "risk": "Medium",
        "yield_potential": "High",
        "market_price": {"price": 3500, "unit": "₹/quintal", "msp": false, "trend": "stable"},
        "soil_suitability": ["Loamy", "Sandy Loam", "Alluvial"],
        "min_temp": 13,
        "max_temp": 37,
        "ph_min": 5.5,
        "ph_max": 7.5,
        "n_needs": "High",
        "p_needs": "Medium",
        "k_needs": "High",
        "description": "Citrus fruit. Requires good drainage.",
        "fertilizer_recommendation": "NPK 500:250:250 per tree. Micronutrients needed."
    }
}

# Merge with existing
profiles.update(new_crops)

# Save updated profiles
with open(PROFILES_PATH, 'w') as f:
    json.dump(profiles, f, indent=4)

print(f"✅ Updated crop profiles: {len(profiles)} total crops")
print(f"   - Added {len(new_crops)} new fruit and vegetable crops")
print(f"   - Original crops: 15")
