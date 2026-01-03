"""
Script to ensure every crop has at least 20 FAQs
"""
import json
import os

FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'crop_faqs_complete.json')

# Common farming FAQ templates that can be applied to any crop
FAQ_TEMPLATES = [
    {
        "question_en": "What is the best time to sow {crop}?",
        "question_te": "{crop_te} విత్తడానికి ఉత్తమ సమయం ఏమిటి?",
        "answer_en": "The best sowing time depends on your region and season. Generally, {crop} is sown during {season} season when temperatures are optimal.",
        "answer_te": "{crop_te}ను సాధారణంగా {season_te} సీజన్‌లో విత్తుతారు, ఉష్ణోగ్రతలు అనుకూలంగా ఉన్నప్పుడు.",
        "category": "sowing"
    },
    {
        "question_en": "How much water does {crop} need?",
        "question_te": "{crop_te}కు ఎంత నీరు అవసరం?",
        "answer_en": "{crop} requires regular irrigation. Water requirements vary by growth stage - more during flowering and fruiting stages.",
        "answer_te": "{crop_te}కు క్రమం తప్పకుండా నీరు పెట్టాలి. పూత మరియు కాయలు కాసే దశలో ఎక్కువ నీరు అవసరం.",
        "category": "irrigation"
    },
    {
        "question_en": "What fertilizers are recommended for {crop}?",
        "question_te": "{crop_te}కు ఏ ఎరువులు సిఫార్సు చేయబడతాయి?",
        "answer_en": "Apply NPK fertilizers as per soil test recommendations. Basal dose at sowing and top dressing during vegetative growth.",
        "answer_te": "మట్టి పరీక్ష ఆధారంగా NPK ఎరువులు వేయండి. విత్తనేటప్పుడు మూల మోతాదు, పెరుగుదల దశలో పైపెట్టు వేయండి.",
        "category": "fertilizer"
    },
    {
        "question_en": "What are common pests affecting {crop}?",
        "question_te": "{crop_te}ను ప్రభావితం చేసే సాధారణ పురుగులు ఏమిటి?",
        "answer_en": "Common pests include stem borers, leaf hoppers, and aphids. Regular scouting and timely intervention is key.",
        "answer_te": "సాధారణ పురుగులలో కాండం తొలుచు పురుగులు, ఆకు దున్నలు మరియు ఆఫిడ్స్ ఉన్నాయి. క్రమం తప్పకుండా పరిశీలించండి.",
        "category": "pest"
    },
    {
        "question_en": "What diseases commonly affect {crop}?",
        "question_te": "{crop_te}ను సాధారణంగా ప్రభావితం చేసే వ్యాధులు ఏమిటి?",
        "answer_en": "Common diseases include fungal infections like blight and wilt. Maintain proper spacing and drainage.",
        "answer_te": "సాధారణ వ్యాధులలో బ్లైట్, విల్ట్ వంటి ఫంగల్ ఇన్‌ఫెక్షన్లు ఉన్నాయి. సరైన దూరం మరియు డ్రైనేజీ ఉంచండి.",
        "category": "disease"
    },
    {
        "question_en": "How to identify nutrient deficiency in {crop}?",
        "question_te": "{crop_te}లో పోషక లోపాన్ని ఎలా గుర్తించాలి?",
        "answer_en": "Yellow leaves indicate nitrogen deficiency, purple leaves indicate phosphorus deficiency, brown leaf edges indicate potassium deficiency.",
        "answer_te": "పసుపు ఆకులు నత్రజని లోపం, ఊదా ఆకులు భాస్వరం లోపం, గోధుమ ఆకు అంచులు పొటాషియం లోపం సూచిస్తాయి.",
        "category": "nutrient"
    },
    {
        "question_en": "When is the right time to harvest {crop}?",
        "question_te": "{crop_te} కోయడానికి సరైన సమయం ఎప్పుడు?",
        "answer_en": "Harvest when the crop reaches physiological maturity. Look for signs like color change and moisture content.",
        "answer_te": "పంట శారీరక పరిపక్వత చేరినప్పుడు కోయండి. రంగు మార్పు మరియు తేమ శాతం గమనించండి.",
        "category": "harvest"
    },
    {
        "question_en": "How to store {crop} after harvest?",
        "question_te": "{crop_te}ను కోత తర్వాత ఎలా నిల్వ చేయాలి?",
        "answer_en": "Dry to optimal moisture content (12-14%). Store in clean, dry, well-ventilated place. Protect from pests and moisture.",
        "answer_te": "సరైన తేమ శాతానికి (12-14%) ఆరబెట్టండి. శుభ్రమైన, పొడి, గాలి ప్రసరించే చోట నిల్వ చేయండి.",
        "category": "storage"
    },
    {
        "question_en": "What is the expected yield of {crop} per acre?",
        "question_te": "{crop_te}కు ఎకరాకు ఊహించిన దిగుబడి ఎంత?",
        "answer_en": "Yield varies by variety and management. With good practices, you can expect good returns.",
        "answer_te": "రకం మరియు నిర్వహణపై ఆధారపడి దిగుబడి మారుతుంది. మంచి పద్ధతులతో మంచి రాబడి పొందవచ్చు.",
        "category": "yield"
    },
    {
        "question_en": "What is the seed rate for {crop}?",
        "question_te": "{crop_te}కు విత్తన రేటు ఎంత?",
        "answer_en": "Seed rate depends on variety and sowing method. Follow recommended rates for your region.",
        "answer_te": "విత్తన రేటు రకం మరియు విత్తే పద్ధతిపై ఆధారపడి ఉంటుంది. మీ ప్రాంతానికి సిఫార్సు చేసిన రేట్లు అనుసరించండి.",
        "category": "sowing"
    },
    {
        "question_en": "How to control weeds in {crop}?",
        "question_te": "{crop_te}లో కలుపు మొక్కలను ఎలా నియంత్రించాలి?",
        "answer_en": "Use pre-emergence and post-emergence herbicides. Manual weeding 20-25 days after sowing is also effective.",
        "answer_te": "ప్రీ-ఎమర్జెన్స్ మరియు పోస్ట్-ఎమర్జెన్స్ హెర్బిసైడ్‌లు వాడండి. విత్తిన 20-25 రోజుల తర్వాత చేతితో కలుపు తీయడం కూడా ప్రభావవంతం.",
        "category": "weed"
    },
    {
        "question_en": "What is the spacing recommended for {crop}?",
        "question_te": "{crop_te}కు సిఫార్సు చేసిన దూరం ఎంత?",
        "answer_en": "Proper spacing ensures good aeration and reduces disease. Follow variety-specific recommendations.",
        "answer_te": "సరైన దూరం మంచి గాలి ప్రసరణ నిర్ధారిస్తుంది మరియు వ్యాధులను తగ్గిస్తుంది. రకం-నిర్దిష్ట సిఫార్సులు అనుసరించండి.",
        "category": "sowing"
    },
    {
        "question_en": "How to prepare land for {crop}?",
        "question_te": "{crop_te} కోసం భూమిని ఎలా సిద్ధం చేయాలి?",
        "answer_en": "Plow 2-3 times, add organic matter, level the field, and ensure proper drainage before sowing.",
        "answer_te": "2-3 సార్లు దున్నండి, సేంద్రియ పదార్థం కలపండి, పొలం సమం చేయండి, విత్తే ముందు సరైన డ్రైనేజీ నిర్ధారించండి.",
        "category": "land_prep"
    },
    {
        "question_en": "What is seed treatment for {crop}?",
        "question_te": "{crop_te}కు విత్తన శుద్ధి ఏమిటి?",
        "answer_en": "Treat seeds with fungicides (Thiram/Carbendazim) and biofertilizers before sowing to protect from soil-borne diseases.",
        "answer_te": "విత్తే ముందు విత్తనాలను ఫంగిసైడ్‌లు (థైరామ్/కార్బెండాజిమ్) మరియు బయోఫెర్టిలైజర్‌లతో శుద్ధి చేయండి.",
        "category": "sowing"
    },
    {
        "question_en": "How to manage {crop} during drought?",
        "question_te": "{crop_te}ను కరువు సమయంలో ఎలా నిర్వహించాలి?",
        "answer_en": "Apply mulching, reduce nitrogen application, irrigate at critical stages, and use drought-tolerant varieties.",
        "answer_te": "మల్చింగ్ వేయండి, నత్రజని తగ్గించండి, క్లిష్టమైన దశల్లో నీరు పెట్టండి, కరువు-నిరోధక రకాలు వాడండి.",
        "category": "stress"
    },
    {
        "question_en": "How to protect {crop} from heavy rain?",
        "question_te": "{crop_te}ను భారీ వర్షం నుండి ఎలా రక్షించాలి?",
        "answer_en": "Ensure proper drainage, stake plants if needed, apply fungicides after rain to prevent diseases.",
        "answer_te": "సరైన డ్రైనేజీ నిర్ధారించండి, అవసరమైతే మొక్కలకు గొంగళి వేయండి, వ్యాధులు నివారించడానికి వర్షం తర్వాత ఫంగిసైడ్‌లు పిచికారీ చేయండి.",
        "category": "stress"
    },
    {
        "question_en": "What are the government subsidies for {crop}?",
        "question_te": "{crop_te}కు ప్రభుత్వ సబ్సిడీలు ఏమిటి?",
        "answer_en": "Check with local agriculture office for input subsidies, crop insurance (PMFBY), and MSP announcements.",
        "answer_te": "ఇన్‌పుట్ సబ్సిడీలు, పంట బీమా (PMFBY), MSP ప్రకటనల కోసం స్థానిక వ్యవసాయ కార్యాలయాన్ని సంప్రదించండి.",
        "category": "scheme"
    },
    {
        "question_en": "What is the MSP for {crop}?",
        "question_te": "{crop_te}కు MSP ఎంత?",
        "answer_en": "MSP is announced by government annually. Check the latest rates from official sources or local mandi.",
        "answer_te": "MSP ప్రభుత్వం వార్షికంగా ప్రకటిస్తుంది. అధికారిక వనరుల నుండి లేదా స్థానిక మండి నుండి తాజా ధరలు చెక్ చేయండి.",
        "category": "market"
    },
    {
        "question_en": "How to improve soil health for {crop}?",
        "question_te": "{crop_te} కోసం మట్టి ఆరోగ్యాన్ని ఎలా మెరుగుపరచాలి?",
        "answer_en": "Add organic matter, practice crop rotation, use green manures, and get regular soil testing done.",
        "answer_te": "సేంద్రియ పదార్థం కలపండి, పంట భ్రమణం పాటించండి, హరిత ఎరువులు వాడండి, క్రమం తప్పకుండా మట్టి పరీక్ష చేయించండి.",
        "category": "soil"
    },
    {
        "question_en": "What is intercropping suitable with {crop}?",
        "question_te": "{crop_te}తో అంతర పంటలు ఏమిటి?",
        "answer_en": "Legumes like pulses can be intercropped to improve nitrogen fixation and income diversification.",
        "answer_te": "పప్పుధాన్యాలు వంటి తృణధాన్యాలను అంతర పంటలుగా పండించవచ్చు, ఇది నత్రజని బంధనం మరియు ఆదాయ వైవిధ్యాన్ని మెరుగుపరుస్తుంది.",
        "category": "cropping"
    },
    {
        "question_en": "How to identify quality seeds for {crop}?",
        "question_te": "{crop_te}కు నాణ్యమైన విత్తనాలను ఎలా గుర్తించాలి?",
        "answer_en": "Buy certified seeds from authorized dealers. Check germination rate, purity, and seed health certificate.",
        "answer_te": "అధీకృత డీలర్ల నుండి ధృవీకృత విత్తనాలు కొనండి. మొలకెత్తే రేటు, స్వచ్ఛత మరియు విత్తన ఆరోగ్య ధృవపత్రం తనిఖీ చేయండి.",
        "category": "seed"
    },
    {
        "question_en": "What organic methods work for {crop}?",
        "question_te": "{crop_te}కు ఏ సేంద్రియ పద్ధతులు పని చేస్తాయి?",
        "answer_en": "Use vermicompost, neem-based pesticides, biofertilizers, and practice integrated pest management.",
        "answer_te": "వర్మీకంపోస్ట్, వేప ఆధారిత పురుగుమందులు, బయోఫెర్టిలైజర్‌లు వాడండి, సమీకృత పురుగుల నిర్వహణ పాటించండి.",
        "category": "organic"
    }
]

# Telugu crop names
CROP_NAMES_TE = {
    "Paddy": "వరి", "Rice": "వరి", "Maize": "మొక్కజొన్న", "Cotton": "పత్తి",
    "Sugarcane": "చెరకు", "Groundnut": "వేరుశెనగ", "Ground Nuts": "వేరుశెనగ",
    "Chilli": "మిరప", "Wheat": "గోధుమ", "Turmeric": "పసుపు",
    "Pulses": "పప్పులు", "Millets": "చిరుధాన్యాలు", "Tomato": "టమాటో",
    "Onion": "ఉల్లిపాయ", "Banana": "అరటి", "Soybean": "సోయాబీన్",
    "Bengal Gram": "శెనగలు", "Brinjal": "వంకాయ", "Okra": "బెండకాయ",
    "Potato": "ఆలుగడ్డ", "Barley": "బార్లీ", "Oil Seeds": "నూనెగింజలు",
    "Tobacco": "పొగాకు", "Cabbage": "క్యాబేజీ", "Cauliflower": "కాలీఫ్లవర్",
    "Carrot": "క్యారెట్", "Mango": "మామిడి", "Papaya": "బొప్పాయి",
    "Guava": "జామ"
}

SEASON_NAMES = {
    "Paddy": ("Kharif", "ఖరీఫ్"), "Rice": ("Kharif", "ఖరీఫ్"),
    "Maize": ("Kharif/Rabi", "ఖరీఫ్/రబీ"), "Cotton": ("Kharif", "ఖరీఫ్"),
    "Wheat": ("Rabi", "రబీ"), "Groundnut": ("Kharif", "ఖరీఫ్"),
    "Chilli": ("Kharif/Rabi", "ఖరీఫ్/రబీ"), "Sugarcane": ("Year-round", "సంవత్సరం పొడవునా"),
}

def expand_faqs():
    # Load existing FAQs
    with open(FAQ_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    crops = data.get('crops', {})
    
    print("Current FAQ counts:")
    for crop in sorted(crops.keys()):
        faqs = crops[crop].get('faqs', [])
        print(f"  {crop}: {len(faqs)}")
    
    # Add FAQs to crops with less than 20
    updated = False
    for crop in crops.keys():
        faqs = crops[crop].get('faqs', [])
        if len(faqs) < 20:
            needed = 20 - len(faqs)
            print(f"\nAdding {needed} FAQs to {crop}...")
            
            crop_te = CROP_NAMES_TE.get(crop, crop)
            season = SEASON_NAMES.get(crop, ("Kharif/Rabi", "ఖరీఫ్/రబీ"))
            
            # Check which templates are already used (by category)
            existing_categories = {faq.get('category', '') for faq in faqs}
            
            added = 0
            for template in FAQ_TEMPLATES:
                if added >= needed:
                    break
                    
                # Skip if similar category already exists
                if template['category'] in existing_categories and added > 5:
                    continue
                
                new_faq = {
                    "question_en": template['question_en'].format(crop=crop),
                    "question_te": template['question_te'].format(crop_te=crop_te),
                    "answer_en": template['answer_en'].format(crop=crop, season=season[0]),
                    "answer_te": template['answer_te'].format(crop_te=crop_te, season_te=season[1]),
                    "category": template['category'],
                    "stage": ["all"]
                }
                faqs.append(new_faq)
                added += 1
            
            crops[crop]['faqs'] = faqs
            updated = True
            print(f"  Now {crop} has {len(faqs)} FAQs")
    
    if updated:
        # Save back
        with open(FAQ_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\n✅ FAQs expanded and saved!")
    else:
        print("\n✅ All crops already have 20+ FAQs!")
    
    # Final count
    print("\nFinal FAQ counts:")
    for crop in sorted(crops.keys()):
        faqs = crops[crop].get('faqs', [])
        status = "✅" if len(faqs) >= 20 else "❌"
        print(f"  {status} {crop}: {len(faqs)}")

if __name__ == "__main__":
    expand_faqs()
