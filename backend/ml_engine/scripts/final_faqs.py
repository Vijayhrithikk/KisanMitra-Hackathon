"""
Add final FAQs to reach 100+ total
"""
import json

faq_path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_faqs_complete.json"
with open(faq_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Add a few more FAQs to cross 100
FINAL_FAQS = {
    "Paddy": [
        {"stage": "maturity", "category": "harvest", "urgency": "medium",
         "question_en": "What is the ideal moisture content for harvesting paddy?",
         "question_te": "వరి కోతకు ఆదర్శ తేమ శాతం ఎంత?",
         "answer_en": "Harvest at 20-22% grain moisture for minimum shattering and cracking.",
         "answer_te": "కనీస రాలడం మరియు పగుళ్లు కోసం 20-22% గింజ తేమలో కోయండి.",
         "action_en": "Use moisture meter. Don't wait for complete field drying.",
         "action_te": "మాయిస్చర్ మీటర్ వాడండి. పొలం పూర్తిగా ఆరడం కోసం వేచి ఉండకండి."},
    ],
    "Cotton": [
        {"stage": "harvest", "category": "harvest", "urgency": "medium",
         "question_en": "How many pickings are ideal for cotton?",
         "question_te": "పత్తికి ఎన్ని కోతలు ఆదర్శం?",
         "answer_en": "3-4 pickings at 15-day intervals. First picking when 30% bolls open.",
         "answer_te": "15-రోజుల వ్యవధిలో 3-4 కోతలు. 30% కాయలు పగిలినప్పుడు మొదటి కోత.",
         "action_en": "Pick only fully opened, dry bolls. Avoid damp cotton.",
         "action_te": "పూర్తిగా పగిలిన, పొడి కాయలు మాత్రమే ఏరండి. తడి పత్తి నివారించండి."},
    ],
    "Maize": [
        {"stage": "maturity", "category": "harvest", "urgency": "medium",
         "question_en": "How to know maize is ready for harvest?",
         "question_te": "మొక్కజొన్న కోతకు సిద్ధమని ఎలా తెలుసుకోవాలి?",
         "answer_en": "Husk turns yellow-brown, kernels hard (black layer visible at base).",
         "answer_te": "పొట్టు పసుపు-గోధుమ రంగులోకి మారుతుంది, గింజలు గట్టిగా (దిగువన నల్ల పొర కనిపిస్తుంది).",
         "action_en": "Scratch kernel base - black layer indicates maturity. Harvest at 20-25% moisture.",
         "action_te": "గింజ దిగువ గోకండి - నల్ల పొర పరిపక్వతను సూచిస్తుంది. 20-25% తేమలో కోయండి."},
    ],
    "Groundnut": [
        {"stage": "flowering", "category": "water", "urgency": "high",
         "question_en": "Critical irrigation stages in groundnut?",
         "question_te": "వేరుశెనగలో క్లిష్టమైన నీటిపారుదల దశలు?",
         "answer_en": "Flowering (25-35 DAS) and Pod development (60-80 DAS) are most critical.",
         "answer_te": "పూత (25-35 రోజులు) మరియు కాయ అభివృద్ధి (60-80 రోజులు) అత్యంత క్లిష్టమైనవి.",
         "action_en": "Don't skip irrigation at these stages. Even one stress can reduce yield 20-30%.",
         "action_te": "ఈ దశలలో నీటిపారుదల వదలకండి. ఒక్క ఒత్తిడి కూడా దిగుబడి 20-30% తగ్గించవచ్చు."},
    ],
    "Chilli": [
        {"stage": "peak_harvest", "category": "harvest", "urgency": "medium",
         "question_en": "How often to harvest chillies for best yield?",
         "question_te": "మంచి దిగుబడి కోసం మిరపకాయలు ఎంత తరచుగా కోయాలి?",
         "answer_en": "Every 7-10 days during peak fruiting. Regular picking promotes new fruit set.",
         "answer_te": "గరిష్ట కాయ సమయంలో ప్రతి 7-10 రోజులు. క్రమం తప్పకుండా ఏరడం కొత్త కాయ ఏర్పాటును ప్రోత్సహిస్తుంది.",
         "action_en": "Pick red/mature fruits regularly. Don't wait for all to ripen.",
         "action_te": "ఎర్రని/పరిపక్వ కాయలను క్రమం తప్పకుండా ఏరండి. అన్నీ పక్వం కావడం కోసం వేచి ఉండకండి."},
    ]
}

# Add to each crop
for crop, faqs in FINAL_FAQS.items():
    data['crops'][crop]['faqs'].extend(faqs)

# Update total
total = sum(len(c["faqs"]) for c in data["crops"].values())
data["total_faqs"] = total

# Save
with open(faq_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Final FAQ count: {total}")
for crop in data["crops"]:
    print(f"   {crop}: {len(data['crops'][crop]['faqs'])} FAQs")
