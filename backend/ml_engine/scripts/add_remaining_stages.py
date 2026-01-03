"""
Add complete stages for ALL remaining crops in the system
Target: Barley, Millets, Pulses, Oil Seeds, Tobacco, Cabbage, Cauliflower, Carrot, Mango, Papaya, Guava
"""
import json

stages_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_stages_complete.json"
with open(stages_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Add Barley stages
data['crops']['Barley'] = {
    "name_te": "బార్లీ",
    "total_duration_days": 120,
    "seasons": ["Rabi"],
    "water_requirement_mm": 350,
    "stages": [
        {"id": 1, "name": "Sowing", "name_te": "విత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Treat seeds with Carbendazim 2g/kg", "priority": "high", "day": 1},
            {"task": "Sow seeds at 3-4 cm depth", "priority": "high", "day": 1},
            {"task": "Apply DAP 50 kg/ha at sowing", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": ["Seedling blight"]},
        {"id": 2, "name": "Crown Root Initiation", "name_te": "వేరు మొక్కలు", "start_day": 11, "end_day": 25,
         "critical_activities": [
            {"task": "First irrigation at CRI stage (18-21 DAS)", "priority": "critical", "day": 20},
            {"task": "Apply 1/3 nitrogen (Urea 40 kg/ha)", "priority": "high", "day": 20}
         ],
         "pest_focus": ["Aphids"], "disease_focus": []},
        {"id": 3, "name": "Tillering", "name_te": "పిల్లలు పట్టడం", "start_day": 26, "end_day": 45,
         "critical_activities": [
            {"task": "Second irrigation at 40-45 DAS", "priority": "high", "day": 42},
            {"task": "Apply remaining nitrogen", "priority": "high", "day": 42},
            {"task": "Hand weed or apply herbicide", "priority": "medium", "day": 30}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Stripe rust"]},
        {"id": 4, "name": "Jointing", "name_te": "కణుపు", "start_day": 46, "end_day": 65,
         "critical_activities": [
            {"task": "Third irrigation", "priority": "high", "day": 55}
         ],
         "pest_focus": [], "disease_focus": ["Powdery mildew"]},
        {"id": 5, "name": "Heading", "name_te": "కంకి", "start_day": 66, "end_day": 85,
         "critical_activities": [
            {"task": "Critical irrigation at heading", "priority": "critical", "day": 75},
            {"task": "Scout for aphids", "priority": "high", "day": 70}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Loose smut"]},
        {"id": 6, "name": "Grain Filling", "name_te": "గింజ నింపు", "start_day": 86, "end_day": 105,
         "critical_activities": [
            {"task": "Fifth irrigation if soil dry", "priority": "medium", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 7, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 106, "end_day": 120,
         "critical_activities": [
            {"task": "Stop irrigation 15 days before harvest", "priority": "high", "day": 105},
            {"task": "Harvest when grain hard and golden", "priority": "high", "day": 118}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Millets stages
data['crops']['Millets'] = {
    "name_te": "చిరుధాన్యాలు",
    "total_duration_days": 90,
    "seasons": ["Kharif"],
    "water_requirement_mm": 350,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Sow seeds at 2-3 cm depth", "priority": "high", "day": 1},
            {"task": "Apply FYM before sowing", "priority": "medium", "day": 1}
         ],
         "pest_focus": ["Shootfly"], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 11, "end_day": 40,
         "critical_activities": [
            {"task": "Thinning to maintain spacing", "priority": "high", "day": 15},
            {"task": "Apply Urea 20 kg/acre", "priority": "medium", "day": 25}
         ],
         "pest_focus": ["Stem borer"], "disease_focus": ["Downy mildew"]},
        {"id": 3, "name": "Heading", "name_te": "కంకి", "start_day": 41, "end_day": 60,
         "critical_activities": [
            {"task": "Critical irrigation if no rain", "priority": "high", "day": 50}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 4, "name": "Grain Filling", "name_te": "గింజ నింపు", "start_day": 61, "end_day": 80,
         "critical_activities": [
            {"task": "Scout for head midge", "priority": "medium", "day": 70}
         ],
         "pest_focus": ["Head midge"], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 81, "end_day": 90,
         "critical_activities": [
            {"task": "Harvest when grains hard", "priority": "high", "day": 88}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Pulses stages
data['crops']['Pulses'] = {
    "name_te": "పప్పుధాన్యాలు",
    "total_duration_days": 100,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 300,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Rhizobium seed treatment", "priority": "high", "day": 1},
            {"task": "Sow at 3-4 cm depth", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 11, "end_day": 40,
         "critical_activities": [
            {"task": "Weeding at 20-25 DAS", "priority": "high", "day": 22},
            {"task": "Apply DAP if needed", "priority": "medium", "day": 15}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": ["Wilt"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 41, "end_day": 60,
         "critical_activities": [
            {"task": "Critical irrigation if dry", "priority": "high", "day": 50},
            {"task": "Scout for pod borer", "priority": "critical", "day": 50}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": []},
        {"id": 4, "name": "Pod Formation", "name_te": "కాయ ఏర్పాటు", "start_day": 61, "end_day": 85,
         "critical_activities": [
            {"task": "Spray for pod borer if needed", "priority": "high", "day": 70}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 86, "end_day": 100,
         "critical_activities": [
            {"task": "Harvest when pods turn brown", "priority": "high", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Oil Seeds stages  
data['crops']['Oil Seeds'] = {
    "name_te": "నూనెగింజలు",
    "total_duration_days": 100,
    "seasons": ["Rabi", "Kharif"],
    "water_requirement_mm": 350,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Sow at 2-3 cm depth", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 11, "end_day": 35,
         "critical_activities": [
            {"task": "Thinning and weeding", "priority": "high", "day": 20},
            {"task": "Apply Sulphur fertilizer", "priority": "high", "day": 25}
         ],
         "pest_focus": ["Aphids"], "disease_focus": []},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 36, "end_day": 55,
         "critical_activities": [
            {"task": "Irrigation at flowering", "priority": "critical", "day": 45}
         ],
         "pest_focus": ["Painted bug"], "disease_focus": ["White rust"]},
        {"id": 4, "name": "Pod/Capsule Development", "name_te": "కాయ అభివృద్ధి", "start_day": 56, "end_day": 85,
         "critical_activities": [
            {"task": "Second irrigation", "priority": "high", "day": 70}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 86, "end_day": 100,
         "critical_activities": [
            {"task": "Harvest when plants turn yellow", "priority": "high", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Tobacco stages
data['crops']['Tobacco'] = {
    "name_te": "పొగాకు",
    "total_duration_days": 150,
    "seasons": ["Rabi"],
    "water_requirement_mm": 450,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 45,
         "critical_activities": [
            {"task": "Prepare raised nursery beds", "priority": "high", "day": 1},
            {"task": "Sow seeds thinly", "priority": "high", "day": 1}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Transplanting", "name_te": "నాటుట", "start_day": 45, "end_day": 55,
         "critical_activities": [
            {"task": "Transplant 8-10 week old seedlings", "priority": "high", "day": 45}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 3, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 56, "end_day": 90,
         "critical_activities": [
            {"task": "Apply NPK fertilizer", "priority": "high", "day": 60},
            {"task": "Weeding", "priority": "high", "day": 65}
         ],
         "pest_focus": ["Tobacco caterpillar"], "disease_focus": []},
        {"id": 4, "name": "Topping/Flowering", "name_te": "పూత తొలగింపు", "start_day": 91, "end_day": 120,
         "critical_activities": [
            {"task": "Remove flower heads (topping)", "priority": "critical", "day": 95},
            {"task": "Apply sucker control chemical", "priority": "high", "day": 96}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 5, "name": "Maturity/Harvest", "name_te": "పరిపక్వత", "start_day": 121, "end_day": 150,
         "critical_activities": [
            {"task": "Harvest mature leaves bottom up", "priority": "high", "day": 130},
            {"task": "Cure leaves properly", "priority": "high", "day": 135}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Cabbage stages
data['crops']['Cabbage'] = {
    "name_te": "క్యాబేజ్",
    "total_duration_days": 100,
    "seasons": ["Rabi"],
    "water_requirement_mm": 400,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 25,
         "critical_activities": [
            {"task": "Sow seeds in raised beds", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Transplanting", "name_te": "నాటుట", "start_day": 25, "end_day": 35,
         "critical_activities": [
            {"task": "Transplant 4-5 leaf seedlings", "priority": "high", "day": 25},
            {"task": "Apply basal fertilizer", "priority": "high", "day": 25}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 3, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 36, "end_day": 55,
         "critical_activities": [
            {"task": "Apply nitrogen top dressing", "priority": "high", "day": 40},
            {"task": "Scout for Diamond Back Moth", "priority": "high", "day": 45}
         ],
         "pest_focus": ["Diamond Back Moth", "Aphids"], "disease_focus": []},
        {"id": 4, "name": "Head Formation", "name_te": "తల ఏర్పాటు", "start_day": 56, "end_day": 85,
         "critical_activities": [
            {"task": "Regular irrigation", "priority": "high", "day": 60},
            {"task": "Apply Boron if deficient", "priority": "medium", "day": 65}
         ],
         "pest_focus": ["Cabbage looper"], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 86, "end_day": 100,
         "critical_activities": [
            {"task": "Harvest when heads firm", "priority": "high", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Cauliflower stages
data['crops']['Cauliflower'] = {
    "name_te": "కాలీఫ్లవర్",
    "total_duration_days": 110,
    "seasons": ["Rabi"],
    "water_requirement_mm": 450,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Sow seeds in raised beds", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Transplanting", "name_te": "నాటుట", "start_day": 30, "end_day": 40,
         "critical_activities": [
            {"task": "Transplant 4-5 week old seedlings", "priority": "high", "day": 30}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 3, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 41, "end_day": 60,
         "critical_activities": [
            {"task": "Apply nitrogen top dressing", "priority": "high", "day": 45},
            {"task": "Scout for Diamond Back Moth", "priority": "high", "day": 50}
         ],
         "pest_focus": ["Diamond Back Moth"], "disease_focus": []},
        {"id": 4, "name": "Curd Formation", "name_te": "కర్డ్ ఏర్పాటు", "start_day": 61, "end_day": 90,
         "critical_activities": [
            {"task": "Blanch curds by tying leaves", "priority": "high", "day": 70},
            {"task": "Apply Boron and Molybdenum", "priority": "medium", "day": 65}
         ],
         "pest_focus": [], "disease_focus": ["Black rot"]},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 91, "end_day": 110,
         "critical_activities": [
            {"task": "Harvest white compact curds", "priority": "high", "day": 100}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Carrot stages
data['crops']['Carrot'] = {
    "name_te": "క్యారెట్",
    "total_duration_days": 100,
    "seasons": ["Rabi"],
    "water_requirement_mm": 400,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 15,
         "critical_activities": [
            {"task": "Sow seeds in raised beds", "priority": "high", "day": 1},
            {"task": "Keep soil moist", "priority": "high", "day": 5}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 16, "end_day": 45,
         "critical_activities": [
            {"task": "Thinning to 5 cm spacing", "priority": "high", "day": 25},
            {"task": "Weeding", "priority": "high", "day": 30}
         ],
         "pest_focus": ["Carrot fly"], "disease_focus": []},
        {"id": 3, "name": "Root Development", "name_te": "వేరు అభివృద్ధి", "start_day": 46, "end_day": 80,
         "critical_activities": [
            {"task": "Regular irrigation", "priority": "high", "day": 55},
            {"task": "Earthing up to prevent green shoulders", "priority": "medium", "day": 60}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 4, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 81, "end_day": 100,
         "critical_activities": [
            {"task": "Harvest when roots 2-3 cm diameter", "priority": "high", "day": 90}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Mango stages (perennial)
data['crops']['Mango'] = {
    "name_te": "మామిడి",
    "total_duration_days": 180,
    "seasons": ["Kharif"],
    "water_requirement_mm": 800,
    "stages": [
        {"id": 1, "name": "Dormancy", "name_te": "నిద్రావస్థ", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Prune dead/diseased branches", "priority": "high", "day": 10},
            {"task": "Apply FYM and fertilizer", "priority": "high", "day": 15}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Flowering", "name_te": "పూత", "start_day": 31, "end_day": 60,
         "critical_activities": [
            {"task": "Spray against hoppers", "priority": "critical", "day": 35},
            {"task": "Spray fungicide for powdery mildew", "priority": "high", "day": 40}
         ],
         "pest_focus": ["Mango hopper", "Mealy bug"], "disease_focus": ["Powdery mildew"]},
        {"id": 3, "name": "Fruit Set", "name_te": "కాయ కట్టడం", "start_day": 61, "end_day": 90,
         "critical_activities": [
            {"task": "Second spray for hoppers", "priority": "high", "day": 70},
            {"task": "Light irrigation", "priority": "medium", "day": 75}
         ],
         "pest_focus": ["Mango hopper"], "disease_focus": ["Anthracnose"]},
        {"id": 4, "name": "Fruit Development", "name_te": "కాయ అభివృద్ధి", "start_day": 91, "end_day": 140,
         "critical_activities": [
            {"task": "Spray for fruit fly control", "priority": "high", "day": 110},
            {"task": "Apply potash fertilizer", "priority": "medium", "day": 100}
         ],
         "pest_focus": ["Fruit fly", "Stone weevil"], "disease_focus": []},
        {"id": 5, "name": "Maturity/Harvest", "name_te": "పరిపక్వత", "start_day": 141, "end_day": 180,
         "critical_activities": [
            {"task": "Harvest at mature green stage", "priority": "high", "day": 160},
            {"task": "Post-harvest treatment", "priority": "medium", "day": 165}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Papaya stages
data['crops']['Papaya'] = {
    "name_te": "బొప్పాయి",
    "total_duration_days": 180,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 600,
    "stages": [
        {"id": 1, "name": "Planting", "name_te": "నాటడం", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Plant 2-month old seedlings in pits", "priority": "high", "day": 1},
            {"task": "Apply FYM and basal dose", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 31, "end_day": 90,
         "critical_activities": [
            {"task": "Regular irrigation", "priority": "high", "day": 40},
            {"task": "Apply NPK monthly", "priority": "high", "day": 60}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Ring spot virus"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 91, "end_day": 120,
         "critical_activities": [
            {"task": "Identify and thin hermaphrodite plants", "priority": "medium", "day": 100}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 4, "name": "Fruiting", "name_te": "కాయ దశ", "start_day": 121, "end_day": 160,
         "critical_activities": [
            {"task": "Continue monthly fertilizer", "priority": "high", "day": 140},
            {"task": "Prop plants if needed", "priority": "medium", "day": 145}
         ],
         "pest_focus": ["Fruit fly"], "disease_focus": []},
        {"id": 5, "name": "Harvest", "name_te": "కోత", "start_day": 161, "end_day": 180,
         "critical_activities": [
            {"task": "Harvest when fruit turns yellow", "priority": "high", "day": 170}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Guava stages
data['crops']['Guava'] = {
    "name_te": "జామ",
    "total_duration_days": 150,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 500,
    "stages": [
        {"id": 1, "name": "Dormancy/Pruning", "name_te": "కత్తిరింపు", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Prune trees for canopy management", "priority": "high", "day": 10},
            {"task": "Apply FYM and NPK", "priority": "high", "day": 15}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Flowering", "name_te": "పూత", "start_day": 31, "end_day": 60,
         "critical_activities": [
            {"task": "Spray for fruit fly control", "priority": "high", "day": 45},
            {"task": "Light irrigation", "priority": "medium", "day": 50}
         ],
         "pest_focus": ["Fruit fly"], "disease_focus": ["Wilt"]},
        {"id": 3, "name": "Fruit Set", "name_te": "కాయ కట్టడం", "start_day": 61, "end_day": 90,
         "critical_activities": [
            {"task": "Thin excess fruits if needed", "priority": "medium", "day": 75},
            {"task": "Continue pest management", "priority": "high", "day": 80}
         ],
         "pest_focus": ["Fruit borer"], "disease_focus": []},
        {"id": 4, "name": "Fruit Development", "name_te": "కాయ అభివృద్ధి", "start_day": 91, "end_day": 130,
         "critical_activities": [
            {"task": "Apply potash", "priority": "medium", "day": 100}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 5, "name": "Harvest", "name_te": "కోత", "start_day": 131, "end_day": 150,
         "critical_activities": [
            {"task": "Harvest at mature green/light yellow", "priority": "high", "day": 140}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

# Add Ground Nuts (alias for Groundnut)
if 'Ground Nuts' not in data['crops'] and 'Groundnut' in data['crops']:
    data['crops']['Ground Nuts'] = data['crops']['Groundnut']

# Save updated data
with open(stages_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Count stats
total_crops = len(data['crops'])
total_stages = sum(len(c.get('stages', [])) for c in data['crops'].values())
print(f"✅ Updated to {total_crops} crops with {total_stages} stages")
print("\nAll crops now covered:")
for crop in sorted(data['crops'].keys()):
    stages = len(data['crops'][crop].get('stages', []))
    print(f"   {crop}: {stages} stages")
