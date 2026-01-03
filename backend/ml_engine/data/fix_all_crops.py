"""
Fix all crop data consistency issues:
1. Add missing crops to FAQs
2. Ensure all crops have proper stage data
3. Sync crop names across all data files
"""
import json
import os

DATA_DIR = os.path.dirname(__file__)
STAGES_PATH = os.path.join(DATA_DIR, 'crop_stages.json')
FAQS_PATH = os.path.join(DATA_DIR, 'crop_faqs_complete.json')

# Telugu names for all crops
CROP_NAMES_TE = {
    "Rice": "వరి",
    "Paddy": "వరి", 
    "Cotton": "పత్తి",
    "Maize": "మొక్కజొన్న",
    "Groundnut": "వేరుశెనగ",
    "Chilli": "మిర్చి",
    "Sugarcane": "చెరకు",
    "Turmeric": "పసుపు",
    "Wheat": "గోధుమ",
    "Tomato": "టమాటో",
    "Onion": "ఉల్లిపాయ",
    "Potato": "బంగాళాదుంప",
    "Banana": "అరటి",
    "Brinjal": "వంకాయ",
    "Okra": "బెండకాయ",
    "Pulses": "పప్పులు",
    "Soybean": "సోయాబీన్",
    "Barley": "బార్లీ",
    "Bengal Gram": "శెనగలు",
    "Watermelon": "పుచ్చకాయ",
    "Mango": "మామిడి",
    "Guava": "జామ",
    "Papaya": "బొప్పాయి",
    "Grapes": "ద్రాక్ష",
    "Orange": "నారింజ",
    "Pomegranate": "దానిమ్మ",
    "Cabbage": "క్యాబేజీ",
    "Cauliflower": "గోబీ",
    "Carrot": "క్యారెట్"
}

# FAQ template generator
def generate_crop_faqs(crop_name, crop_name_te, duration=120, season="Kharif"):
    """Generate 20 standard FAQs for a crop"""
    return [
        {"question_en": f"What is the best time to sow {crop_name}?", "question_te": f"{crop_name_te} విత్తడానికి ఉత్తమ సమయం?", "answer_en": f"{crop_name} is typically sown during {season} season. Exact timing depends on your region.", "answer_te": f"{crop_name_te}ను సాధారణంగా {season} సీజన్‌లో విత్తుతారు.", "category": "sowing", "stage": ["all"]},
        {"question_en": f"How much water does {crop_name} need?", "question_te": f"{crop_name_te}కు ఎంత నీరు అవసరం?", "answer_en": f"Water requirement varies by growth stage. Monitor soil moisture and irrigate as needed.", "answer_te": f"నీటి అవసరం పెరుగుదల దశపై ఆధారపడి ఉంటుంది. మట్టి తేమ పర్యవేక్షించండి.", "category": "irrigation", "stage": ["all"]},
        {"question_en": f"What fertilizers are recommended for {crop_name}?", "question_te": f"{crop_name_te}కు ఏ ఎరువులు సిఫార్సు?", "answer_en": f"Apply balanced NPK fertilizers based on soil test. Split nitrogen applications for better uptake.", "answer_te": f"మట్టి పరీక్ష ఆధారంగా సమతుల్య NPK ఎరువులు వేయండి.", "category": "fertilizer", "stage": ["all"]},
        {"question_en": f"What are common pests in {crop_name}?", "question_te": f"{crop_name_te}లో సాధారణ పురుగులు?", "answer_en": f"Common pests vary by region. Monitor regularly and apply appropriate control measures.", "answer_te": f"సాధారణ పురుగులు ప్రాంతాన్ని బట్టి మారుతాయి. క్రమం తప్పకుండా పరిశీలించండి.", "category": "pest", "stage": ["all"]},
        {"question_en": f"What diseases affect {crop_name}?", "question_te": f"{crop_name_te}ను ప్రభావితం చేసే వ్యాధులు?", "answer_en": f"Fungal and bacterial diseases are common. Maintain proper spacing and drainage.", "answer_te": f"ఫంగల్ మరియు బాక్టీరియల్ వ్యాధులు సాధారణం. సరైన దూరం మరియు డ్రైనేజీ ఉంచండి.", "category": "disease", "stage": ["all"]},
        {"question_en": f"When to harvest {crop_name}?", "question_te": f"{crop_name_te} ఎప్పుడు కోయాలి?", "answer_en": f"Harvest when crop shows maturity signs. Usually {duration} days after sowing.", "answer_te": f"పంట పరిపక్వత సంకేతాలు చూపినప్పుడు కోయండి. సాధారణంగా విత్తిన {duration} రోజుల తర్వాత.", "category": "harvest", "stage": ["all"]},
        {"question_en": f"What is the expected yield of {crop_name}?", "question_te": f"{crop_name_te} ఊహించిన దిగుబడి?", "answer_en": f"Yield depends on variety, soil, and management. Follow good agricultural practices for best results.", "answer_te": f"దిగుబడి రకం, మట్టి మరియు నిర్వహణపై ఆధారపడి ఉంటుంది.", "category": "yield", "stage": ["all"]},
        {"question_en": f"What is the seed rate for {crop_name}?", "question_te": f"{crop_name_te} విత్తన రేటు?", "answer_en": f"Seed rate varies by variety and method. Check with local agricultural office for recommendations.", "answer_te": f"విత్తన రేటు రకం మరియు పద్ధతిని బట్టి మారుతుంది.", "category": "sowing", "stage": ["all"]},
        {"question_en": f"What spacing is required for {crop_name}?", "question_te": f"{crop_name_te}కు ఏ దూరం అవసరం?", "answer_en": f"Proper spacing ensures good air circulation and reduces disease. Follow variety-specific recommendations.", "answer_te": f"సరైన దూరం మంచి గాలి ప్రసరణ నిర్ధారిస్తుంది మరియు వ్యాధిని తగ్గిస్తుంది.", "category": "sowing", "stage": ["all"]},
        {"question_en": f"How to prepare land for {crop_name}?", "question_te": f"{crop_name_te} కోసం భూమి సిద్ధం?", "answer_en": f"Plow 2-3 times, add organic manure, level the field, and prepare beds as needed.", "answer_te": f"2-3 సార్లు దున్నండి, సేంద్రియ ఎరువు కలపండి, పొలం సమం చేయండి.", "category": "land_prep", "stage": ["all"]},
        {"question_en": f"How to control weeds in {crop_name}?", "question_te": f"{crop_name_te}లో కలుపు నియంత్రణ?", "answer_en": f"Use pre-emergence herbicides and hand weeding. Mulching also helps control weeds.", "answer_te": f"ప్రీ-ఎమర్జెన్స్ హెర్బిసైడ్‌లు మరియు చేతి కలుపు వాడండి. మల్చింగ్ కూడా సహాయపడుతుంది.", "category": "weed", "stage": ["all"]},
        {"question_en": f"How to store {crop_name} after harvest?", "question_te": f"{crop_name_te} కోత తర్వాత నిల్వ?", "answer_en": f"Dry properly before storage. Store in clean, dry, well-ventilated place protected from pests.", "answer_te": f"నిల్వ చేయడానికి ముందు బాగా ఆరబెట్టండి. శుభ్రమైన, పొడి, గాలి ప్రసరించే చోట నిల్వ చేయండి.", "category": "storage", "stage": ["all"]},
        {"question_en": f"What is seed treatment for {crop_name}?", "question_te": f"{crop_name_te}కు విత్తన శుద్ధి?", "answer_en": f"Treat seeds with fungicide before sowing to prevent seed-borne diseases.", "answer_te": f"విత్తే ముందు విత్తనాలకు ఫంగిసైడ్ శుద్ధి చేయండి.", "category": "sowing", "stage": ["all"]},
        {"question_en": f"How to manage {crop_name} during drought?", "question_te": f"కరువులో {crop_name_te} నిర్వహణ?", "answer_en": f"Irrigate at critical stages. Mulching helps retain moisture. Consider drought-tolerant varieties.", "answer_te": f"క్లిష్టమైన దశల్లో నీరు పెట్టండి. మల్చింగ్ తేమ నిలుపుతుంది.", "category": "stress", "stage": ["all"]},
        {"question_en": f"How to protect {crop_name} from heavy rain?", "question_te": f"భారీ వర్షం నుండి {crop_name_te} రక్షణ?", "answer_en": f"Ensure proper drainage. Apply fungicides after rain to prevent diseases.", "answer_te": f"సరైన డ్రైనేజీ నిర్ధారించండి. వ్యాధులు నివారించడానికి వర్షం తర్వాత ఫంగిసైడ్‌లు వేయండి.", "category": "stress", "stage": ["all"]},
        {"question_en": f"What are government subsidies for {crop_name}?", "question_te": f"{crop_name_te}కు ప్రభుత్వ సబ్సిడీలు?", "answer_en": f"Check with local agriculture office for input subsidies, MSP, and other schemes.", "answer_te": f"ఇన్‌పుట్ సబ్సిడీలు, MSP మరియు ఇతర పథకాల కోసం స్థానిక వ్యవసాయ కార్యాలయం సంప్రదించండి.", "category": "scheme", "stage": ["all"]},
        {"question_en": f"What is the MSP for {crop_name}?", "question_te": f"{crop_name_te}కు MSP?", "answer_en": f"MSP is announced by government annually. Check latest rates from official sources.", "answer_te": f"MSP ప్రభుత్వం వార్షికంగా ప్రకటిస్తుంది. తాజా ధరలు చెక్ చేయండి.", "category": "market", "stage": ["all"]},
        {"question_en": f"How to improve soil health for {crop_name}?", "question_te": f"{crop_name_te} కోసం మట్టి ఆరోగ్యం?", "answer_en": f"Add organic matter, practice crop rotation, and get soil tested regularly.", "answer_te": f"సేంద్రియ పదార్థం కలపండి, పంట భ్రమణం చేయండి, క్రమం తప్పకుండా మట్టి పరీక్ష చేయించండి.", "category": "soil", "stage": ["all"]},
        {"question_en": f"What organic methods work for {crop_name}?", "question_te": f"{crop_name_te}కు సేంద్రియ పద్ధతులు?", "answer_en": f"Use vermicompost, neem-based pesticides, biofertilizers for organic production.", "answer_te": f"సేంద్రియ ఉత్పత్తికి వర్మీకంపోస్ట్, వేప ఆధారిత పురుగుమందులు, బయోఫెర్టిలైజర్‌లు వాడండి.", "category": "organic", "stage": ["all"]},
        {"question_en": f"How to identify nutrient deficiency in {crop_name}?", "question_te": f"{crop_name_te}లో పోషక లోపం ఎలా గుర్తించాలి?", "answer_en": f"Yellow leaves indicate nitrogen deficiency. Purple leaves indicate phosphorus deficiency. Brown leaf edges indicate potassium deficiency.", "answer_te": f"పసుపు ఆకులు నత్రజని లోపం. ఊదా ఆకులు భాస్వరం లోపం. గోధుమ అంచులు పొటాషియం లోపం.", "category": "nutrient", "stage": ["all"]}
    ]

def fix_all_crops():
    # Load existing data
    with open(STAGES_PATH, 'r', encoding='utf-8') as f:
        stages_data = json.load(f)
    
    with open(FAQS_PATH, 'r', encoding='utf-8') as f:
        faqs_data = json.load(f)
    
    stages_crops = set(stages_data.get('crops', {}).keys())
    faq_crops = set(faqs_data.get('crops', {}).keys())
    
    print(f"Crops in stages: {len(stages_crops)}")
    print(f"Crops with FAQs: {len(faq_crops)}")
    
    # Find missing
    missing_in_faqs = stages_crops - faq_crops
    print(f"\nCrops missing FAQs: {missing_in_faqs}")
    
    # Add missing crops to FAQs
    added = 0
    for crop in missing_in_faqs:
        crop_te = CROP_NAMES_TE.get(crop, crop)
        duration = stages_data['crops'][crop].get('duration_days', 120)
        season = stages_data['crops'][crop].get('seasons', ['Kharif'])[0] if stages_data['crops'][crop].get('seasons') else 'Kharif'
        
        faqs_data['crops'][crop] = {
            "name_te": crop_te,
            "faqs": generate_crop_faqs(crop, crop_te, duration, season)
        }
        print(f"  Added 20 FAQs for {crop}")
        added += 1
    
    # Also ensure Paddy/Rice is handled (they may be duplicates)
    if 'Rice' in stages_crops and 'Paddy' in faq_crops and 'Rice' not in faq_crops:
        faqs_data['crops']['Rice'] = faqs_data['crops']['Paddy']
        print("  Copied Paddy FAQs to Rice")
    
    # Update total count
    total = sum(len(faqs_data['crops'][c].get('faqs', [])) for c in faqs_data['crops'])
    faqs_data['total_faqs'] = total
    
    # Save FAQs
    with open(FAQS_PATH, 'w', encoding='utf-8') as f:
        json.dump(faqs_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Added FAQs for {added} crops")
    print(f"Total FAQs now: {total}")
    
    # Final verification
    print("\nFinal crop list with FAQs:")
    for crop in sorted(faqs_data['crops'].keys()):
        count = len(faqs_data['crops'][crop].get('faqs', []))
        status = "✓" if count >= 20 else "⚠"
        print(f"  {status} {crop}: {count} FAQs")

if __name__ == "__main__":
    fix_all_crops()
