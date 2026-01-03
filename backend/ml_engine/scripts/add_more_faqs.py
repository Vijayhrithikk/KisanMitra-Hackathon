"""
Add additional FAQs for the new crops to improve coverage
"""
import json

faqs_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_faqs_complete.json"
with open(faqs_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Additional FAQs for each new crop
EXTRA_FAQS = {
    "Wheat": [
        {"stage": "sowing", "category": "water", "urgency": "critical",
         "question_en": "Best time for first irrigation in wheat?",
         "question_te": "గోధుమలో మొదటి నీటికి ఉత్తమ సమయం?",
         "answer_en": "Crown Root Initiation (CRI) stage at 20-25 DAS. Most critical irrigation.",
         "answer_te": "CRI దశ 20-25 రోజులలో. అత్యంత క్లిష్టమైన నీటిపారుదల.",
         "action_en": "Don't delay CRI irrigation. Yield loss of 25-30% if missed.",
         "action_te": "CRI నీటిపారుదల ఆలస్యం చేయకండి. తప్పితే 25-30% దిగుబడి నష్టం."},
    ],
    "Sugarcane": [
        {"stage": "planting", "category": "pest", "urgency": "high",
         "question_en": "Setts not germinating, eaten by insects",
         "question_te": "సెట్స్ మొలకెత్తడం లేదు, పురుగులు తిన్నాయి",
         "answer_en": "Termite damage. Common in dry soils with trash.",
         "answer_te": "చెదలు నష్టం. చెత్తగల పొడి మట్టిలో సాధారణం.",
         "action_en": "Treat soil with Chlorpyriphos 20 EC @ 5L/ha before planting.",
         "action_te": "నాటడానికి ముందు క్లోర్పైరిఫాస్‌తో మట్టి శుద్ధి."},
    ],
    "Tomato": [
        {"stage": "flowering", "category": "fertilizer", "urgency": "medium",
         "question_en": "Flowers dropping without setting fruit",
         "question_te": "కాయ కట్టకుండా పూలు రాలిపోతున్నాయి",
         "answer_en": "Poor pollination due to high temperature or nutrient deficiency.",
         "answer_te": "అధిక ఉష్ణోగ్రత లేదా పోషకాల లోపం వల్ల పేలవమైన పరాగసంపర్కం.",
         "action_en": "Spray NAA 20ppm + Boron 0.2%. Irrigate in evening.",
         "action_te": "NAA + బోరాన్ పిచికారీ. సాయంత్రం నీరు పెట్టండి."},
    ],
    "Onion": [
        {"stage": "storage", "category": "storage", "urgency": "high",
         "question_en": "Onions rotting in storage",
         "question_te": "నిల్వలో ఉల్లిపాయలు కుళ్ళిపోతున్నాయి",
         "answer_en": "Poor curing or storage in humid conditions.",
         "answer_te": "సరిగ్గా ఆరబెట్టలేదు లేదా తేమగల పరిస్థితులలో నిల్వ.",
         "action_en": "Cure for 7-10 days in shade. Store in ventilated structure.",
         "action_te": "నీడలో 7-10 రోజులు ఆరబెట్టండి. గాలి వచ్చే నిర్మాణంలో నిల్వ."},
    ],
    "Banana": [
        {"stage": "bunch", "category": "pest", "urgency": "medium",
         "question_en": "Black spots on fingers, skin cracking",
         "question_te": "వేళ్లపై నల్లని మచ్చలు, చర్మం పగుళ్లు",
         "answer_en": "Scarring Beetle damage. Cosmetic issue but affects marketability.",
         "answer_te": "స్కారింగ్ బీటిల్ నష్టం. కాస్మెటిక్ సమస్య కానీ మార్కెటబిలిటీని ప్రభావితం చేస్తుంది.",
         "action_en": "Use bunch covers. Spray Carbaryl 50 WP @ 2g/L on exposed bunches.",
         "action_te": "గెల కవర్లు వాడండి. కార్బరిల్ పిచికారీ."},
    ],
    "Soybean": [
        {"stage": "flowering", "category": "disease", "urgency": "high",
         "question_en": "Orange pustules on undersides of leaves",
         "question_te": "ఆకుల దిగువ ఉపరితలంపై నారింజ బొబ్బలు",
         "answer_en": "Asian Soybean Rust. Serious in high humidity.",
         "answer_te": "ఏషియన్ సోయాబీన్ రస్ట్. అధిక తేమలో తీవ్రం.",
         "action_en": "Spray Propiconazole 25 EC @ 1ml/L. Repeat after 15 days.",
         "action_te": "ప్రొపికొనాజోల్ పిచికారీ. 15 రోజుల తర్వాత మళ్ళీ."},
    ],
    "Turmeric": [
        {"stage": "rhizome", "category": "disease", "urgency": "critical",
         "question_en": "Rhizomes rotting with foul smell",
         "question_te": "దుర్వాసనతో దుంపలు కుళ్ళిపోతున్నాయి",
         "answer_en": "Rhizome Rot (Pythium). Serious in waterlogged conditions.",
         "answer_te": "రైజోమ్ రాట్. నీరు నిలిచిన పరిస్థితులలో తీవ్రం.",
         "action_en": "Improve drainage. Drench with Copper oxychloride 3g/L.",
         "action_te": "డ్రైనేజ్ మెరుగుపరచండి. కాపర్ ఆక్సీక్లోరైడ్ డ్రెంచ్."},
    ],
    "Bengal Gram": [
        {"stage": "flowering", "category": "water", "urgency": "high",
         "question_en": "Should I irrigate chickpea?",
         "question_te": "శెనగలకు నీరు పెట్టాలా?",
         "answer_en": "Only if soil moisture is critically low. Chickpea is sensitive to overwatering.",
         "answer_te": "మట్టి తేమ తీవ్రంగా తక్కువగా ఉంటేనే. శెనగలు అధిక నీటికి సున్నితం.",
         "action_en": "Light irrigation at flowering if needed. Never waterlog.",
         "action_te": "అవసరమైతే పూతలో తేలికపాటి నీరు. ఎప్పుడూ నీరు నిలవకూడదు."},
    ],
    "Brinjal": [
        {"stage": "fruiting", "category": "fertilizer", "urgency": "medium",
         "question_en": "Fruits are small and bitter",
         "question_te": "కాయలు చిన్నగా మరియు చేదుగా ఉన్నాయి",
         "answer_en": "Water stress or harvesting too late.",
         "answer_te": "నీటి ఒత్తిడి లేదా చాలా ఆలస్యంగా కోయడం.",
         "action_en": "Regular irrigation. Harvest at right maturity stage.",
         "action_te": "క్రమబద్ధమైన నీటిపారుదల. సరైన పరిపక్వ దశలో కోయండి."},
    ],
    "Okra": [
        {"stage": "fruiting", "category": "pest", "urgency": "high",
         "question_en": "Fruits with bore holes and caterpillars inside",
         "question_te": "కాయలలో రంధ్రాలు, లోపల పురుగులు",
         "answer_en": "Shoot and Fruit Borer - common pest in okra.",
         "answer_te": "షూట్ మరియు ఫ్రూట్ బోరర్ - బెండలో సాధారణ పురుగు.",
         "action_en": "Spray Emamectin benzoate 5 SG @ 0.4g/L. Remove affected fruits.",
         "action_te": "ఎమామెక్టిన్ బెంజోయేట్ పిచికారీ. నష్టపడిన కాయలు తీసివేయండి."},
    ],
    "Potato": [
        {"stage": "tuber", "category": "fertilizer", "urgency": "medium",
         "question_en": "Tubers have green patches",
         "question_te": "దుంపలపై పచ్చని మచ్చలు ఉన్నాయి",
         "answer_en": "Greening due to sunlight exposure - contains solanine (toxic).",
         "answer_te": "సూర్యరశ్మి బహిర్గతం వల్ల పచ్చబడటం - సోలానిన్ (విషం) కలిగి ఉంటుంది.",
         "action_en": "Do proper earthing up. Store in dark place. Don't eat green potatoes.",
         "action_te": "సరిగ్గా మట్టి వేయండి. చీకటి ప్రదేశంలో నిల్వ చేయండి. పచ్చని బంగాళాదుంపలు తినకండి."},
    ]
}

# Add extra FAQs
for crop, faqs in EXTRA_FAQS.items():
    if crop in data['crops']:
        data['crops'][crop]['faqs'].extend(faqs)

# Update total
total_faqs = sum(len(c.get('faqs', [])) for c in data['crops'].values())
data['total_faqs'] = total_faqs

with open(faqs_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Total FAQs now: {total_faqs}")
for crop in data['crops']:
    print(f"   {crop}: {len(data['crops'][crop]['faqs'])} FAQs")
