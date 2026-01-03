"""
Comprehensive Crop Stages Database Generator
Generates detailed stage-by-stage data for 5 priority crops
"""
import json
from datetime import datetime

# Comprehensive crop stages database
CROP_STAGES_COMPLETE = {
    "version": "2.0",
    "generated": datetime.now().isoformat(),
    "crops": {
        "Paddy": {
            "name_te": "వరి",
            "total_duration_days": 120,
            "seasons": ["Kharif", "Rabi"],
            "water_requirement_mm": 1200,
            "stages": [
                {
                    "id": 1,
                    "name": "Nursery",
                    "name_te": "నారుమడి",
                    "start_day": 0,
                    "end_day": 21,
                    "description": "Seed germination and seedling growth in nursery beds",
                    "critical_activities": [
                        {"task": "Prepare raised nursery beds (1.5m width)", "priority": "high", "day": 1},
                        {"task": "Treat seeds with Carbendazim 2g/kg", "priority": "high", "day": 1},
                        {"task": "Soak seeds for 24 hours", "priority": "high", "day": 1},
                        {"task": "Incubate seeds for 48 hours", "priority": "medium", "day": 2},
                        {"task": "Broadcast pre-germinated seeds uniformly", "priority": "high", "day": 3},
                        {"task": "Maintain 2-3 cm water depth", "priority": "high", "day": 5},
                        {"task": "Apply DAP 2.5 kg per 100 sqm", "priority": "medium", "day": 10},
                        {"task": "Scout for leaf folder and thrips", "priority": "medium", "day": 15},
                        {"task": "Spray Chlorpyriphos if pests found", "priority": "high", "day": 15}
                    ],
                    "water_management": "Keep saturated, thin layer 2-3 cm",
                    "fertilizer_schedule": [{"day": 10, "product": "DAP", "qty_per_acre": "2.5 kg"}],
                    "pest_focus": ["Thrips", "Leaf folder"],
                    "disease_focus": ["Damping off"],
                    "weather_sensitivity": {"frost": "critical", "heat_above_40": "high"}
                },
                {
                    "id": 2,
                    "name": "Transplanting",
                    "name_te": "నాటుట",
                    "start_day": 21,
                    "end_day": 28,
                    "description": "Transfer 21-day old seedlings to main field",
                    "critical_activities": [
                        {"task": "Puddle main field thoroughly", "priority": "high", "day": 21},
                        {"task": "Level field for uniform water distribution", "priority": "high", "day": 21},
                        {"task": "Apply basal fertilizer - DAP 50kg/acre", "priority": "high", "day": 22},
                        {"task": "Uproot seedlings carefully", "priority": "high", "day": 22},
                        {"task": "Transplant 2-3 seedlings per hill", "priority": "high", "day": 22},
                        {"task": "Maintain 20x15 cm spacing", "priority": "medium", "day": 22},
                        {"task": "Maintain 5 cm water depth", "priority": "high", "day": 23},
                        {"task": "Gap filling within 7 days", "priority": "medium", "day": 28}
                    ],
                    "water_management": "5 cm standing water",
                    "fertilizer_schedule": [{"day": 22, "product": "DAP", "qty_per_acre": "50 kg"}],
                    "pest_focus": ["Stem borer", "Green leafhopper"],
                    "weather_sensitivity": {"heavy_rain": "medium", "drought": "critical"}
                },
                {
                    "id": 3,
                    "name": "Tillering",
                    "name_te": "పిల్ల పట్టడం",
                    "start_day": 28,
                    "end_day": 56,
                    "description": "Vegetative growth with tiller production",
                    "critical_activities": [
                        {"task": "First nitrogen top-dressing - Urea 30 kg/acre", "priority": "high", "day": 30},
                        {"task": "Maintain 5-7 cm water depth", "priority": "high", "day": 28},
                        {"task": "Scout for BPH weekly", "priority": "high", "day": 35},
                        {"task": "Hand weeding or herbicide application", "priority": "high", "day": 35},
                        {"task": "Second nitrogen dose - Urea 20 kg/acre", "priority": "high", "day": 45},
                        {"task": "Monitor for stem borer moth", "priority": "medium", "day": 42},
                        {"task": "Install pheromone traps", "priority": "medium", "day": 40},
                        {"task": "Drain field intermittently", "priority": "medium", "day": 50}
                    ],
                    "water_management": "5-7 cm, alternate wetting and drying",
                    "fertilizer_schedule": [
                        {"day": 30, "product": "Urea", "qty_per_acre": "30 kg"},
                        {"day": 45, "product": "Urea", "qty_per_acre": "20 kg"}
                    ],
                    "pest_focus": ["BPH", "Stem borer", "Leaf folder"],
                    "disease_focus": ["Bacterial leaf blight"],
                    "weather_sensitivity": {"continuous_rain": "high", "drought": "critical"}
                },
                {
                    "id": 4,
                    "name": "Panicle Initiation",
                    "name_te": "కంకి ఏర్పడటం",
                    "start_day": 56,
                    "end_day": 70,
                    "description": "Reproductive stage begins",
                    "critical_activities": [
                        {"task": "Third nitrogen dose - Urea 20 kg/acre", "priority": "high", "day": 56},
                        {"task": "Apply potash - MOP 20 kg/acre", "priority": "high", "day": 56},
                        {"task": "Maintain 5 cm water continuously", "priority": "critical", "day": 56},
                        {"task": "Scout for neck blast symptoms", "priority": "high", "day": 60},
                        {"task": "Spray Tricyclazole if blast risk", "priority": "high", "day": 62},
                        {"task": "Monitor BPH population", "priority": "high", "day": 65}
                    ],
                    "water_management": "Continuous 5 cm - CRITICAL",
                    "fertilizer_schedule": [
                        {"day": 56, "product": "Urea", "qty_per_acre": "20 kg"},
                        {"day": 56, "product": "MOP", "qty_per_acre": "20 kg"}
                    ],
                    "pest_focus": ["BPH", "Gall midge"],
                    "disease_focus": ["Neck blast", "Sheath blight"],
                    "weather_sensitivity": {"drought": "CRITICAL", "cold_below_15": "critical"}
                },
                {
                    "id": 5,
                    "name": "Flowering",
                    "name_te": "పూత దశ",
                    "start_day": 70,
                    "end_day": 85,
                    "description": "Anthesis and pollination",
                    "critical_activities": [
                        {"task": "Maintain 5 cm water strictly", "priority": "critical", "day": 70},
                        {"task": "Avoid any pesticide spraying during peak flowering", "priority": "critical", "day": 75},
                        {"task": "Scout for rice bug", "priority": "high", "day": 78},
                        {"task": "Monitor for false smut", "priority": "medium", "day": 80},
                        {"task": "Spray fungicide only if necessary", "priority": "medium", "day": 82}
                    ],
                    "water_management": "Continuous 5 cm - CRITICAL for grain setting",
                    "pest_focus": ["Rice bug", "Ear cutting caterpillar"],
                    "disease_focus": ["False smut"],
                    "weather_sensitivity": {"heat_above_35": "CRITICAL", "heavy_rain": "high"}
                },
                {
                    "id": 6,
                    "name": "Grain Filling",
                    "name_te": "గింజ నింపుట",
                    "start_day": 85,
                    "end_day": 100,
                    "description": "Starch accumulation in grains",
                    "critical_activities": [
                        {"task": "Maintain 3-5 cm water", "priority": "high", "day": 85},
                        {"task": "Scout for grain discoloration", "priority": "medium", "day": 90},
                        {"task": "Spray Propiconazole if sheath blight severe", "priority": "medium", "day": 92},
                        {"task": "Begin gradual water reduction", "priority": "high", "day": 95}
                    ],
                    "water_management": "3-5 cm, reduce gradually",
                    "pest_focus": ["Grain bugs"],
                    "disease_focus": ["Grain discoloration", "Sheath rot"],
                    "weather_sensitivity": {"heat_above_38": "high", "heavy_rain": "medium"}
                },
                {
                    "id": 7,
                    "name": "Maturity",
                    "name_te": "పరిపక్వత",
                    "start_day": 100,
                    "end_day": 115,
                    "description": "Grain maturation and drying",
                    "critical_activities": [
                        {"task": "Drain field completely", "priority": "high", "day": 100},
                        {"task": "Monitor grain moisture (harvest at 20-22%)", "priority": "high", "day": 105},
                        {"task": "Prepare harvesting equipment", "priority": "medium", "day": 110},
                        {"task": "Arrange threshing floor/combine", "priority": "medium", "day": 112}
                    ],
                    "water_management": "Drain completely 10-15 days before harvest",
                    "weather_sensitivity": {"heavy_rain": "CRITICAL", "strong_wind": "high"}
                },
                {
                    "id": 8,
                    "name": "Harvest",
                    "name_te": "కోత",
                    "start_day": 115,
                    "end_day": 120,
                    "description": "Cutting, threshing and drying",
                    "critical_activities": [
                        {"task": "Harvest when 85% grains are straw-colored", "priority": "critical", "day": 115},
                        {"task": "Thresh within 24 hours of cutting", "priority": "high", "day": 116},
                        {"task": "Dry grains to 14% moisture for storage", "priority": "high", "day": 118},
                        {"task": "Clean and store in dry place", "priority": "high", "day": 120}
                    ],
                    "weather_sensitivity": {"rain": "CRITICAL - delay harvest", "humid": "high"}
                }
            ]
        }
    }
}

# Save to file
output_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_stages_complete.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(CROP_STAGES_COMPLETE, f, indent=2, ensure_ascii=False)

print(f"✅ Created Paddy crop stages at {output_path}")
print(f"   Stages: {len(CROP_STAGES_COMPLETE['crops']['Paddy']['stages'])}")
