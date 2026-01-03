"""
Add missing crops (Soybean, Barley, etc.) to FAQ file
"""
import json
import os

FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'crop_faqs_complete.json')

# Missing crops to add with their FAQs
MISSING_CROPS = {
    "Soybean": {
        "name_te": "సోయాబీన్",
        "faqs": [
            {"question_en": "What is the best time to sow Soybean?", "question_te": "సోయాబీన్ విత్తడానికి ఉత్తమ సమయం ఏమిటి?", "answer_en": "Sow during June-July with onset of monsoon. Seed rate 30-35 kg/acre.", "answer_te": "వర్షాకాలం ప్రారంభంతో జూన్-జూలైలో విత్తండి. విత్తన రేటు 30-35 కిలో/ఎకరం.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How much water does Soybean need?", "question_te": "సోయాబీన్‌కు ఎంత నీరు అవసరం?", "answer_en": "Soybean is mainly rainfed. Critical irrigation needed during flowering and pod filling if rain fails.", "answer_te": "సోయాబీన్ ప్రధానంగా వర్షాధారం. వర్షం లేకపోతే పూత మరియు కాయ నింపే దశలో క్లిష్టమైన నీరు.", "category": "irrigation", "stage": ["all"]},
            {"question_en": "What fertilizers are recommended for Soybean?", "question_te": "సోయాబీన్‌కు ఏ ఎరువులు సిఫార్సు?", "answer_en": "Apply 20 kg N + 60 kg P2O5 per hectare. Rhizobium seed treatment recommended.", "answer_te": "హెక్టారుకు 20 కిలో N + 60 కిలో P2O5 వేయండి. రైజోబియం విత్తన శుద్ధి సిఫార్సు.", "category": "fertilizer", "stage": ["all"]},
            {"question_en": "What are common pests affecting Soybean?", "question_te": "సోయాబీన్‌ను ప్రభావితం చేసే పురుగులు?", "answer_en": "Girdle beetle, stem fly, and pod borer are major pests. Scout regularly.", "answer_te": "గర్డిల్ బీటిల్, స్టెమ్ ఫ్లై, పాడ్ బోరర్ ప్రధాన పురుగులు. క్రమం తప్పకుండా పరిశీలించండి.", "category": "pest", "stage": ["all"]},
            {"question_en": "What diseases commonly affect Soybean?", "question_te": "సోయాబీన్‌ను ప్రభావితం చేసే వ్యాధులు?", "answer_en": "Rust, anthracnose, and bacterial pustule. Maintain proper spacing and drainage.", "answer_te": "రస్ట్, ఆంత్రాక్నోస్, బాక్టీరియల్ పస్ట్యూల్. సరైన దూరం మరియు డ్రైనేజీ ఉంచండి.", "category": "disease", "stage": ["all"]},
            {"question_en": "How to identify nutrient deficiency in Soybean?", "question_te": "సోయాబీన్‌లో పోషక లోపం ఎలా గుర్తించాలి?", "answer_en": "Yellow leaves indicate nitrogen deficiency. Purple leaves indicate phosphorus deficiency.", "answer_te": "పసుపు ఆకులు నత్రజని లోపం. ఊదా ఆకులు భాస్వరం లోపం సూచిస్తాయి.", "category": "nutrient", "stage": ["all"]},
            {"question_en": "When is the right time to harvest Soybean?", "question_te": "సోయాబీన్ కోయడానికి సరైన సమయం?", "answer_en": "Harvest when 95% pods turn brown and leaves shed. Usually 90-100 days after sowing.", "answer_te": "95% కాయలు గోధుమ రంగుకు మారి ఆకులు రాలినప్పుడు కోయండి. విత్తిన 90-100 రోజుల తర్వాత.", "category": "harvest", "stage": ["all"]},
            {"question_en": "How to store Soybean after harvest?", "question_te": "సోయాబీన్ కోత తర్వాత ఎలా నిల్వ చేయాలి?", "answer_en": "Dry to 10% moisture. Store in clean, dry, well-ventilated place.", "answer_te": "10% తేమకు ఆరబెట్టండి. శుభ్రమైన, పొడి, గాలి ప్రసరించే చోట నిల్వ చేయండి.", "category": "storage", "stage": ["all"]},
            {"question_en": "What is the expected yield of Soybean per acre?", "question_te": "సోయాబీన్‌కు ఎకరాకు ఊహించిన దిగుబడి?", "answer_en": "With good practices, expect 8-10 quintals per acre.", "answer_te": "మంచి పద్ధతులతో ఎకరాకు 8-10 క్వింటాళ్లు ఊహించవచ్చు.", "category": "yield", "stage": ["all"]},
            {"question_en": "What is the seed rate for Soybean?", "question_te": "సోయాబీన్‌కు విత్తన రేటు?", "answer_en": "Seed rate is 30-35 kg/acre for most varieties.", "answer_te": "చాలా రకాలకు ఎకరాకు 30-35 కిలో విత్తన రేటు.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to control weeds in Soybean?", "question_te": "సోయాబీన్‌లో కలుపు నియంత్రణ?", "answer_en": "Use pre-emergence herbicide Pendimethalin 30EC @ 3.3L/ha. Hand weeding at 30 DAS.", "answer_te": "ప్రీ-ఎమర్జెన్స్ హెర్బిసైడ్ పెండిమెథాలిన్ వాడండి. 30 రోజులకు చేతి కలుపు.", "category": "weed", "stage": ["all"]},
            {"question_en": "What is the spacing recommended for Soybean?", "question_te": "సోయాబీన్‌కు సిఫార్సు చేసిన దూరం?", "answer_en": "Row to row 30-45 cm, plant to plant 5-7 cm.", "answer_te": "వరుసకు వరుస 30-45 సెం.మీ, మొక్కకు మొక్క 5-7 సెం.మీ.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to prepare land for Soybean?", "question_te": "సోయాబీన్ కోసం భూమి సిద్ధం?", "answer_en": "Plow 2-3 times, add FYM 5 tonnes/ha, make BBF (broad bed and furrow).", "answer_te": "2-3 సార్లు దున్నండి, FYM 5 టన్నులు/హెక్టారు కలపండి, BBF తయారు చేయండి.", "category": "land_prep", "stage": ["all"]},
            {"question_en": "What is seed treatment for Soybean?", "question_te": "సోయాబీన్‌కు విత్తన శుద్ధి?", "answer_en": "Treat with Thiram 3g/kg + Rhizobium culture before sowing.", "answer_te": "విత్తే ముందు థైరామ్ 3గ్రా/కిలో + రైజోబియం కల్చర్‌తో శుద్ధి చేయండి.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to manage Soybean during drought?", "question_te": "కరువులో సోయాబీన్ నిర్వహణ?", "answer_en": "Irrigate at flower and pod filling stage. Mulching helps retain moisture.", "answer_te": "పూత మరియు కాయ నింపే దశలో నీరు పెట్టండి. మల్చింగ్ తేమ నిలుపుతుంది.", "category": "stress", "stage": ["all"]},
            {"question_en": "How to protect Soybean from heavy rain?", "question_te": "భారీ వర్షం నుండి సోయాబీన్ రక్షణ?", "answer_en": "Ensure proper drainage. Apply fungicides after rain to prevent diseases.", "answer_te": "సరైన డ్రైనేజీ నిర్ధారించండి. వ్యాధులు నివారించడానికి వర్షం తర్వాత ఫంగిసైడ్‌లు వేయండి.", "category": "stress", "stage": ["all"]},
            {"question_en": "What are the government subsidies for Soybean?", "question_te": "సోయాబీన్‌కు ప్రభుత్వ సబ్సిడీలు?", "answer_en": "Check with local agriculture office for input subsidies and MSP.", "answer_te": "ఇన్‌పుట్ సబ్సిడీలు మరియు MSP కోసం స్థానిక వ్యవసాయ కార్యాలయం సంప్రదించండి.", "category": "scheme", "stage": ["all"]},
            {"question_en": "What is the MSP for Soybean?", "question_te": "సోయాబీన్‌కు MSP?", "answer_en": "MSP is announced by government annually. Check latest rates.", "answer_te": "MSP ప్రభుత్వం వార్షికంగా ప్రకటిస్తుంది. తాజా ధరలు చెక్ చేయండి.", "category": "market", "stage": ["all"]},
            {"question_en": "How to improve soil health for Soybean?", "question_te": "సోయాబీన్ కోసం మట్టి ఆరోగ్యం మెరుగుపరచడం?", "answer_en": "Soybean being legume fixes nitrogen. Rotate with cereals.", "answer_te": "సోయాబీన్ పప్పుధాన్యం కాబట్టి నత్రజని బంధిస్తుంది. ధాన్యాలతో భ్రమణం చేయండి.", "category": "soil", "stage": ["all"]},
            {"question_en": "What organic methods work for Soybean?", "question_te": "సోయాబీన్‌కు సేంద్రియ పద్ధతులు?", "answer_en": "Use vermicompost, neem-based pesticides, biofertilizers like Rhizobium.", "answer_te": "వర్మీకంపోస్ట్, వేప ఆధారిత పురుగుమందులు, రైజోబియం వంటి బయోఫెర్టిలైజర్‌లు వాడండి.", "category": "organic", "stage": ["all"]}
        ]
    },
    "Barley": {
        "name_te": "బార్లీ",
        "faqs": [
            {"question_en": "What is the best time to sow Barley?", "question_te": "బార్లీ విత్తడానికి ఉత్తమ సమయం?", "answer_en": "Sow during Rabi season (October-November). Seed rate 40-50 kg/acre.", "answer_te": "రబీ సీజన్‌లో (అక్టోబర్-నవంబర్) విత్తండి. విత్తన రేటు 40-50 కిలో/ఎకరం.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How much water does Barley need?", "question_te": "బార్లీకు ఎంత నీరు అవసరం?", "answer_en": "2-3 irrigations sufficient. First at tillering (25-30 DAS), second at heading.", "answer_te": "2-3 నీరు సరిపోతుంది. మొదటిది పిల్లలు పట్టేటప్పుడు, రెండవది కంకి.", "category": "irrigation", "stage": ["all"]},
            {"question_en": "What fertilizers are recommended for Barley?", "question_te": "బార్లీకు ఏ ఎరువులు సిఫార్సు?", "answer_en": "Apply 40 kg N + 20 kg P2O5 per acre. Half N at sowing, half at tillering.", "answer_te": "ఎకరాకు 40 కిలో N + 20 కిలో P2O5. సగం N విత్తేటప్పుడు, సగం పిల్లలు పట్టేటప్పుడు.", "category": "fertilizer", "stage": ["all"]},
            {"question_en": "What are common pests affecting Barley?", "question_te": "బార్లీని ప్రభావితం చేసే పురుగులు?", "answer_en": "Aphids and termites are common. Monitor regularly.", "answer_te": "ఆఫిడ్స్ మరియు చెదపురుగులు సాధారణం. క్రమం తప్పకుండా పరిశీలించండి.", "category": "pest", "stage": ["all"]},
            {"question_en": "What diseases commonly affect Barley?", "question_te": "బార్లీని ప్రభావితం చేసే వ్యాధులు?", "answer_en": "Yellow rust, stripe rust, and powdery mildew are common.", "answer_te": "యెల్లో రస్ట్, స్ట్రైప్ రస్ట్, పౌడరీ మిల్డ్యూ సాధారణం.", "category": "disease", "stage": ["all"]},
            {"question_en": "How to control yellow rust in Barley?", "question_te": "బార్లీలో యెల్లో రస్ట్ నియంత్రణ?", "answer_en": "Spray Propiconazole 25 EC @ 1ml/L when symptoms appear.", "answer_te": "లక్షణాలు కనిపించినప్పుడు ప్రోపికొనాజోల్ పిచికారీ చేయండి.", "category": "disease", "stage": ["all"]},
            {"question_en": "When is the right time to harvest Barley?", "question_te": "బార్లీ కోయడానికి సరైన సమయం?", "answer_en": "Harvest when grains are hard and straw is golden. Usually 120-130 days after sowing.", "answer_te": "గింజలు గట్టిగా మరియు గడ్డి బంగారు రంగు అయినప్పుడు కోయండి. 120-130 రోజులు.", "category": "harvest", "stage": ["all"]},
            {"question_en": "How to store Barley after harvest?", "question_te": "బార్లీ కోత తర్వాత నిల్వ?", "answer_en": "Dry to 12% moisture. Store in clean, dry place protected from pests.", "answer_te": "12% తేమకు ఆరబెట్టండి. పురుగుల నుండి రక్షణతో శుభ్రమైన, పొడి చోట నిల్వ చేయండి.", "category": "storage", "stage": ["all"]},
            {"question_en": "What is the expected yield of Barley per acre?", "question_te": "బార్లీకు ఎకరాకు ఊహించిన దిగుబడి?", "answer_en": "With good practices, expect 15-20 quintals per acre.", "answer_te": "మంచి పద్ధతులతో ఎకరాకు 15-20 క్వింటాళ్లు.", "category": "yield", "stage": ["all"]},
            {"question_en": "What is the seed rate for Barley?", "question_te": "బార్లీకు విత్తన రేటు?", "answer_en": "Seed rate is 40-50 kg/acre.", "answer_te": "విత్తన రేటు ఎకరాకు 40-50 కిలో.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to control weeds in Barley?", "question_te": "బార్లీలో కలుపు నియంత్రణ?", "answer_en": "Apply Isoproturon 50 WP @ 1.5 kg/ha as pre-emergence.", "answer_te": "ప్రీ-ఎమర్జెన్స్‌గా ఐసోప్రోట్యూరాన్ 1.5 కిలో/హెక్టారు వేయండి.", "category": "weed", "stage": ["all"]},
            {"question_en": "What is the spacing recommended for Barley?", "question_te": "బార్లీకు సిఫార్సు చేసిన దూరం?", "answer_en": "Row to row 22.5 cm for line sowing.", "answer_te": "లైన్ సోవింగ్‌కు వరుసకు వరుస 22.5 సెం.మీ.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to prepare land for Barley?", "question_te": "బార్లీ కోసం భూమి సిద్ధం?", "answer_en": "Plow 2-3 times, level the field, apply basal fertilizers.", "answer_te": "2-3 సార్లు దున్నండి, పొలం సమం చేయండి, మూల ఎరువులు వేయండి.", "category": "land_prep", "stage": ["all"]},
            {"question_en": "What is seed treatment for Barley?", "question_te": "బార్లీకు విత్తన శుద్ధి?", "answer_en": "Treat with Thiram/Carbendazim 2g/kg seed before sowing.", "answer_te": "విత్తే ముందు థైరామ్/కార్బెండజిమ్ 2గ్రా/కిలో విత్తనంతో శుద్ధి చేయండి.", "category": "sowing", "stage": ["all"]},
            {"question_en": "How to manage Barley during drought?", "question_te": "కరువులో బార్లీ నిర్వహణ?", "answer_en": "Irrigate at critical stages - tillering and heading.", "answer_te": "క్లిష్టమైన దశల్లో నీరు పెట్టండి - పిల్లలు పట్టడం మరియు కంకి.", "category": "stress", "stage": ["all"]},
            {"question_en": "How to protect Barley from frost?", "question_te": "మంచు నుండి బార్లీ రక్షణ?", "answer_en": "Light irrigation before frost. Avoid late sowing.", "answer_te": "మంచుకు ముందు తేలికపాటి నీరు. ఆలస్యంగా విత్తడం నివారించండి.", "category": "stress", "stage": ["all"]},
            {"question_en": "What are varieties of Barley for malt production?", "question_te": "మాల్ట్ ఉత్పత్తికి బార్లీ రకాలు?", "answer_en": "DWRUB 52, RD 2660, RD 2668 are good malt varieties.", "answer_te": "DWRUB 52, RD 2660, RD 2668 మంచి మాల్ట్ రకాలు.", "category": "variety", "stage": ["all"]},
            {"question_en": "What is the MSP for Barley?", "question_te": "బార్లీకు MSP?", "answer_en": "MSP is announced by government annually. Check latest rates.", "answer_te": "MSP ప్రభుత్వం వార్షికంగా ప్రకటిస్తుంది. తాజా ధరలు చెక్ చేయండి.", "category": "market", "stage": ["all"]},
            {"question_en": "What organic methods work for Barley?", "question_te": "బార్లీకు సేంద్రియ పద్ధతులు?", "answer_en": "Use FYM, vermicompost, neem-based pesticides for organic production.", "answer_te": "సేంద్రియ ఉత్పత్తికి FYM, వర్మీకంపోస్ట్, వేప ఆధారిత పురుగుమందులు వాడండి.", "category": "organic", "stage": ["all"]},
            {"question_en": "How to improve soil health for Barley?", "question_te": "బార్లీ కోసం మట్టి ఆరోగ్యం?", "answer_en": "Rotate with legumes, add organic matter, get soil tested.", "answer_te": "పప్పుధాన్యాలతో భ్రమణం, సేంద్రియ పదార్థం కలపండి, మట్టి పరీక్ష చేయించండి.", "category": "soil", "stage": ["all"]}
        ]
    }
}

def add_missing_crops():
    # Load existing FAQs
    with open(FAQ_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    crops = data.get('crops', {})
    
    print("Current crops:", list(crops.keys()))
    
    # Add missing crops
    added = []
    for crop, crop_data in MISSING_CROPS.items():
        if crop not in crops:
            crops[crop] = crop_data
            added.append(crop)
            print(f"Added {crop} with {len(crop_data['faqs'])} FAQs")
        else:
            print(f"{crop} already exists with {len(crops[crop].get('faqs', []))} FAQs")
    
    if added:
        # Update total count
        total = sum(len(crops[c].get('faqs', [])) for c in crops)
        data['total_faqs'] = total
        
        # Save back
        with open(FAQ_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Added {len(added)} crops: {', '.join(added)}")
        print(f"Total FAQs now: {total}")
    else:
        print("\n✅ All crops already exist!")
    
    # Final count
    print("\nFinal crop list:")
    for crop in sorted(crops.keys()):
        faqs = crops[crop].get('faqs', [])
        print(f"  {crop}: {len(faqs)} FAQs")

if __name__ == "__main__":
    add_missing_crops()
