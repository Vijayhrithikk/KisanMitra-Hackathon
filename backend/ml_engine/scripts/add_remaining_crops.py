"""
Add remaining 4 crops to the comprehensive stages database
Cotton, Maize, Groundnut, Chilli
"""
import json

# Load existing
path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_stages_complete.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Add Cotton
data['crops']['Cotton'] = {
    "name_te": "పత్తి",
    "total_duration_days": 180,
    "seasons": ["Kharif"],
    "water_requirement_mm": 700,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తుట", "start_day": 0, "end_day": 15,
         "critical_activities": [
             {"task": "Treat seeds with Imidacloprid 5g/kg", "priority": "high", "day": 1},
             {"task": "Sow seeds 3-4 cm deep", "priority": "high", "day": 1},
             {"task": "Maintain soil moisture", "priority": "high", "day": 3},
             {"task": "Gap filling if needed", "priority": "medium", "day": 12}
         ],
         "pest_focus": ["Sucking pests"], "disease_focus": ["Seedling rot"]},
        {"id": 2, "name": "Seedling", "name_te": "మొక్క దశ", "start_day": 15, "end_day": 35,
         "critical_activities": [
             {"task": "First weeding and thinning", "priority": "high", "day": 20},
             {"task": "Apply Urea 30 kg/acre as first dose", "priority": "high", "day": 25},
             {"task": "Scout for Jassids and Aphids weekly", "priority": "high", "day": 20},
             {"task": "Spray Imidacloprid if Jassids >2/leaf", "priority": "high", "day": 25}
         ],
         "pest_focus": ["Jassids", "Aphids", "Whitefly"], "disease_focus": ["Bacterial blight"]},
        {"id": 3, "name": "Squaring", "name_te": "చదరాలు ఏర్పడటం", "start_day": 35, "end_day": 55,
         "critical_activities": [
             {"task": "Second weeding and earthing up", "priority": "high", "day": 40},
             {"task": "Apply second dose Urea + MOP", "priority": "high", "day": 45},
             {"task": "Scout for Thrips and Bollworm", "priority": "high", "day": 45},
             {"task": "Install pheromone traps for bollworm", "priority": "medium", "day": 40},
             {"task": "Light irrigation if required", "priority": "medium", "day": 50}
         ],
         "pest_focus": ["American Bollworm", "Thrips", "Pink Bollworm"], "disease_focus": ["Grey mildew"]},
        {"id": 4, "name": "Flowering", "name_te": "పూత దశ", "start_day": 55, "end_day": 85,
         "critical_activities": [
             {"task": "Critical irrigation - do not allow stress", "priority": "critical", "day": 60},
             {"task": "Apply final nitrogen dose", "priority": "high", "day": 60},
             {"task": "Intensive bollworm scouting twice weekly", "priority": "critical", "day": 60},
             {"task": "Spray Spinosad/Emamectin if ETL crossed", "priority": "high", "day": 70},
             {"task": "Apply micronutrients foliar spray", "priority": "medium", "day": 75}
         ],
         "pest_focus": ["American Bollworm", "Pink Bollworm", "Spotted Bollworm"], "disease_focus": ["Alternaria leaf spot"]},
        {"id": 5, "name": "Boll Development", "name_te": "కాయ అభివృద్ధి", "start_day": 85, "end_day": 130,
         "critical_activities": [
             {"task": "Continue bollworm management", "priority": "high", "day": 90},
             {"task": "Irrigate at critical boll development stage", "priority": "high", "day": 100},
             {"task": "Scout for Pink Bollworm rosette flowers", "priority": "high", "day": 110},
             {"task": "Spray Profenophos + Cypermethrin if needed", "priority": "medium", "day": 115}
         ],
         "pest_focus": ["Pink Bollworm", "Mealy bug"], "disease_focus": ["Boll rot"]},
        {"id": 6, "name": "Boll Opening", "name_te": "కాయ పగలడం", "start_day": 130, "end_day": 160,
         "critical_activities": [
             {"task": "Stop irrigation before first picking", "priority": "high", "day": 130},
             {"task": "First picking at 60% boll opening", "priority": "high", "day": 145},
             {"task": "Keep cotton dry - avoid rain damage", "priority": "critical", "day": 145},
             {"task": "Second picking after 15 days", "priority": "medium", "day": 160}
         ],
         "pest_focus": ["Mealy bug"], "weather_sensitivity": {"rain": "CRITICAL - staining"}},
        {"id": 7, "name": "Final Harvest", "name_te": "చివరి కోత", "start_day": 160, "end_day": 180,
         "critical_activities": [
             {"task": "Complete all pickings", "priority": "high", "day": 175},
             {"task": "Destroy crop residues to prevent pink bollworm", "priority": "high", "day": 180},
             {"task": "Deep plough field", "priority": "medium", "day": 180}
         ]}
    ]
}

# Add Maize
data['crops']['Maize'] = {
    "name_te": "మొక్కజొన్న",
    "total_duration_days": 110,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 500,
    "stages": [
        {"id": 1, "name": "Emergence", "name_te": "మొలకెత్తుట", "start_day": 0, "end_day": 12,
         "critical_activities": [
             {"task": "Treat seeds with Thiram 3g/kg", "priority": "high", "day": 1},
             {"task": "Sow at 4-5 cm depth", "priority": "high", "day": 1},
             {"task": "Apply pre-emergence herbicide Atrazine", "priority": "medium", "day": 2},
             {"task": "Gap filling by day 10", "priority": "medium", "day": 10}
         ],
         "pest_focus": ["Shootfly", "Cutworm"]},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార దశ", "start_day": 12, "end_day": 45,
         "critical_activities": [
             {"task": "First weeding and hoeing", "priority": "high", "day": 20},
             {"task": "Apply Urea 40 kg/acre first dose", "priority": "high", "day": 25},
             {"task": "Scout for Fall Armyworm weekly", "priority": "critical", "day": 15},
             {"task": "Spray Emamectin benzoate if FAW found", "priority": "high", "day": 20},
             {"task": "Second weeding and earthing up", "priority": "high", "day": 35},
             {"task": "Second Urea dose before knee-high", "priority": "high", "day": 40}
         ],
         "pest_focus": ["Fall Armyworm", "Stem Borer"], "disease_focus": ["Turcicum leaf blight"]},
        {"id": 3, "name": "Tasseling", "name_te": "తురాయి దశ", "start_day": 45, "end_day": 60,
         "critical_activities": [
             {"task": "Critical irrigation - must not stress", "priority": "critical", "day": 50},
             {"task": "Final nitrogen application", "priority": "high", "day": 50},
             {"task": "Scout for aphids on tassel", "priority": "medium", "day": 55}
         ],
         "weather_sensitivity": {"drought": "CRITICAL - severe yield loss"}},
        {"id": 4, "name": "Silking", "name_te": "పట్టు దశ", "start_day": 60, "end_day": 70,
         "critical_activities": [
             {"task": "Ensure adequate soil moisture", "priority": "critical", "day": 60},
             {"task": "Scout for ear borers", "priority": "high", "day": 65},
             {"task": "Avoid any stress during pollination", "priority": "critical", "day": 65}
         ],
         "weather_sensitivity": {"heat_above_38": "CRITICAL - poor kernel set"}},
        {"id": 5, "name": "Kernel Development", "name_te": "గింజ అభివృద్ధి", "start_day": 70, "end_day": 95,
         "critical_activities": [
             {"task": "Maintain soil moisture", "priority": "high", "day": 75},
             {"task": "Scout for ear rot", "priority": "medium", "day": 85},
             {"task": "Monitor for aphids", "priority": "medium", "day": 80}
         ],
         "disease_focus": ["Ear rot", "Stalk rot"]},
        {"id": 6, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 95, "end_day": 110,
         "critical_activities": [
             {"task": "Check kernel milk line - harvest at 25% moisture", "priority": "high", "day": 100},
             {"task": "Harvest when black layer forms", "priority": "high", "day": 105},
             {"task": "Dry to 14% moisture for storage", "priority": "high", "day": 110}
         ]}
    ]
}

# Add Groundnut
data['crops']['Groundnut'] = {
    "name_te": "వేరుశెనగ",
    "total_duration_days": 120,
    "seasons": ["Kharif", "Rabi", "Summer"],
    "water_requirement_mm": 450,
    "stages": [
        {"id": 1, "name": "Emergence", "name_te": "మొలకెత్తుట", "start_day": 0, "end_day": 15,
         "critical_activities": [
             {"task": "Treat seeds with Thiram + Carbendazim", "priority": "high", "day": 1},
             {"task": "Rhizobium seed inoculation", "priority": "high", "day": 1},
             {"task": "Sow at 5 cm depth", "priority": "high", "day": 1},
             {"task": "Apply Gypsum 200 kg/acre at sowing", "priority": "high", "day": 1}
         ],
         "disease_focus": ["Collar rot", "Root rot"]},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార దశ", "start_day": 15, "end_day": 35,
         "critical_activities": [
             {"task": "First weeding", "priority": "high", "day": 20},
             {"task": "Scout for Thrips and Jassids", "priority": "high", "day": 20},
             {"task": "Apply basal fertilizer if not applied", "priority": "medium", "day": 15}
         ],
         "pest_focus": ["Thrips", "Jassids", "Aphids"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత దశ", "start_day": 35, "end_day": 50,
         "critical_activities": [
             {"task": "Apply Gypsum 2nd dose 100 kg/acre", "priority": "high", "day": 40},
             {"task": "Critical irrigation at flowering", "priority": "critical", "day": 40},
             {"task": "Scout for Spodoptera", "priority": "high", "day": 45},
             {"task": "Earthing up to help pegging", "priority": "high", "day": 45}
         ],
         "weather_sensitivity": {"drought": "CRITICAL"}},
        {"id": 4, "name": "Pegging", "name_te": "గూర్చి దశ", "start_day": 50, "end_day": 70,
         "critical_activities": [
             {"task": "Maintain soil moisture for peg penetration", "priority": "critical", "day": 55},
             {"task": "Second earthing up", "priority": "high", "day": 55},
             {"task": "Scout for leaf miner", "priority": "medium", "day": 60}
         ]},
        {"id": 5, "name": "Pod Development", "name_te": "కాయ అభివృద్ధి", "start_day": 70, "end_day": 100,
         "critical_activities": [
             {"task": "Irrigate at critical pod filling", "priority": "high", "day": 75},
             {"task": "Scout for Tikka disease", "priority": "high", "day": 80},
             {"task": "Spray Mancozeb if Tikka >25% incidence", "priority": "high", "day": 85}
         ],
         "disease_focus": ["Tikka disease", "Rust"]},
        {"id": 6, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 100, "end_day": 120,
         "critical_activities": [
             {"task": "Stop irrigation 10 days before harvest", "priority": "high", "day": 100},
             {"task": "Check pod maturity - 70% pods mature", "priority": "high", "day": 110},
             {"task": "Harvest, dry pods immediately", "priority": "high", "day": 115}
         ]}
    ]
}

# Add Chilli
data['crops']['Chilli'] = {
    "name_te": "మిర్చి",
    "total_duration_days": 180,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 800,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 30,
         "critical_activities": [
             {"task": "Raise nursery in raised beds", "priority": "high", "day": 1},
             {"task": "Treat seeds with Trichoderma", "priority": "high", "day": 1},
             {"task": "Cover with mulch until germination", "priority": "medium", "day": 1},
             {"task": "Light irrigation daily", "priority": "high", "day": 5},
             {"task": "Harden seedlings before transplant", "priority": "medium", "day": 25}
         ],
         "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Transplanting", "name_te": "నాటుట", "start_day": 30, "end_day": 40,
         "critical_activities": [
             {"task": "Transplant 30-35 day old seedlings", "priority": "high", "day": 30},
             {"task": "Maintain 60x45 cm spacing", "priority": "high", "day": 30},
             {"task": "Irrigate immediately after transplanting", "priority": "critical", "day": 30},
             {"task": "Gap filling within 10 days", "priority": "medium", "day": 38}
         ]},
        {"id": 3, "name": "Vegetative", "name_te": "శాకాహార దశ", "start_day": 40, "end_day": 70,
         "critical_activities": [
             {"task": "First weeding and hoeing", "priority": "high", "day": 45},
             {"task": "Apply first nitrogen dose", "priority": "high", "day": 50},
             {"task": "Scout for Thrips weekly", "priority": "critical", "day": 45},
             {"task": "Spray Fipronil if Thrips >5/leaf", "priority": "high", "day": 55},
             {"task": "Second weeding", "priority": "high", "day": 65}
         ],
         "pest_focus": ["Thrips", "Mites", "Aphids"]},
        {"id": 4, "name": "Flowering", "name_te": "పూత దశ", "start_day": 70, "end_day": 95,
         "critical_activities": [
             {"task": "Critical irrigation - avoid stress", "priority": "critical", "day": 75},
             {"task": "Apply second nitrogen + potash", "priority": "high", "day": 80},
             {"task": "Scout for fruit borer", "priority": "high", "day": 85},
             {"task": "Spray Spinosad for fruit borer", "priority": "high", "day": 90}
         ],
         "pest_focus": ["Fruit borer", "Thrips"], "disease_focus": ["Anthracnose"]},
        {"id": 5, "name": "Fruiting", "name_te": "కాయ దశ", "start_day": 95, "end_day": 140,
         "critical_activities": [
             {"task": "Regular irrigation every 7-10 days", "priority": "high", "day": 100},
             {"task": "Scout for fruit rot", "priority": "high", "day": 110},
             {"task": "Spray Copper oxychloride for fruit rot", "priority": "medium", "day": 115},
             {"task": "First harvest of green chillies", "priority": "high", "day": 100},
             {"task": "Continue picking every 10-15 days", "priority": "high", "day": 115}
         ],
         "disease_focus": ["Fruit rot", "Powdery mildew", "Leaf curl"]},
        {"id": 6, "name": "Peak Harvest", "name_te": "గరిష్ట కోత", "start_day": 140, "end_day": 170,
         "critical_activities": [
             {"task": "Harvest red chillies for dry chilli", "priority": "high", "day": 145},
             {"task": "Dry chillies to 10% moisture", "priority": "high", "day": 150},
             {"task": "Continue pickings every 10 days", "priority": "high", "day": 160}
         ]},
        {"id": 7, "name": "Final Harvest", "name_te": "చివరి కోత", "start_day": 170, "end_day": 180,
         "critical_activities": [
             {"task": "Complete final picking", "priority": "high", "day": 175},
             {"task": "Remove and destroy plant debris", "priority": "medium", "day": 180}
         ]}
    ]
}

# Save updated file
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Added 4 more crops to database")
for crop in data['crops']:
    print(f"   {crop}: {len(data['crops'][crop]['stages'])} stages")
