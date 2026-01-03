"""
Expand FAQs and Pest/Disease entries for Maize and Groundnut
Target: Add 50+ more FAQs and pest entries
"""
import json

# Load existing FAQs
faq_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_faqs_complete.json"
with open(faq_path, 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

# Additional FAQs for underrepresented crops
MAIZE_EXTRA = [
    {"stage": "vegetative", "category": "fertilizer", "urgency": "high",
     "question_en": "When to apply urea in maize for best results?",
     "question_te": "మొక్కజొన్నలో మంచి ఫలితాల కోసం యూరియా ఎప్పుడు వేయాలి?",
     "answer_en": "Apply in 3 splits: 1/3 at sowing, 1/3 at knee-high (25-30 DAS), 1/3 at tasseling (45-50 DAS).",
     "answer_te": "3 భాగాలుగా వేయండి: 1/3 విత్తేటప్పుడు, 1/3 మోకాలు ఎత్తులో, 1/3 తురాయి దశలో.",
     "action_en": "Total 50-60 kg Urea/acre in splits. Apply in moist soil.",
     "action_te": "మొత్తం 50-60 కిలో యూరియా/ఎకరం భాగాలుగా. తడి మట్టిలో వేయండి."},
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Small brown larvae eating tassel before emergence",
     "question_te": "చిన్న గోధుమ పురుగులు తురాయి రాక ముందే తింటున్నాయి",
     "answer_en": "Ear Worm (Corn Earworm) - Helicoverpa zea. Also attacks developing ears.",
     "answer_te": "ఇయర్ వార్మ్ - హెలికోవెర్పా జియా. అభివృద్ధి చెందుతున్న కంకులపై కూడా దాడి చేస్తుంది.",
     "action_en": "Spray Spinosad 45 SC @ 0.3ml/L. Apply in evening for best results.",
     "action_te": "స్పినోసాడ్ సాయంత్రం పిచికారీ చేయండి."},
    {"stage": "emergence", "category": "disease", "urgency": "medium",
     "question_en": "Seeds not germinating, white fungal growth on seeds",
     "question_te": "విత్తనాలు మొలకెత్తడం లేదు, విత్తనాలపై తెల్లని బూజు పెరుగుదల",
     "answer_en": "Seed rot and seedling blight caused by Pythium/Fusarium. Common in cold, wet soils.",
     "answer_te": "సీడ్ రాట్ మరియు సీడ్లింగ్ బ్లైట్. చల్లని, తడి మట్టిలో సాధారణం.",
     "action_en": "Treat seeds with Thiram + Carbendazim @ 3g/kg before sowing.",
     "action_te": "విత్తడానికి ముందు విత్తనాలను థైరామ్ + కార్బెండజిమ్‌తో శుద్ధి చేయండి."},
    {"stage": "silking", "category": "water", "urgency": "critical",
     "question_en": "Silks came out but dried quickly, poor pollination expected",
     "question_te": "పట్టు వచ్చింది కానీ త్వరగా ఎండిపోయింది, పేలవమైన పరాగసంపర్కం",
     "answer_en": "Drought stress during critical pollination period. Irreversible damage possible.",
     "answer_te": "క్లిష్టమైన పరాగసంపర్క కాలంలో కరువు ఒత్తిడి. తిరిగి పొందలేని నష్టం సాధ్యం.",
     "action_en": "Irrigate immediately. Even partial recovery can save 20-30% yield.",
     "action_te": "వెంటనే నీరు పెట్టండి. పాక్షిక రికవరీ కూడా 20-30% దిగుబడి రక్షించగలదు."},
    {"stage": "kernel", "category": "disease", "urgency": "high",
     "question_en": "Ears rotting with pink/red mold",
     "question_te": "కంకులు పింక్/ఎరుపు బూజుతో కుళ్ళిపోతున్నాయి",
     "answer_en": "Fusarium Ear Rot. Common after insect damage or wet weather.",
     "answer_te": "ఫ్యూసారియం ఇయర్ రాట్. పురుగు నష్టం లేదా తడి వాతావరణం తర్వాత సాధారణం.",
     "action_en": "Remove and destroy affected ears. Avoid feeding to livestock (toxins).",
     "action_te": "నష్టపడిన కంకులు తీసివేయండి. పశువులకు మేత వేయకండి (టాక్సిన్లు)."},
    {"stage": "vegetative", "category": "weed", "urgency": "high",
     "question_en": "Best herbicide for maize without damaging crop?",
     "question_te": "పంటను పాడు చేయకుండా మొక్కజొన్నకు మంచి కలుపు మందు?",
     "answer_en": "Atrazine is selective for maize. Apply pre-emergence or early post-emergence.",
     "answer_te": "అట్రాజిన్ మొక్కజొన్నకు సెలెక్టివ్. ప్రీ-ఎమర్జెన్స్ లేదా ఎర్లీ పోస్ట్-ఎమర్జెన్స్ వేయండి.",
     "action_en": "Spray Atrazine 50 WP @ 0.5 kg/acre + Pendimethalin 30 EC @ 1L/acre pre-emergence.",
     "action_te": "ప్రీ-ఎమర్జెన్స్‌లో అట్రాజిన్ + పెండిమెథాలిన్ పిచికారీ."},
]

GROUNDNUT_EXTRA = [
    {"stage": "pod", "category": "disease", "urgency": "critical",
     "question_en": "Pods have dark spots and are rotting in soil",
     "question_te": "కాయలపై నల్లని మచ్చలు, మట్టిలో కుళ్ళిపోతున్నాయి",
     "answer_en": "Pod Rot (Collar Rot) - Aspergillus niger. Produces aflatoxin - dangerous!",
     "answer_te": "పాడ్ రాట్ (కాలర్ రాట్). అఫ్లాటాక్సిన్ ఉత్పత్తి చేస్తుంది - ప్రమాదకరం!",
     "action_en": "Remove and destroy infected plants. Apply Trichoderma to soil. Don't use affected pods for seed.",
     "action_te": "సోకిన మొక్కలు తీసివేయండి. మట్టికి ట్రైకోడర్మా వేయండి. నష్టపడిన కాయలను విత్తనంగా వాడకండి."},
    {"stage": "pegging", "category": "pest", "urgency": "high",
     "question_en": "White grubs eating roots and pods underground",
     "question_te": "తెల్ల పురుగులు వేర్లు మరియు కాయలు మట్టిలో తింటున్నాయి",
     "answer_en": "White Grub (Holotrichia) larvae. Serious soil pest in groundnut.",
     "answer_te": "వైట్ గ్రబ్ లార్వా. వేరుశెనగలో తీవ్రమైన మట్టి పురుగు.",
     "action_en": "Apply Chlorpyriphos 20 EC @ 2.5L/ha in irrigation water. Or Phorate 10G @ 10 kg/ha.",
     "action_te": "నీటిలో క్లోర్పైరిఫాస్ వేయండి. లేదా ఫోరేట్ గ్రాన్యూల్స్."},
    {"stage": "flowering", "category": "pest", "urgency": "high",
     "question_en": "Caterpillars cutting leaves and making webbing",
     "question_te": "పురుగులు ఆకులు కత్తిరించి జాలం చేస్తున్నాయి",
     "answer_en": "Red Hairy Caterpillar or Tobacco Caterpillar. Night feeders.",
     "answer_te": "రెడ్ హెయిరీ క్యాటర్‌పిల్లర్ లేదా టొబాకో క్యాటర్‌పిల్లర్. రాత్రి తినేవి.",
     "action_en": "Hand pick caterpillars. Spray Quinalphos 25 EC @ 2ml/L in evening.",
     "action_te": "పురుగులను చేతితో ఏరండి. సాయంత్రం క్వినాల్ఫాస్ పిచికారీ."},
    {"stage": "vegetative", "category": "fertilizer", "urgency": "medium",
     "question_en": "Do groundnuts need nitrogen fertilizer?",
     "question_te": "వేరుశెనగలకు నత్రజని ఎరువు అవసరమా?",
     "answer_en": "Minimal - groundnuts fix nitrogen through Rhizobium. Mainly need P, K, and Calcium (gypsum).",
     "answer_te": "కనిష్టం - వేరుశెనగలు రైజోబియం ద్వారా నత్రజని స్థిరపరుస్తాయి. ప్రధానంగా P, K, మరియు కాల్షియం అవసరం.",
     "action_en": "Apply SSP 100 kg + Gypsum 200 kg per acre. Rhizobium seed treatment is essential.",
     "action_te": "SSP 100 కిలో + జిప్సమ్ 200 కిలో/ఎకరం వేయండి. రైజోబియం విత్తన శుద్ధి అవసరం."},
    {"stage": "maturity", "category": "harvest", "urgency": "high",
     "question_en": "How to check if groundnut is ready for harvest?",
     "question_te": "వేరుశెనగ కోతకు సిద్ధంగా ఉందో ఎలా తనిఖీ చేయాలి?",
     "answer_en": "70% pods should have dark inner shell. Check by opening few pods - kernels should fill shell.",
     "answer_te": "70% కాయలకు లోపలి షెల్ నల్లగా ఉండాలి. కొన్ని కాయలు తెరిచి చూడండి - గింజలు షెల్ నిండాలి.",
     "action_en": "Irrigate lightly 2 days before harvest for easy uprooting. Harvest in morning.",
     "action_te": "సులభంగా పెకలించడానికి కోతకు 2 రోజుల ముందు తేలికపాటి నీరు. ఉదయం కోయండి."},
    {"stage": "post_harvest", "category": "storage", "urgency": "critical",
     "question_en": "How to prevent aflatoxin during storage?",
     "question_te": "నిల్వ సమయంలో అఫ్లాటాక్సిన్ ఎలా నివారించాలి?",
     "answer_en": "Aflatoxin is deadly toxin produced by Aspergillus. Proper drying is CRITICAL.",
     "answer_te": "అఫ్లాటాక్సిన్ ఆస్పెర్‌జిల్లస్ ఉత్పత్తి చేసే ప్రాణాంతక టాక్సిన్. సరైన ఆరబెట్టడం అత్యంత ముఖ్యం.",
     "action_en": "Dry pods to <8% moisture. Store in dry place. Check regularly for mold. Discard moldy pods.",
     "action_te": "కాయలను <8% తేమకు ఆరబెట్టండి. పొడి ప్రదేశంలో నిల్వ చేయండి. మసి కాయలు పారేయండి."},
]

CHILLI_EXTRA = [
    {"stage": "flowering", "category": "fertilizer", "urgency": "high",
     "question_en": "Flowers dropping without setting fruit",
     "question_te": "పూలు కాయ కట్టకుండా రాలిపోతున్నాయి",
     "answer_en": "Flower drop due to high temperature, nutrient deficiency (Boron), or water stress.",
     "answer_te": "అధిక ఉష్ణోగ్రత, పోషకాల లోపం (బోరాన్), లేదా నీటి ఒత్తిడి వల్ల పూలు రాలడం.",
     "action_en": "Spray Boron 0.2% (Borax 2g/L) + NAA 20ppm. Irrigate in evening to reduce temperature.",
     "action_te": "బోరాన్ 0.2% + NAA పిచికారీ. ఉష్ణోగ్రత తగ్గించడానికి సాయంత్రం నీరు పెట్టండి."},
    {"stage": "nursery", "category": "disease", "urgency": "high",
     "question_en": "Seedlings falling over with rotted base",
     "question_te": "నారు మొక్కలు కుళ్ళిన మొదలుతో పడిపోతున్నాయి",
     "answer_en": "Damping Off disease caused by Pythium/Rhizoctonia. Common in overwatered nurseries.",
     "answer_te": "డాంపింగ్ ఆఫ్ వ్యాధి. అధికంగా నీరు పెట్టిన నారుమడులలో సాధారణం.",
     "action_en": "Reduce watering. Drench with Copper oxychloride 3g/L or Carbendazim 1g/L.",
     "action_te": "నీరు తగ్గించండి. కాపర్ ఆక్సీక్లోరైడ్ లేదా కార్బెండజిమ్‌తో డ్రెంచ్."},
    {"stage": "fruiting", "category": "pest", "urgency": "high",
     "question_en": "Small white flying insects on undersides of leaves",
     "question_te": "ఆకుల దిగువ చిన్న తెల్లని ఎగిరే పురుగులు",
     "answer_en": "Whitefly (Bemisia tabaci). Vector for Leaf Curl Virus - very serious!",
     "answer_te": "వైట్‌ఫ్లై. లీఫ్ కర్ల్ వైరస్ వాహకం - చాలా తీవ్రం!",
     "action_en": "Spray Diafenthiuron 50 WP @ 1g/L or Spiromesifen 22.9 SC @ 0.5ml/L. Repeat every 10 days.",
     "action_te": "డయాఫెంథియురాన్ లేదా స్పైరోమెసిఫెన్ పిచికారీ. ప్రతి 10 రోజులకు మళ్ళీ."},
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Plants suddenly wilting and dying even with water",
     "question_te": "నీరు ఉన్నా మొక్కలు హఠాత్తుగా వాడి చనిపోతున్నాయి",
     "answer_en": "Bacterial Wilt (Ralstonia solanacearum). Vascular disease - no cure.",
     "answer_te": "బాక్టీరియల్ విల్ట్. వాస్కులర్ వ్యాధి - చికిత్స లేదు.",
     "action_en": "Remove and burn infected plants. Don't plant solanaceous crops for 2-3 years. Use raised beds.",
     "action_te": "సోకిన మొక్కలు తీసి కాల్చండి. 2-3 సంవత్సరాలు సోలనేసియస్ పంటలు వేయకండి."},
]

COTTON_EXTRA = [
    {"stage": "squaring", "category": "fertilizer", "urgency": "high",
     "question_en": "When to apply potash in cotton?",
     "question_te": "పత్తిలో పొటాష్ ఎప్పుడు వేయాలి?",
     "answer_en": "Apply at squaring (35-40 DAS) for better square retention and boll development.",
     "answer_te": "మెరుగైన చదరం నిలుపుదల మరియు కాయ అభివృద్ధి కోసం చదరాల సమయంలో వేయండి.",
     "action_en": "Apply MOP 25 kg/acre at squaring. Foliar spray 1% KCl if deficiency seen.",
     "action_te": "చదరాల సమయంలో MOP 25 కిలో/ఎకరం వేయండి. లోపం కనిపిస్తే 1% KCl పిచికారీ."},
    {"stage": "flowering", "category": "disease", "urgency": "high",
     "question_en": "Reddening of leaves with premature leaf drop",
     "question_te": "ఆకులు ఎర్రబడటం, అకాలంగా ఆకు రాలడం",
     "answer_en": "Red Leaf disease - caused by nutrient imbalance or magnesium deficiency.",
     "answer_te": "రెడ్ లీఫ్ వ్యాధి - పోషకాల అసమతుల్యత లేదా మెగ్నీషియం లోపం వల్ల.",
     "action_en": "Spray Magnesium sulphate 1% + Urea 2% foliar. Check for root health.",
     "action_te": "మెగ్నీషియం సల్ఫేట్ 1% + యూరియా 2% ఆకులపై పిచికారీ. వేర్ల ఆరోగ్యం తనిఖీ చేయండి."},
    {"stage": "boll", "category": "pest", "urgency": "high",
     "question_en": "Bolls not opening, stuck together",
     "question_te": "కాయలు పగలడం లేదు, అతుక్కుపోయి ఉన్నాయి",
     "answer_en": "Boll Rot or Stained Cotton due to continuous wet weather. Lint quality affected.",
     "answer_te": "నిరంతర తడి వాతావరణం వల్ల కాయ కుళ్ళు లేదా మచ్చల పత్తి. నార నాణ్యత ప్రభావితం.",
     "action_en": "Wait for dry weather. Pick affected bolls separately. Don't mix with good cotton.",
     "action_te": "పొడి వాతావరణం కోసం వేచి ఉండండి. నష్టపడిన కాయలు విడిగా ఏరండి. మంచి పత్తితో కలపకండి."},
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Leaves with white cottony mass on veins",
     "question_te": "ఈనెలపై తెల్లని పత్తి వంటి పదార్థంతో ఆకులు",
     "answer_en": "Mealybug infestation. Serious late-season pest.",
     "answer_te": "మీలీబగ్ దాడి. సీజన్ చివరలో తీవ్రమైన పురుగు.",
     "action_en": "Release Cryptolaemus beetle (biological). Or spray Profenophos 50 EC @ 2ml/L + Neem oil.",
     "action_te": "క్రిప్టోలేమస్ బీటిల్ వదలండి (జీవసంబంధ). లేదా ప్రొఫెనోఫాస్ + వేప నూనె పిచికారీ."},
]

PADDY_EXTRA2 = [
    {"stage": "nursery", "category": "water", "urgency": "high",
     "question_en": "How much water to keep in nursery?",
     "question_te": "నారుమడిలో ఎంత నీరు ఉంచాలి?",
     "answer_en": "Keep saturated initially, then thin layer 2-3 cm after germination.",
     "answer_te": "మొదట సంతృప్తంగా ఉంచండి, మొలకెత్తిన తర్వాత 2-3 సెం.మీ పలుచని పొర.",
     "action_en": "Drain if water exceeds 5 cm. Excess water causes weak seedlings.",
     "action_te": "నీరు 5 సెం.మీ మించితే తీసివేయండి. అధిక నీరు బలహీన నారు మొక్కలకు కారణమవుతుంది."},
    {"stage": "transplanting", "category": "spacing", "urgency": "medium",
     "question_en": "What is the ideal spacing for paddy?",
     "question_te": "వరికి ఆదర్శ దూరం ఏమిటి?",
     "answer_en": "20x15 cm or 20x20 cm for most varieties. Closer for short duration, wider for long duration.",
     "answer_te": "చాలా రకాలకు 20x15 సెం.మీ లేదా 20x20 సెం.మీ. స్వల్పకాలికానికి దగ్గరగా, దీర్ఘకాలికానికి విస్తృతంగా.",
     "action_en": "Use marker or rope for uniform spacing. 2-3 seedlings per hill.",
     "action_te": "ఏకరీతి దూరం కోసం మార్కర్ లేదా తాడు వాడండి. ప్రతి గుట్టకు 2-3 నారు మొక్కలు."},
    {"stage": "tillering", "category": "pest", "urgency": "medium",
     "question_en": "Small hoppers jumping when plants are disturbed",
     "question_te": "మొక్కలను కదిలించినప్పుడు చిన్న హాపర్లు గెంతుతున్నాయి",
     "answer_en": "Green Leafhopper (GLH) or White-backed Planthopper. Both vectors for virus diseases.",
     "answer_te": "గ్రీన్ లీఫ్‌హాపర్ లేదా వైట్-బ్యాక్డ్ ప్లాంట్‌హాపర్. రెండూ వైరస్ వ్యాధుల వాహకాలు.",
     "action_en": "Spray Thiamethoxam 25 WG @ 0.5g/L if population exceeds 2/hill.",
     "action_te": "జనాభా 2/గుట్ట మించితే థియామెథాక్సామ్ పిచికారీ."},
    {"stage": "grain_fill", "category": "pest", "urgency": "medium",
     "question_en": "Grains partially filled with empty portions",
     "question_te": "గింజలు పాక్షికంగా నిండి ఖాళీ భాగాలతో ఉన్నాయి",
     "answer_en": "Could be Rice Bug feeding or chaffy grains due to heat/drought stress during flowering.",
     "answer_te": "రైస్ బగ్ తినడం లేదా పూత సమయంలో వేడి/కరువు ఒత్తిడి వల్ల ఊక గింజలు.",
     "action_en": "If bugs still present, spray Malathion in evening. Nothing can be done for stress damage.",
     "action_te": "పురుగులు ఇంకా ఉంటే సాయంత్రం మాలాథియాన్ పిచికారీ. ఒత్తిడి నష్టానికి ఏమీ చేయలేరు."},
]

# Merge all new FAQs
faq_data['crops']['Maize']['faqs'].extend(MAIZE_EXTRA)
faq_data['crops']['Groundnut']['faqs'].extend(GROUNDNUT_EXTRA)
faq_data['crops']['Chilli']['faqs'].extend(CHILLI_EXTRA)
faq_data['crops']['Cotton']['faqs'].extend(COTTON_EXTRA)
faq_data['crops']['Paddy']['faqs'].extend(PADDY_EXTRA2)

# Update total count
total = sum(len(c["faqs"]) for c in faq_data["crops"].values())
faq_data["total_faqs"] = total

# Save updated FAQs
with open(faq_path, 'w', encoding='utf-8') as f:
    json.dump(faq_data, f, indent=2, ensure_ascii=False)

print(f"✅ Expanded FAQ database")
print(f"   Total FAQs: {total}")
for crop in faq_data["crops"]:
    print(f"   {crop}: {len(faq_data['crops'][crop]['faqs'])} FAQs")

# Now expand pest/disease database
pest_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\pest_disease_db.json"
with open(pest_path, 'r', encoding='utf-8') as f:
    pest_data = json.load(f)

# Add more pests for Groundnut
pest_data['pests']['Groundnut'] = [
    {
        "id": "thrips_gn",
        "name_en": "Thrips",
        "name_te": "త్రిప్స్",
        "scientific_name": "Scirtothrips dorsalis",
        "type": "sucking",
        "severity": "high",
        "triggers": {"temp_range": [25, 35], "humidity_max": 60, "stage": ["vegetative", "flowering"]},
        "symptoms": ["Silvery patches on leaves", "Leaf curling", "Stunted growth"],
        "economic_threshold": "5 thrips/leaflet",
        "treatment": {"chemical": [{"product": "Fipronil 5 SC", "dose": "2 ml/L"}]}
    },
    {
        "id": "white_grub",
        "name_en": "White Grub",
        "name_te": "తెల్ల పురుగు",
        "scientific_name": "Holotrichia consanguinea",
        "type": "soil_pest",
        "severity": "critical",
        "triggers": {"stage": ["pegging", "pod_development"], "conditions": ["sandy soil", "monsoon"]},
        "symptoms": ["Plants wilting", "Roots eaten", "Pods damaged underground"],
        "treatment": {"chemical": [{"product": "Chlorpyriphos 20 EC", "dose": "2.5 L/ha in irrigation"}]}
    }
]

# Add more diseases for Groundnut
pest_data['diseases']['Groundnut'] = [
    {
        "id": "tikka",
        "name_en": "Tikka Disease (Early/Late Leaf Spot)",
        "name_te": "టిక్కా వ్యాధి",
        "pathogen": "Cercospora arachidicola / Phaeoisariopsis personata",
        "type": "fungal",
        "severity": "high",
        "triggers": {"humidity_min": 80, "temp_range": [25, 30]},
        "symptoms": ["Brown spots with concentric rings", "Severe defoliation"],
        "treatment": {"fungicides": [{"product": "Mancozeb 75 WP", "dose": "2.5 g/L"}]}
    },
    {
        "id": "rust_gn",
        "name_en": "Groundnut Rust",
        "name_te": "తుప్పు",
        "pathogen": "Puccinia arachidis",
        "type": "fungal",
        "severity": "high",
        "triggers": {"humidity_min": 85, "temp_range": [20, 30]},
        "symptoms": ["Orange pustules on lower leaf surface", "Premature leaf fall"],
        "treatment": {"fungicides": [{"product": "Triadimefon 25 WP", "dose": "1 g/L"}]}
    }
]

# Add more for Maize
pest_data['pests']['Maize'].extend([
    {
        "id": "stem_borer_maize",
        "name_en": "Spotted Stem Borer",
        "name_te": "మచ్చల కాండం తొలుచు పురుగు",
        "scientific_name": "Chilo partellus",
        "type": "borer",
        "severity": "high",
        "triggers": {"stage": ["vegetative"], "conditions": ["late sowing"]},
        "symptoms": ["Dead hearts", "Bore holes in stem", "Frass at nodes"],
        "treatment": {"chemical": [{"product": "Carbofuran 3G", "dose": "8-10 kg/acre in whorl"}]}
    }
])

pest_data['diseases']['Maize'] = [
    {
        "id": "tlb",
        "name_en": "Turcicum Leaf Blight",
        "name_te": "టర్సికమ్ లీఫ్ బ్లైట్",
        "pathogen": "Exserohilum turcicum",
        "type": "fungal",
        "severity": "high",
        "triggers": {"humidity_min": 80, "temp_range": [20, 30]},
        "symptoms": ["Long elliptical grey-green lesions", "Lesions coalesce"],
        "treatment": {"fungicides": [{"product": "Mancozeb 75 WP", "dose": "2.5 g/L"}]}
    }
]

# Save updated pest/disease database
with open(pest_path, 'w', encoding='utf-8') as f:
    json.dump(pest_data, f, indent=2, ensure_ascii=False)

pest_count = sum(len(v) for v in pest_data['pests'].values())
disease_count = sum(len(v) for v in pest_data['diseases'].values())

print(f"\n✅ Expanded Pest/Disease Database")
print(f"   Total Pests: {pest_count}")
print(f"   Total Diseases: {disease_count}")
