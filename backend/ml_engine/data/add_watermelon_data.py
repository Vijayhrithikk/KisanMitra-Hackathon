"""
Add comprehensive crop monitoring data for Watermelon and other crops
"""
import json
import os

DATA_DIR = os.path.dirname(__file__)
STAGES_PATH = os.path.join(DATA_DIR, 'crop_stages.json')
FAQS_PATH = os.path.join(DATA_DIR, 'crop_faqs_complete.json')

# Comprehensive Watermelon data
WATERMELON_DATA = {
    "name_en": "Watermelon",
    "name_te": "పుచ్చకాయ",
    "duration_days": 90,
    "seasons": ["Zaid", "Summer", "Kharif"],
    "water_requirement": "High",
    "stages": [
        {
            "name": "Land Preparation",
            "name_te": "భూమి సిద్ధం",
            "week_start": 1,
            "week_end": 1,
            "tasks_en": [
                "Plow field 2-3 times to fine tilth",
                "Apply FYM 10-15 tonnes per hectare",
                "Prepare raised beds or pits 60cm x 60cm x 45cm",
                "Apply basal fertilizers - 50kg N, 60kg P, 60kg K per hectare"
            ],
            "tasks_te": [
                "పొలాన్ని 2-3 సార్లు దున్నండి",
                "హెక్టారుకు 10-15 టన్నులు FYM వేయండి",
                "60x60x45 సెం.మీ గుంటలు తవ్వండి",
                "హెక్టారుకు 50 కిలో N, 60 కిలో P, 60 కిలో K వేయండి"
            ],
            "irrigation_en": "Pre-sowing irrigation for moisture",
            "irrigation_te": "విత్తే ముందు తేమ కోసం నీరు"
        },
        {
            "name": "Sowing",
            "name_te": "విత్తడం",
            "week_start": 2,
            "week_end": 2,
            "tasks_en": [
                "Sow 2-3 seeds per pit at 2-3cm depth",
                "Seed rate: 1.5-2 kg per hectare",
                "Spacing: 2-3m between rows, 1-1.5m between plants",
                "Treat seeds with Thiram 3g/kg before sowing"
            ],
            "tasks_te": [
                "ప్రతి గుంటలో 2-3 విత్తనాలు 2-3 సెం.మీ లోతులో నాటండి",
                "విత్తన రేటు: హెక్టారుకు 1.5-2 కిలో",
                "వరుసల మధ్య 2-3 మీ, మొక్కల మధ్య 1-1.5 మీ",
                "విత్తే ముందు థైరామ్ 3గ్రా/కిలోతో శుద్ధి చేయండి"
            ],
            "irrigation_en": "Light irrigation after sowing",
            "irrigation_te": "విత్తిన తర్వాత తేలికపాటి నీరు"
        },
        {
            "name": "Germination",
            "name_te": "మొలకెత్తడం",
            "week_start": 3,
            "week_end": 3,
            "tasks_en": [
                "Maintain soil moisture for germination",
                "Thin to 2 plants per pit after germination",
                "Monitor for cutworm and protect seedlings",
                "Provide shade if temperature exceeds 40°C"
            ],
            "tasks_te": [
                "మొలకెత్తడానికి మట్టి తేమ నిలపండి",
                "మొలకెత్తిన తర్వాత గుంటకు 2 మొక్కలు ఉంచండి",
                "కట్‌వార్మ్ కోసం పరిశీలించండి",
                "40°C దాటితే నీడ ఇవ్వండి"
            ],
            "irrigation_en": "Light irrigation every 2-3 days",
            "irrigation_te": "2-3 రోజులకు ఒకసారి తేలికపాటి నీరు"
        },
        {
            "name": "Vine Growth",
            "name_te": "తీగ పెరుగుదల",
            "week_start": 4,
            "week_end": 6,
            "tasks_en": [
                "Apply first top dressing - 25kg N per hectare",
                "Train vines in one direction",
                "Weed control - manual or mulching",
                "Monitor for aphids and fruit flies",
                "Apply straw mulch to conserve moisture"
            ],
            "tasks_te": [
                "మొదటి టాప్ డ్రెస్సింగ్ - హెక్టారుకు 25 కిలో N",
                "తీగలను ఒక దిశలో పరచండి",
                "కలుపు నియంత్రణ - చేతి లేదా మల్చింగ్",
                "ఆఫిడ్స్ మరియు ఫ్రూట్ ఫ్లై కోసం పరిశీలించండి",
                "తేమ నిలపడానికి గడ్డి మల్చ్ వేయండి"
            ],
            "irrigation_en": "Regular irrigation every 4-5 days",
            "irrigation_te": "4-5 రోజులకు ఒకసారి నీరు"
        },
        {
            "name": "Flowering",
            "name_te": "పూత",
            "week_start": 7,
            "week_end": 8,
            "tasks_en": [
                "Critical stage - maintain adequate moisture",
                "Apply second top dressing - 25kg N per hectare",
                "Encourage bee activity for pollination",
                "Avoid excess nitrogen to prevent excessive vegetative growth",
                "Monitor for powdery mildew"
            ],
            "tasks_te": [
                "క్లిష్టమైన దశ - తగినంత తేమ నిలపండి",
                "రెండవ టాప్ డ్రెస్సింగ్ - హెక్టారుకు 25 కిలో N",
                "పరాగసంపర్కానికి తేనెటీగలను ప్రోత్సహించండి",
                "అధిక ఆకుల పెరుగుదల నివారించడానికి తక్కువ నత్రజని",
                "పౌడరీ మిల్డ్యూ కోసం పరిశీలించండి"
            ],
            "irrigation_en": "Regular irrigation, avoid water stress",
            "irrigation_te": "క్రమం తప్పకుండా నీరు, నీటి ఒత్తిడి నివారించండి"
        },
        {
            "name": "Fruit Development",
            "name_te": "కాయ అభివృద్ధి",
            "week_start": 9,
            "week_end": 11,
            "tasks_en": [
                "Most critical irrigation stage",
                "Support developing fruits with straw",
                "Rotate fruits for uniform color development",
                "Control fruit fly with traps and sprays",
                "Apply potassium for fruit quality"
            ],
            "tasks_te": [
                "అత్యంత క్లిష్టమైన నీటి దశ",
                "పెరుగుతున్న కాయలకు గడ్డితో ఆధారం ఇవ్వండి",
                "ఏకరీతి రంగు కోసం కాయలను తిప్పండి",
                "ఫ్రూట్ ఫ్లై నియంత్రణ",
                "కాయ నాణ్యత కోసం పొటాషియం వేయండి"
            ],
            "irrigation_en": "Regular deep irrigation every 5-6 days",
            "irrigation_te": "5-6 రోజులకు ఒకసారి లోతైన నీరు"
        },
        {
            "name": "Maturity & Harvest",
            "name_te": "పరిపక్వత & కోత",
            "week_start": 12,
            "week_end": 13,
            "tasks_en": [
                "Reduce irrigation 7-10 days before harvest",
                "Check maturity - tendril drying, thumb test, ground spot color",
                "Harvest early morning for better quality",
                "Leave 2-3 cm stem while harvesting",
                "Handle carefully to avoid bruising"
            ],
            "tasks_te": [
                "కోతకు 7-10 రోజుల ముందు నీరు తగ్గించండి",
                "పరిపక్వత తనిఖీ - తీగ ఎండటం, బొటనవేలు పరీక్ష",
                "మంచి నాణ్యత కోసం ఉదయం కోయండి",
                "కోసేటప్పుడు 2-3 సెం.మీ కాడ ఉంచండి",
                "జాగ్రత్తగా నిర్వహించండి"
            ],
            "irrigation_en": "Stop irrigation before harvest",
            "irrigation_te": "కోతకు ముందు నీరు ఆపండి"
        }
    ],
    "pests": [
        {
            "name": "Fruit Fly",
            "name_te": "ఫ్రూట్ ఫ్లై",
            "symptoms": "Maggots inside fruit, premature fruit drop",
            "symptoms_te": "కాయలో పురుగులు, ముందుగా కాయ రాలడం",
            "control": "Methyl eugenol traps, Malathion spray",
            "control_te": "మిథైల్ యూజినాల్ ట్రాప్స్, మాలథియాన్ పిచికారీ",
            "risk_months": [4, 5, 6, 7]
        },
        {
            "name": "Aphids",
            "name_te": "ఆఫిడ్స్",
            "symptoms": "Curling leaves, sticky honeydew, stunted growth",
            "symptoms_te": "ఆకులు ముడుచుకోవడం, జిగట పదార్థం",
            "control": "Imidacloprid spray, neem oil",
            "control_te": "ఇమిడాక్లోప్రిడ్ పిచికారీ, వేప నూనె",
            "risk_months": [3, 4, 5, 6]
        },
        {
            "name": "Red Pumpkin Beetle",
            "name_te": "ఎర్ర గుమ్మడికాయ పురుగు",
            "symptoms": "Holes in leaves, defoliation",
            "symptoms_te": "ఆకులలో రంధ్రాలు, ఆకులు రాలడం",
            "control": "Carbaryl dust, hand picking",
            "control_te": "కార్బరిల్ పొడి, చేతితో ఏరడం",
            "risk_months": [2, 3, 4]
        }
    ],
    "diseases": [
        {
            "name": "Powdery Mildew",
            "name_te": "పౌడరీ మిల్డ్యూ",
            "symptoms": "White powdery spots on leaves",
            "symptoms_te": "ఆకులపై తెల్లని పొడి మచ్చలు",
            "conditions": "High humidity, 20-25°C",
            "control": "Sulfur dust, Carbendazim spray",
            "control_te": "సల్ఫర్ పొడి, కార్బెండజిమ్ పిచికారీ"
        },
        {
            "name": "Anthracnose",
            "name_te": "ఆంథ్రాక్నోస్",
            "symptoms": "Brown spots on leaves and fruits",
            "symptoms_te": "ఆకులు మరియు కాయలపై గోధుమ మచ్చలు",
            "conditions": "Warm humid weather",
            "control": "Mancozeb spray, remove infected parts",
            "control_te": "మాంకోజెబ్ పిచికారీ, సోకిన భాగాలు తొలగించండి"
        },
        {
            "name": "Fusarium Wilt",
            "name_te": "ఫ్యూసేరియం విల్ట్",
            "symptoms": "Yellowing and wilting of vines",
            "symptoms_te": "తీగలు పసుపు మరియు వాడిపోవడం",
            "conditions": "Soil-borne, warm weather",
            "control": "Resistant varieties, crop rotation",
            "control_te": "నిరోధక రకాలు, పంట భ్రమణం"
        }
    ]
}

# Watermelon FAQs
WATERMELON_FAQS = [
    {"question_en": "What is the best time to sow Watermelon?", "question_te": "పుచ్చకాయ విత్తడానికి ఉత్తమ సమయం?", "answer_en": "February-March for summer crop, June-July for kharif. Avoid cold weather as seeds need 25-30°C for germination.", "answer_te": "వేసవి పంటకు ఫిబ్రవరి-మార్చి, ఖరీఫ్‌కు జూన్-జూలై. చల్లని వాతావరణం నివారించండి.", "category": "sowing", "stage": ["all"]},
    {"question_en": "How much water does Watermelon need?", "question_te": "పుచ్చకాయకు ఎంత నీరు అవసరం?", "answer_en": "Irrigate every 4-5 days during vine growth, every 5-6 days during fruit development. Reduce before harvest.", "answer_te": "తీగ పెరుగుదలలో 4-5 రోజులకు, కాయ అభివృద్ధిలో 5-6 రోజులకు నీరు. కోతకు ముందు తగ్గించండి.", "category": "irrigation", "stage": ["all"]},
    {"question_en": "What fertilizers are recommended for Watermelon?", "question_te": "పుచ్చకాయకు ఏ ఎరువులు సిఫార్సు?", "answer_en": "Apply 100 kg N, 60 kg P2O5, 60 kg K2O per hectare. N in 3 splits - basal, vine growth, flowering.", "answer_te": "హెక్టారుకు 100 కిలో N, 60 కిలో P, 60 కిలో K. N ను 3 భాగాలుగా వేయండి.", "category": "fertilizer", "stage": ["all"]},
    {"question_en": "What are common pests in Watermelon?", "question_te": "పుచ్చకాయలో సాధారణ పురుగులు?", "answer_en": "Fruit fly is most damaging. Use methyl eugenol traps. Also watch for aphids and red pumpkin beetle.", "answer_te": "ఫ్రూట్ ఫ్లై అత్యంత నష్టకరం. మిథైల్ యూజినాల్ ట్రాప్స్ వాడండి. ఆఫిడ్స్ కూడా చూడండి.", "category": "pest", "stage": ["all"]},
    {"question_en": "How to control fruit fly in Watermelon?", "question_te": "పుచ్చకాయలో ఫ్రూట్ ఫ్లై నియంత్రణ?", "answer_en": "Use methyl eugenol traps at 12-15 per hectare. Spray Malathion 50 EC @ 2ml/L. Collect and destroy fallen fruits.", "answer_te": "హెక్టారుకు 12-15 మిథైల్ యూజినాల్ ట్రాప్స్ వాడండి. మాలథియాన్ పిచికారీ చేయండి. పడిన కాయలు నాశనం చేయండి.", "category": "pest", "stage": ["all"]},
    {"question_en": "What diseases affect Watermelon?", "question_te": "పుచ్చకాయను ప్రభావితం చేసే వ్యాధులు?", "answer_en": "Powdery mildew, anthracnose, and fusarium wilt are common. Maintain proper spacing and drainage.", "answer_te": "పౌడరీ మిల్డ్యూ, ఆంథ్రాక్నోస్, ఫ్యూసేరియం విల్ట్ సాధారణం. సరైన దూరం మరియు డ్రైనేజీ ఉంచండి.", "category": "disease", "stage": ["all"]},
    {"question_en": "How to identify ripe Watermelon?", "question_te": "పక్వమైన పుచ్చకాయ ఎలా గుర్తించాలి?", "answer_en": "Look for: 1) Tendril near fruit dries up, 2) Ground spot turns yellow, 3) Hollow sound when tapped, 4) Skin becomes dull.", "answer_te": "చూడండి: 1) కాయ దగ్గర తీగ ఎండిపోవడం, 2) నేల మచ్చ పసుపు రంగు, 3) తట్టినప్పుడు బోలు శబ్దం, 4) చర్మం మందంగా మారడం.", "category": "harvest", "stage": ["all"]},
    {"question_en": "When to harvest Watermelon?", "question_te": "పుచ్చకాయ ఎప్పుడు కోయాలి?", "answer_en": "Harvest 80-90 days after sowing when tendril dries, ground spot is yellow. Harvest in morning for better quality.", "answer_te": "విత్తిన 80-90 రోజుల తర్వాత, తీగ ఎండినప్పుడు కోయండి. మంచి నాణ్యత కోసం ఉదయం కోయండి.", "category": "harvest", "stage": ["all"]},
    {"question_en": "What is the expected yield of Watermelon?", "question_te": "పుచ్చకాయ ఊహించిన దిగుబడి?", "answer_en": "With good practices, expect 30-40 tonnes per hectare for hybrid varieties, 20-25 tonnes for local varieties.", "answer_te": "మంచి పద్ధతులతో హైబ్రిడ్ రకాలకు హెక్టారుకు 30-40 టన్నులు, స్థానిక రకాలకు 20-25 టన్నులు.", "category": "yield", "stage": ["all"]},
    {"question_en": "What is the seed rate for Watermelon?", "question_te": "పుచ్చకాయ విత్తన రేటు?", "answer_en": "Seed rate is 1.5-2 kg per hectare for direct sowing. For transplanting, 300-400g seeds for raising nursery.", "answer_te": "నేరుగా విత్తడానికి హెక్టారుకు 1.5-2 కిలో. నారు పెంచడానికి 300-400 గ్రా.", "category": "sowing", "stage": ["all"]},
    {"question_en": "What spacing is required for Watermelon?", "question_te": "పుచ్చకాయకు ఏ దూరం అవసరం?", "answer_en": "Row to row 2-3 meters, plant to plant 1-1.5 meters. More spacing for spreading varieties.", "answer_te": "వరుసకు వరుస 2-3 మీటర్లు, మొక్కకు మొక్క 1-1.5 మీటర్లు.", "category": "sowing", "stage": ["all"]},
    {"question_en": "How to prepare land for Watermelon?", "question_te": "పుచ్చకాయ కోసం భూమి సిద్ధం?", "answer_en": "Plow 2-3 times, add FYM 10-15 tonnes/ha, prepare circular pits 60x60x45 cm at required spacing.", "answer_te": "2-3 సార్లు దున్నండి, FYM 10-15 టన్నులు/హెక్టారు, 60x60x45 సెం.మీ గుంటలు తవ్వండి.", "category": "land_prep", "stage": ["all"]},
    {"question_en": "How to control weeds in Watermelon?", "question_te": "పుచ్చకాయలో కలుపు నియంత్రణ?", "answer_en": "Apply Pendimethalin 30 EC pre-emergence. Use straw mulch between rows. Hand weeding 2-3 times.", "answer_te": "పెండిమెథాలిన్ ప్రీ-ఎమర్జెన్స్ వేయండి. వరుసల మధ్య గడ్డి మల్చ్ వాడండి. 2-3 సార్లు చేతి కలుపు.", "category": "weed", "stage": ["all"]},
    {"question_en": "How to store Watermelon after harvest?", "question_te": "పుచ్చకాయ కోత తర్వాత నిల్వ?", "answer_en": "Store at 10-15°C with 85-90% humidity. Can be stored for 2-3 weeks. Avoid chilling injury below 7°C.", "answer_te": "10-15°C వద్ద 85-90% తేమతో నిల్వ చేయండి. 2-3 వారాలు నిల్వ చేయవచ్చు. 7°C కంటే తక్కువ నివారించండి.", "category": "storage", "stage": ["all"]},
    {"question_en": "What are the best Watermelon varieties?", "question_te": "మంచి పుచ్చకాయ రకాలు?", "answer_en": "Sugar Baby (small, sweet), Arka Manik (red flesh), Durgapura Meetha, NS-295 (hybrid), Madhubala (seedless).", "answer_te": "సుగర్ బేబీ (చిన్న, తీపి), అర్క మాణిక్ (ఎర్ర గుజ్జు), దుర్గాపూర్ మీఠా, NS-295 (హైబ్రిడ్), మధుబాల (విత్తనాలు లేని).", "category": "variety", "stage": ["all"]},
    {"question_en": "How to improve sweetness in Watermelon?", "question_te": "పుచ్చకాయ తీపి పెంచడం ఎలా?", "answer_en": "Apply potassium during fruit development. Reduce irrigation before harvest. Ensure proper sunlight.", "answer_te": "కాయ అభివృద్ధిలో పొటాషియం వేయండి. కోతకు ముందు నీరు తగ్గించండి. సరైన సూర్యరశ్మి ఉండేలా చూడండి.", "category": "quality", "stage": ["all"]},
    {"question_en": "Why are my Watermelon fruits cracking?", "question_te": "నా పుచ్చకాయలు ఎందుకు పగులుతున్నాయి?", "answer_en": "Fruit cracking is due to irregular irrigation. Maintain uniform moisture. Avoid heavy irrigation after dry spell.", "answer_te": "అసమాన నీటి వల్ల కాయలు పగులుతాయి. ఏకరీతి తేమ నిలపండి. ఎండాకాలం తర్వాత భారీ నీరు నివారించండి.", "category": "problem", "stage": ["all"]},
    {"question_en": "How to increase fruit size in Watermelon?", "question_te": "పుచ్చకాయ పరిమాణం పెంచడం?", "answer_en": "Limit to 3-4 fruits per vine. Apply adequate fertilizers and water. Remove extra fruits early.", "answer_te": "తీగకు 3-4 కాయలకు పరిమితం చేయండి. తగినంత ఎరువులు మరియు నీరు వేయండి. అదనపు కాయలు ముందుగా తొలగించండి.", "category": "yield", "stage": ["all"]},
    {"question_en": "How to manage Watermelon in summer heat?", "question_te": "వేసవి వేడిలో పుచ్చకాయ నిర్వహణ?", "answer_en": "Irrigate in evening or early morning. Apply straw mulch. Provide shade if temperature exceeds 40°C.", "answer_te": "సాయంత్రం లేదా ఉదయం నీరు పెట్టండి. గడ్డి మల్చ్ వేయండి. 40°C దాటితే నీడ ఇవ్వండి.", "category": "stress", "stage": ["all"]},
    {"question_en": "What is pollination requirement for Watermelon?", "question_te": "పుచ్చకాయ పరాగసంపర్కం అవసరం?", "answer_en": "Watermelon needs bee pollination. Avoid pesticide spray during flowering. Maintain bee-friendly environment.", "answer_te": "పుచ్చకాయకు తేనెటీగల పరాగసంపర్కం అవసరం. పూత సమయంలో పురుగుమందు నివారించండి.", "category": "flowering", "stage": ["all"]}
]

def add_watermelon_data():
    # Update crop_stages.json
    with open(STAGES_PATH, 'r', encoding='utf-8') as f:
        stages_data = json.load(f)
    
    # Add/update Watermelon data
    if 'crops' not in stages_data:
        stages_data['crops'] = {}
    
    stages_data['crops']['Watermelon'] = WATERMELON_DATA
    
    # Save
    with open(STAGES_PATH, 'w', encoding='utf-8') as f:
        json.dump(stages_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated Watermelon in crop_stages.json with {len(WATERMELON_DATA['stages'])} stages")
    
    # Update crop_faqs_complete.json
    with open(FAQS_PATH, 'r', encoding='utf-8') as f:
        faqs_data = json.load(f)
    
    if 'crops' not in faqs_data:
        faqs_data['crops'] = {}
    
    faqs_data['crops']['Watermelon'] = {
        "name_te": "పుచ్చకాయ",
        "faqs": WATERMELON_FAQS
    }
    
    # Update total count
    total = sum(len(faqs_data['crops'][c].get('faqs', [])) for c in faqs_data['crops'])
    faqs_data['total_faqs'] = total
    
    # Save
    with open(FAQS_PATH, 'w', encoding='utf-8') as f:
        json.dump(faqs_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated Watermelon FAQs with {len(WATERMELON_FAQS)} FAQs")
    print(f"Total FAQs in database: {total}")

if __name__ == "__main__":
    add_watermelon_data()
