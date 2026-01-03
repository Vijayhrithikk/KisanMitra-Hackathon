"""
Expand comprehensive data to ALL crops in the system
Adding stages and FAQs for 21 additional crops
"""
import json
from datetime import datetime

# Load existing data
stages_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_stages_complete.json"
faqs_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_faqs_complete.json"

with open(stages_path, 'r', encoding='utf-8') as f:
    stages_data = json.load(f)

with open(faqs_path, 'r', encoding='utf-8') as f:
    faqs_data = json.load(f)

# ===== WHEAT =====
stages_data['crops']['Wheat'] = {
    "name_te": "గోధుమ",
    "total_duration_days": 120,
    "seasons": ["Rabi"],
    "water_requirement_mm": 450,
    "stages": [
        {"id": 1, "name": "Sowing", "name_te": "విత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Select certified seeds (100 kg/ha)", "priority": "high", "day": 1},
            {"task": "Treat seeds with Thiram + Carbendazim", "priority": "high", "day": 1},
            {"task": "Apply DAP 100 kg/ha at sowing", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": ["Seedling blight"]},
        {"id": 2, "name": "Crown Root Initiation", "name_te": "కిరీటపు వేరు", "start_day": 11, "end_day": 25,
         "critical_activities": [
            {"task": "First irrigation at 20-25 DAS", "priority": "critical", "day": 21},
            {"task": "Apply 1/3 Nitrogen (Urea)", "priority": "high", "day": 21}
         ],
         "pest_focus": ["Aphids"], "disease_focus": []},
        {"id": 3, "name": "Tillering", "name_te": "పిల్లలు పట్టడం", "start_day": 26, "end_day": 45,
         "critical_activities": [
            {"task": "Second irrigation at 40-45 DAS", "priority": "high", "day": 40},
            {"task": "Apply remaining 1/3 Nitrogen", "priority": "high", "day": 40}
         ],
         "pest_focus": ["Termites", "Brown wheat mite"], "disease_focus": ["Yellow rust"]},
        {"id": 4, "name": "Jointing", "name_te": "కణుపు", "start_day": 46, "end_day": 65,
         "critical_activities": [
            {"task": "Third irrigation", "priority": "high", "day": 60}
         ],
         "pest_focus": [], "disease_focus": ["Powdery mildew"]},
        {"id": 5, "name": "Heading/Flowering", "name_te": "పూత", "start_day": 66, "end_day": 85,
         "critical_activities": [
            {"task": "Critical irrigation at flowering", "priority": "critical", "day": 75},
            {"task": "Scout for aphids", "priority": "high", "day": 70}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Loose smut", "Karnal bunt"]},
        {"id": 6, "name": "Grain Filling", "name_te": "గింజ నింపు", "start_day": 86, "end_day": 105,
         "critical_activities": [
            {"task": "Fifth irrigation", "priority": "high", "day": 90}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 7, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 106, "end_day": 120,
         "critical_activities": [
            {"task": "Stop irrigation 15 days before harvest", "priority": "medium", "day": 105},
            {"task": "Harvest at golden yellow color", "priority": "high", "day": 120}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Wheat'] = {"faqs": [
    {"stage": "sowing", "category": "seed", "urgency": "high",
     "question_en": "What is the ideal seed rate for wheat?",
     "question_te": "గోధుమకు ఆదర్శ విత్తన రేటు ఎంత?",
     "answer_en": "100 kg/ha for timely sowing, 125 kg/ha for late sowing.",
     "answer_te": "సకాలంలో విత్తడానికి 100 కిలో/హె, ఆలస్యంగా విత్తడానికి 125 కిలో/హె.",
     "action_en": "Use certified seeds. Treat with fungicide before sowing.",
     "action_te": "ధృవీకరించిన విత్తనాలు వాడండి. విత్తడానికి ముందు బూజు మందుతో శుద్ధి చేయండి."},
    {"stage": "tillering", "category": "disease", "urgency": "critical",
     "question_en": "Yellow-orange pustules appearing on leaves",
     "question_te": "ఆకులపై పసుపు-నారింజ బొబ్బలు కనిపిస్తున్నాయి",
     "answer_en": "Yellow Rust (Puccinia striiformis). Most serious wheat disease.",
     "answer_te": "ఎల్లో రస్ట్. అత్యంత తీవ్రమైన గోధుమ వ్యాధి.",
     "action_en": "Spray Propiconazole 25 EC @ 1ml/L immediately. Repeat after 15 days.",
     "action_te": "వెంటనే ప్రొపికొనాజోల్ పిచికారీ. 15 రోజుల తర్వాత మళ్ళీ."},
    {"stage": "flowering", "category": "pest", "urgency": "high",
     "question_en": "Green insects clustering on wheat heads",
     "question_te": "గోధుమ కంకులపై ఆకుపచ్చ పురుగులు గుంపులుగా",
     "answer_en": "Wheat Aphids. Suck sap and reduce grain filling.",
     "answer_te": "గోధుమ ఆఫిడ్లు. రసం పీల్చి గింజ నింపు తగ్గిస్తాయి.",
     "action_en": "Spray Imidacloprid 17.8 SL @ 0.3ml/L or Dimethoate 30 EC @ 1.5ml/L.",
     "action_te": "ఇమిడాక్లోప్రిడ్ లేదా డైమిథోయేట్ పిచికారీ."},
]}

# ===== SUGARCANE =====
stages_data['crops']['Sugarcane'] = {
    "name_te": "చెరకు",
    "total_duration_days": 365,
    "seasons": ["Kharif", "Rabi", "Zaid"],
    "water_requirement_mm": 2000,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 35,
         "critical_activities": [
            {"task": "Plant 3-budded setts", "priority": "high", "day": 1},
            {"task": "Treat setts with fungicide", "priority": "high", "day": 1},
            {"task": "Light irrigation every 5-7 days", "priority": "high", "day": 5}
         ],
         "pest_focus": ["Termites"], "disease_focus": ["Sett rot"]},
        {"id": 2, "name": "Tillering", "name_te": "పిల్లలు పట్టడం", "start_day": 36, "end_day": 120,
         "critical_activities": [
            {"task": "Apply 100 kg Urea/ha", "priority": "high", "day": 45},
            {"task": "Earthing up", "priority": "high", "day": 60},
            {"task": "Trash mulching", "priority": "medium", "day": 60}
         ],
         "pest_focus": ["Early shoot borer"], "disease_focus": []},
        {"id": 3, "name": "Grand Growth", "name_te": "వేగవంత పెరుగుదల", "start_day": 121, "end_day": 270,
         "critical_activities": [
            {"task": "Regular irrigation (7-10 days interval)", "priority": "high", "day": 130},
            {"task": "Apply remaining nitrogen in splits", "priority": "high", "day": 150}
         ],
         "pest_focus": ["Internode borer", "Top borer"], "disease_focus": ["Red rot"]},
        {"id": 4, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 271, "end_day": 365,
         "critical_activities": [
            {"task": "Stop nitrogen 2 months before harvest", "priority": "high", "day": 300},
            {"task": "Stop irrigation 15 days before harvest", "priority": "medium", "day": 350}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Sugarcane'] = {"faqs": [
    {"stage": "tillering", "category": "pest", "urgency": "critical",
     "question_en": "Dead hearts appearing in young sugarcane",
     "question_te": "యువ చెరకులో డెడ్ హార్ట్స్ కనిపిస్తున్నాయి",
     "answer_en": "Early Shoot Borer (Chilo infuscatellus). Major pest in formative stage.",
     "answer_te": "ఎర్లీ షూట్ బోరర్. నిర్మాణ దశలో ప్రధాన పురుగు.",
     "action_en": "Apply Carbofuran 3G @ 30 kg/ha. Or spray Chlorantraniliprole.",
     "action_te": "కార్బోఫ్యూరాన్ వేయండి. లేదా క్లోరాంట్రానిలిప్రోల్ పిచికారీ."},
    {"stage": "grand_growth", "category": "disease", "urgency": "critical",
     "question_en": "Red color in split canes, alcohol smell",
     "question_te": "చీల్చిన చెరకులో ఎరుపు రంగు, మద్యం వాసన",
     "answer_en": "Red Rot (Colletotrichum falcatum). Most destructive disease.",
     "answer_te": "రెడ్ రాట్. అత్యంత వినాశకరమైన వ్యాధి.",
     "action_en": "No cure. Remove and destroy infected clumps. Use resistant varieties.",
     "action_te": "చికిత్స లేదు. సోకిన గుంపులు తీసివేయండి. నిరోధక రకాలు వాడండి."},
]}

# ===== TOMATO =====
stages_data['crops']['Tomato'] = {
    "name_te": "టమాటా",
    "total_duration_days": 120,
    "seasons": ["Kharif", "Rabi", "Zaid"],
    "water_requirement_mm": 600,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 25,
         "critical_activities": [
            {"task": "Sow seeds in raised beds", "priority": "high", "day": 1},
            {"task": "Transplant at 4-5 leaf stage", "priority": "high", "day": 25}
         ],
         "pest_focus": ["Damping off"], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 26, "end_day": 45,
         "critical_activities": [
            {"task": "Staking plants", "priority": "high", "day": 30},
            {"task": "Apply NPK fertilizer", "priority": "high", "day": 35}
         ],
         "pest_focus": ["Whitefly", "Aphids"], "disease_focus": ["Early blight"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 46, "end_day": 65,
         "critical_activities": [
            {"task": "Spray Boron for fruit set", "priority": "medium", "day": 50}
         ],
         "pest_focus": ["Fruit borer"], "disease_focus": ["Bacterial wilt"]},
        {"id": 4, "name": "Fruiting", "name_te": "కాయ దశ", "start_day": 66, "end_day": 90,
         "critical_activities": [
            {"task": "Regular irrigation", "priority": "high", "day": 70},
            {"task": "Scout for fruit borer", "priority": "high", "day": 75}
         ],
         "pest_focus": ["Fruit borer", "Leaf miner"], "disease_focus": ["Late blight"]},
        {"id": 5, "name": "Harvest", "name_te": "కోత", "start_day": 91, "end_day": 120,
         "critical_activities": [
            {"task": "Pick at breaker stage for long transport", "priority": "medium", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Tomato'] = {"faqs": [
    {"stage": "fruiting", "category": "pest", "urgency": "critical",
     "question_en": "Holes in fruits with caterpillar inside",
     "question_te": "కాయలలో రంధ్రాలు, లోపల పురుగు",
     "answer_en": "Tomato Fruit Borer (Helicoverpa armigera). Major pest.",
     "answer_te": "టమాటా ఫ్రూట్ బోరర్. ప్రధాన పురుగు.",
     "action_en": "Spray Spinosad 45 SC @ 0.3ml/L. Install pheromone traps.",
     "action_te": "స్పినోసాడ్ పిచికారీ. ఫెరమోన్ ట్రాప్స్ పెట్టండి."},
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Plants suddenly wilting despite watering",
     "question_te": "నీరు పెట్టినా మొక్కలు హఠాత్తుగా వాడిపోతున్నాయి",
     "answer_en": "Bacterial Wilt. No cure available.",
     "answer_te": "బాక్టీరియల్ విల్ట్. చికిత్స లేదు.",
     "action_en": "Remove infected plants. Crop rotation. Use resistant varieties.",
     "action_te": "సోకిన మొక్కలు తీసివేయండి. పంట మార్పిడి. నిరోధక రకాలు వాడండి."},
    {"stage": "fruiting", "category": "disease", "urgency": "medium",
     "question_en": "Black sunken area at bottom of fruit",
     "question_te": "కాయ దిగువన నల్లని కుంగిన ప్రాంతం",
     "answer_en": "Blossom End Rot - Calcium deficiency disorder.",
     "answer_te": "బ్లాసమ్ ఎండ్ రాట్ - కాల్షియం లోపం.",
     "action_en": "Spray Calcium Chloride 0.5%. Maintain regular irrigation.",
     "action_te": "కాల్షియం క్లోరైడ్ 0.5% పిచికారీ. క్రమబద్ధమైన నీటిపారుదల."},
]}

# ===== ONION =====
stages_data['crops']['Onion'] = {
    "name_te": "ఉల్లిపాయ",
    "total_duration_days": 120,
    "seasons": ["Rabi", "Kharif"],
    "water_requirement_mm": 500,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 45,
         "critical_activities": [
            {"task": "Sow seeds in raised beds", "priority": "high", "day": 1},
            {"task": "Transplant healthy seedlings", "priority": "high", "day": 45}
         ],
         "pest_focus": [], "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 46, "end_day": 70,
         "critical_activities": [
            {"task": "Apply Nitrogen top dressing", "priority": "high", "day": 55}
         ],
         "pest_focus": ["Thrips"], "disease_focus": []},
        {"id": 3, "name": "Bulb Formation", "name_te": "గడ్డ ఏర్పాటు", "start_day": 71, "end_day": 100,
         "critical_activities": [
            {"task": "Reduce nitrogen", "priority": "medium", "day": 75},
            {"task": "Regular irrigation", "priority": "high", "day": 80}
         ],
         "pest_focus": ["Thrips"], "disease_focus": ["Purple blotch"]},
        {"id": 4, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 101, "end_day": 120,
         "critical_activities": [
            {"task": "Stop irrigation when tops fall", "priority": "high", "day": 105},
            {"task": "Harvest when 50% tops fall", "priority": "high", "day": 115}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Onion'] = {"faqs": [
    {"stage": "vegetative", "category": "pest", "urgency": "critical",
     "question_en": "Silvery streaks on leaves, leaves curling",
     "question_te": "ఆకులపై వెండి గీతలు, ఆకులు మడతపడటం",
     "answer_en": "Thrips - Most serious onion pest. Vector for purple blotch.",
     "answer_te": "త్రిప్స్ - అత్యంత తీవ్రమైన ఉల్లి పురుగు.",
     "action_en": "Spray Fipronil 5 SC @ 2ml/L or Spinosad 45 SC @ 0.3ml/L.",
     "action_te": "ఫిప్రోనిల్ లేదా స్పినోసాడ్ పిచికారీ."},
    {"stage": "bulb", "category": "disease", "urgency": "high",
     "question_en": "Purple-brown spots on leaves spreading rapidly",
     "question_te": "ఆకులపై ఊదా-గోధుమ మచ్చలు వేగంగా వ్యాపిస్తున్నాయి",
     "answer_en": "Purple Blotch (Alternaria porri). Serious in humid conditions.",
     "answer_te": "పర్పుల్ బ్లాచ్. తేమగల పరిస్థితులలో తీవ్రం.",
     "action_en": "Spray Mancozeb 75 WP @ 2.5g/L or Chlorothalonil @ 2g/L.",
     "action_te": "మాంకోజెబ్ లేదా క్లోరోథలోనిల్ పిచికారీ."},
]}

# ===== BANANA =====
stages_data['crops']['Banana'] = {
    "name_te": "అరటి",
    "total_duration_days": 365,
    "seasons": ["Kharif", "Rabi", "Zaid"],
    "water_requirement_mm": 2000,
    "stages": [
        {"id": 1, "name": "Planting", "name_te": "నాటడం", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Plant sword suckers in pits", "priority": "high", "day": 1},
            {"task": "Apply FYM 10 kg/pit", "priority": "high", "day": 1}
         ],
         "pest_focus": ["Rhizome weevil"], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 31, "end_day": 180,
         "critical_activities": [
            {"task": "Apply NPK in splits", "priority": "high", "day": 60},
            {"task": "Desuckering", "priority": "medium", "day": 90}
         ],
         "pest_focus": ["Banana aphid", "Stem weevil"], "disease_focus": ["Panama wilt"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 181, "end_day": 240,
         "critical_activities": [
            {"task": "Propping/Staking", "priority": "high", "day": 200}
         ],
         "pest_focus": [], "disease_focus": ["Sigatoka leaf spot"]},
        {"id": 4, "name": "Bunch Development", "name_te": "గెల అభివృద్ధి", "start_day": 241, "end_day": 330,
         "critical_activities": [
            {"task": "Remove male bud", "priority": "medium", "day": 250},
            {"task": "Bunch covering", "priority": "medium", "day": 260}
         ],
         "pest_focus": ["Scarring beetle"], "disease_focus": []},
        {"id": 5, "name": "Harvest", "name_te": "కోత", "start_day": 331, "end_day": 365,
         "critical_activities": [
            {"task": "Harvest at 75% maturity for distant markets", "priority": "high", "day": 350}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Banana'] = {"faqs": [
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Yellowing of older leaves, plants wilting",
     "question_te": "పాత ఆకులు పసుపు పడటం, మొక్కలు వాడిపోవడం",
     "answer_en": "Panama Wilt (Fusarium oxysporum). Devastating soil-borne disease.",
     "answer_te": "పనామా విల్ట్. వినాశకరమైన మట్టి ద్వారా వచ్చే వ్యాధి.",
     "action_en": "No cure. Remove infected plants. Don't replant for 3 years.",
     "action_te": "చికిత్స లేదు. సోకిన మొక్కలు తీసివేయండి. 3 సంవత్సరాలు మళ్ళీ వేయకండి."},
]}

# ===== SOYBEAN =====
stages_data['crops']['Soybean'] = {
    "name_te": "సోయాబీన్",
    "total_duration_days": 100,
    "seasons": ["Kharif"],
    "water_requirement_mm": 450,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Rhizobium seed treatment", "priority": "high", "day": 1},
            {"task": "Sow at 3-4 cm depth", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 11, "end_day": 35,
         "critical_activities": [
            {"task": "Gap filling", "priority": "medium", "day": 12},
            {"task": "Weeding", "priority": "high", "day": 20}
         ],
         "pest_focus": ["Girdle beetle", "Stem fly"], "disease_focus": []},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 36, "end_day": 55,
         "critical_activities": [
            {"task": "Critical irrigation if rain fails", "priority": "critical", "day": 45}
         ],
         "pest_focus": ["Green semilooper"], "disease_focus": ["Rust"]},
        {"id": 4, "name": "Pod Formation", "name_te": "కాయ ఏర్పాటు", "start_day": 56, "end_day": 85,
         "critical_activities": [
            {"task": "Scout for pod borer", "priority": "high", "day": 65}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 86, "end_day": 100,
         "critical_activities": [
            {"task": "Harvest when 90% pods turn brown", "priority": "high", "day": 95}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Soybean'] = {"faqs": [
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Stem girdled with ring marks",
     "question_te": "కాండంపై రింగ్ గుర్తులతో గర్డిల్ చేయబడింది",
     "answer_en": "Girdle Beetle damage. Serious pest in soybean.",
     "answer_te": "గర్డిల్ బీటిల్ నష్టం. సోయాబీన్‌లో తీవ్రమైన పురుగు.",
     "action_en": "Spray Quinalphos 25 EC @ 2ml/L. Remove affected plants.",
     "action_te": "క్వినాల్ఫాస్ పిచికారీ. నష్టపడిన మొక్కలు తీసివేయండి."},
]}

# ===== TURMERIC =====
stages_data['crops']['Turmeric'] = {
    "name_te": "పసుపు",
    "total_duration_days": 270,
    "seasons": ["Kharif"],
    "water_requirement_mm": 1500,
    "stages": [
        {"id": 1, "name": "Planting", "name_te": "నాటడం", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Plant mother/finger rhizomes", "priority": "high", "day": 1},
            {"task": "Apply FYM 25 t/ha", "priority": "high", "day": 1}
         ],
         "pest_focus": ["Rhizome scale"], "disease_focus": ["Rhizome rot"]},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 31, "end_day": 120,
         "critical_activities": [
            {"task": "Mulching with leaves", "priority": "high", "day": 40},
            {"task": "Earthing up", "priority": "high", "day": 60}
         ],
         "pest_focus": ["Shoot borer"], "disease_focus": ["Leaf blotch"]},
        {"id": 3, "name": "Rhizome Development", "name_te": "దుంప అభివృద్ధి", "start_day": 121, "end_day": 240,
         "critical_activities": [
            {"task": "Apply potash", "priority": "high", "day": 150}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 4, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 241, "end_day": 270,
         "critical_activities": [
            {"task": "Harvest when leaves dry", "priority": "high", "day": 260}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Turmeric'] = {"faqs": [
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Leaves rolling and drying from center",
     "question_te": "ఆకులు మధ్య నుండి మడతపడి ఎండిపోతున్నాయి",
     "answer_en": "Shoot Borer tunneling in pseudostem.",
     "answer_te": "షూట్ బోరర్ కాండంలో సొరంగం.",
     "action_en": "Spray Chlorpyriphos 20 EC @ 2ml/L. Remove affected shoots.",
     "action_te": "క్లోర్పైరిఫాస్ పిచికారీ. నష్టపడిన మొక్కలు తీసివేయండి."},
]}

# ===== BENGAL GRAM (Chickpea) =====
stages_data['crops']['Bengal Gram'] = {
    "name_te": "శెనగలు",
    "total_duration_days": 110,
    "seasons": ["Rabi"],
    "water_requirement_mm": 350,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 15,
         "critical_activities": [
            {"task": "Rhizobium seed treatment", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 16, "end_day": 45,
         "critical_activities": [
            {"task": "Hoeing and weeding", "priority": "high", "day": 25}
         ],
         "pest_focus": ["Cut worm"], "disease_focus": ["Wilt"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 46, "end_day": 70,
         "critical_activities": [
            {"task": "Critical irrigation if needed", "priority": "high", "day": 55}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": []},
        {"id": 4, "name": "Pod Formation", "name_te": "కాయ ఏర్పాటు", "start_day": 71, "end_day": 95,
         "critical_activities": [
            {"task": "Scout for pod borer intensively", "priority": "critical", "day": 80}
         ],
         "pest_focus": ["Pod borer"], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 96, "end_day": 110,
         "critical_activities": [
            {"task": "Harvest when pods turn straw color", "priority": "high", "day": 105}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Bengal Gram'] = {"faqs": [
    {"stage": "pod", "category": "pest", "urgency": "critical",
     "question_en": "Caterpillars eating pods at night",
     "question_te": "రాత్రి పురుగులు కాయలు తింటున్నాయి",
     "answer_en": "Gram Pod Borer (Helicoverpa armigera). Most serious pest.",
     "answer_te": "గ్రామ్ పాడ్ బోరర్. అత్యంత తీవ్రమైన పురుగు.",
     "action_en": "Spray HaNPV 250 LE/ha. Or Spinosad 45 SC in evening.",
     "action_te": "HaNPV పిచికారీ. లేదా సాయంత్రం స్పినోసాడ్."},
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Plants wilting, yellow leaves, dying in patches",
     "question_te": "మొక్కలు వాడిపోతున్నాయి, పసుపు ఆకులు, మచ్చలుగా చనిపోతున్నాయి",
     "answer_en": "Fusarium Wilt. Soil-borne disease.",
     "answer_te": "ఫ్యూసారియం విల్ట్. మట్టి ద్వారా వచ్చే వ్యాధి.",
     "action_en": "Use resistant varieties. Seed treatment with Trichoderma.",
     "action_te": "నిరోధక రకాలు వాడండి. ట్రైకోడర్మాతో విత్తన శుద్ధి."},
]}

# ===== BRINJAL =====
stages_data['crops']['Brinjal'] = {
    "name_te": "వంకాయ",
    "total_duration_days": 150,
    "seasons": ["Kharif", "Rabi"],
    "water_requirement_mm": 600,
    "stages": [
        {"id": 1, "name": "Nursery", "name_te": "నారుమడి", "start_day": 0, "end_day": 30,
         "critical_activities": [
            {"task": "Raise seedlings in nursery", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": ["Damping off"]},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 31, "end_day": 50,
         "critical_activities": [
            {"task": "Transplant at 4-5 leaf stage", "priority": "high", "day": 30}
         ],
         "pest_focus": ["Aphids", "Jassids"], "disease_focus": []},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 51, "end_day": 70,
         "critical_activities": [
            {"task": "Scout for shoot and fruit borer", "priority": "critical", "day": 55}
         ],
         "pest_focus": ["Shoot and fruit borer"], "disease_focus": []},
        {"id": 4, "name": "Fruiting", "name_te": "కాయ దశ", "start_day": 71, "end_day": 130,
         "critical_activities": [
            {"task": "Remove withered shoots regularly", "priority": "high", "day": 80}
         ],
         "pest_focus": ["Shoot and fruit borer"], "disease_focus": ["Fruit rot"]},
        {"id": 5, "name": "Harvest", "name_te": "కోత", "start_day": 131, "end_day": 150,
         "critical_activities": [
            {"task": "Pick fruits regularly", "priority": "high", "day": 135}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Brinjal'] = {"faqs": [
    {"stage": "flowering", "category": "pest", "urgency": "critical",
     "question_en": "Shoots wilting and fruits with bore holes",
     "question_te": "మొక్కలు వాడిపోతున్నాయి, కాయలలో రంధ్రాలు",
     "answer_en": "Brinjal Shoot and Fruit Borer - most damaging pest.",
     "answer_te": "వంకాయ షూట్ మరియు ఫ్రూట్ బోరర్ - అత్యంత హానికర పురుగు.",
     "action_en": "Remove affected shoots. Spray Emamectin benzoate 5 SG @ 0.4g/L.",
     "action_te": "నష్టపడిన మొక్కలు తీసివేయండి. ఎమామెక్టిన్ బెంజోయేట్ పిచికారీ."},
]}

# ===== OKRA =====
stages_data['crops']['Okra'] = {
    "name_te": "బెండకాయ",
    "total_duration_days": 100,
    "seasons": ["Kharif", "Zaid"],
    "water_requirement_mm": 400,
    "stages": [
        {"id": 1, "name": "Germination", "name_te": "మొలకెత్తడం", "start_day": 0, "end_day": 10,
         "critical_activities": [
            {"task": "Soak seeds in water before sowing", "priority": "medium", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 11, "end_day": 35,
         "critical_activities": [
            {"task": "Thinning", "priority": "medium", "day": 15}
         ],
         "pest_focus": ["Jassids", "Aphids"], "disease_focus": ["Yellow vein mosaic"]},
        {"id": 3, "name": "Flowering", "name_te": "పూత", "start_day": 36, "end_day": 50,
         "critical_activities": [
            {"task": "Regular irrigation", "priority": "high", "day": 40}
         ],
         "pest_focus": ["Shoot and fruit borer"], "disease_focus": []},
        {"id": 4, "name": "Fruiting", "name_te": "కాయ దశ", "start_day": 51, "end_day": 100,
         "critical_activities": [
            {"task": "Pick fruits every 2-3 days", "priority": "high", "day": 55}
         ],
         "pest_focus": ["Fruit borer"], "disease_focus": []}
    ]
}

faqs_data['crops']['Okra'] = {"faqs": [
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Leaves showing yellow veins, curling",
     "question_te": "ఆకులలో పసుపు ఈనెలు, మడతపడటం",
     "answer_en": "Yellow Vein Mosaic Virus - transmitted by whitefly.",
     "answer_te": "ఎల్లో వెయిన్ మొజాయిక్ వైరస్ - వైట్‌ఫ్లై ద్వారా వ్యాపిస్తుంది.",
     "action_en": "Remove infected plants. Control whitefly. Use resistant varieties.",
     "action_te": "సోకిన మొక్కలు తీసివేయండి. వైట్‌ఫ్లై నియంత్రించండి. నిరోధక రకాలు వాడండి."},
]}

# ===== POTATO =====
stages_data['crops']['Potato'] = {
    "name_te": "బంగాళాదుంప",
    "total_duration_days": 100,
    "seasons": ["Rabi"],
    "water_requirement_mm": 500,
    "stages": [
        {"id": 1, "name": "Planting", "name_te": "నాటడం", "start_day": 0, "end_day": 15,
         "critical_activities": [
            {"task": "Plant cut seed tubers", "priority": "high", "day": 1}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 2, "name": "Vegetative", "name_te": "శాకాహార", "start_day": 16, "end_day": 40,
         "critical_activities": [
            {"task": "First earthing up", "priority": "high", "day": 25}
         ],
         "pest_focus": ["Aphids"], "disease_focus": ["Early blight"]},
        {"id": 3, "name": "Tuber Initiation", "name_te": "దుంప ప్రారంభం", "start_day": 41, "end_day": 60,
         "critical_activities": [
            {"task": "Second earthing up", "priority": "high", "day": 45}
         ],
         "pest_focus": [], "disease_focus": ["Late blight"]},
        {"id": 4, "name": "Tuber Bulking", "name_te": "దుంప పెరుగుదల", "start_day": 61, "end_day": 85,
         "critical_activities": [
            {"task": "Critical irrigation", "priority": "critical", "day": 70}
         ],
         "pest_focus": [], "disease_focus": []},
        {"id": 5, "name": "Maturity", "name_te": "పరిపక్వత", "start_day": 86, "end_day": 100,
         "critical_activities": [
            {"task": "Cut haulms 10 days before harvest", "priority": "medium", "day": 90}
         ],
         "pest_focus": [], "disease_focus": []}
    ]
}

faqs_data['crops']['Potato'] = {"faqs": [
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Water-soaked lesions on leaves spreading rapidly",
     "question_te": "ఆకులపై నీటితో నానిన గాయాలు వేగంగా వ్యాపిస్తున్నాయి",
     "answer_en": "Late Blight (Phytophthora infestans) - can destroy crop in days.",
     "answer_te": "లేట్ బ్లైట్ - రోజుల్లో పంటను నాశనం చేయగలదు.",
     "action_en": "Spray Mancozeb + Metalaxyl MZ 72 WP @ 2g/L immediately. Repeat every 7 days.",
     "action_te": "వెంటనే మాంకోజెబ్ + మెటలాక్సిల్ పిచికారీ. ప్రతి 7 రోజులకు మళ్ళీ."},
]}

# Update totals and save
stages_data['generated'] = datetime.now().isoformat()
total_stages = sum(len(c.get('stages', [])) for c in stages_data['crops'].values())

with open(stages_path, 'w', encoding='utf-8') as f:
    json.dump(stages_data, f, indent=2, ensure_ascii=False)

total_faqs = sum(len(c.get('faqs', [])) for c in faqs_data['crops'].values())
faqs_data['total_faqs'] = total_faqs

with open(faqs_path, 'w', encoding='utf-8') as f:
    json.dump(faqs_data, f, indent=2, ensure_ascii=False)

print(f"✅ Expanded to {len(stages_data['crops'])} crops")
print(f"   Total stages: {total_stages}")
print(f"   Total FAQs: {total_faqs}")
print("\nCrops covered:")
for crop in stages_data['crops']:
    stages = len(stages_data['crops'][crop].get('stages', []))
    faqs = len(faqs_data['crops'].get(crop, {}).get('faqs', []))
    print(f"   {crop}: {stages} stages, {faqs} FAQs")
