"""
Expand FAQs to 100+ per crop
Comprehensive coverage of all stages, pests, diseases, fertilizers, irrigation, harvest
"""
import json

# Load existing FAQs
path = r"c:\Users\hi\KisanMitra-AI-v2\backend\ml_engine\data\crop_faqs_complete.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Additional Paddy FAQs (expanding to 100+)
PADDY_EXTRA = [
    # PEST FAQs
    {"stage": "tillering", "category": "pest", "urgency": "critical",
     "question_en": "Yellow plants with hopperburn symptoms spreading rapidly",
     "question_te": "పసుపు మొక్కలు హాపర్‌బర్న్ లక్షణాలు వేగంగా వ్యాపిస్తున్నాయి",
     "answer_en": "Severe BPH outbreak. Population has exceeded economic threshold level.",
     "answer_te": "తీవ్రమైన BPH ప్రాదుర్భావం. జనాభా ఆర్థిక పరిమితి స్థాయిని దాటింది.",
     "action_en": "Drain field completely. Spray Buprofezin 25 SC @ 1.6 ml/L or Pymetrozine 50 WG @ 0.6 g/L",
     "action_te": "పొలం పూర్తిగా ఆరబెట్టండి. బుప్రోఫెజిన్ లేదా పైమెట్రోజిన్ పిచికారీ చేయండి."},
    {"stage": "tillering", "category": "pest", "urgency": "high",
     "question_en": "White egg masses on leaf tips with leaf rolling",
     "question_te": "ఆకు చివరలో తెల్లని గుడ్ల గుంపులు, ఆకులు మడతపడటం",
     "answer_en": "Leaf Folder (Cnaphalocrocis medinalis) oviposition. Will cause serious damage if not controlled.",
     "answer_te": "లీఫ్ ఫోల్డర్ గుడ్లు పెట్టడం. నియంత్రించకపోతే తీవ్ర నష్టం.",
     "action_en": "Spray Cartap hydrochloride 50 SP @ 1g/L or Chlorantraniliprole 18.5 SC @ 0.3 ml/L",
     "action_te": "కార్టాప్ హైడ్రోక్లోరైడ్ లేదా క్లోరాంట్రానిలిప్రోల్ పిచికారీ చేయండి."},
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Silvery white streaks on leaves with brown tips",
     "question_te": "ఆకులపై వెండి తెల్ల గీతలు, గోధుమ చివరలు",
     "answer_en": "Thrips damage. Common in dry weather conditions.",
     "answer_te": "త్రిప్స్ నష్టం. పొడి వాతావరణంలో సాధారణం.",
     "action_en": "Spray Thiamethoxam 25 WG @ 0.5g/L. Maintain adequate irrigation.",
     "action_te": "థియామెథాక్సామ్ పిచికారీ చేయండి. తగిన నీరు ఇవ్వండి."},
    {"stage": "panicle", "category": "pest", "urgency": "high",
     "question_en": "Small galls instead of grains on panicles",
     "question_te": "కంకులపై గింజల బదులు చిన్న ఉబ్బెత్తులు",
     "answer_en": "Gall Midge (Orseolia oryzae) damage. Severe in cloudy, humid weather.",
     "answer_te": "గాల్ మిడ్జ్ నష్టం. మేఘావృతమైన, తేమగల వాతావరణంలో తీవ్రం.",
     "action_en": "Remove and destroy affected tillers. Apply Carbofuran 3G @ 25 kg/ha.",
     "action_te": "నష్టపడిన పిల్లలను తీసివేయండి. కార్బోఫ్యూరాన్ వేయండి."},
    
    # DISEASE FAQs
    {"stage": "tillering", "category": "disease", "urgency": "high",
     "question_en": "Spindle-shaped spots with grey center and brown margin on leaves",
     "question_te": "ఆకులపై బూడిద మధ్యభాగం, గోధుమ అంచులతో కదురు ఆకారపు మచ్చలు",
     "answer_en": "Rice Blast (Magnaporthe oryzae). Most destructive fungal disease.",
     "answer_te": "రైస్ బ్లాస్ట్. అత్యంత వినాశకరమైన బూజు వ్యాధి.",
     "action_en": "Spray Tricyclazole 75 WP @ 0.6g/L or Isoprothiolane 40 EC @ 1.5ml/L immediately.",
     "action_te": "వెంటనే ట్రైసైక్లాజోల్ లేదా ఐసోప్రోథియోలేన్ పిచికారీ చేయండి."},
    {"stage": "flowering", "category": "disease", "urgency": "critical",
     "question_en": "Panicle neck turning brown and breaking",
     "question_te": "కంకి మెడ గోధుమ రంగులోకి మారి విరిగిపోతోంది",
     "answer_en": "Neck Blast - most damaging form of blast. Can cause 100% yield loss.",
     "answer_te": "నెక్ బ్లాస్ట్ - అత్యంత హానికరమైన బ్లాస్ట్ రూపం. 100% దిగుబడి నష్టం.",
     "action_en": "Spray Tricyclazole 75 WP immediately. Repeat after 7 days. Avoid excess nitrogen.",
     "action_te": "వెంటనే ట్రైసైక్లాజోల్ పిచికారీ. 7 రోజుల తర్వాత మళ్ళీ. అధిక నత్రజని నివారించండి."},
    {"stage": "grain_fill", "category": "disease", "urgency": "medium",
     "question_en": "Reddish-brown oval spots on leaf sheath near waterline",
     "question_te": "నీటి స్థాయిలో ఆకు పొరపై ఎర్రటి-గోధుమ అండాకార మచ్చలు",
     "answer_en": "Sheath Blight (Rhizoctonia solani). Spreads rapidly in dense, high nitrogen fields.",
     "answer_te": "షీత్ బ్లైట్. దట్టమైన, అధిక నత్రజని పొలాలలో వేగంగా వ్యాపిస్తుంది.",
     "action_en": "Drain and dry field. Spray Hexaconazole 5 EC @ 2ml/L or Validamycin 3 SL @ 2ml/L.",
     "action_te": "పొలం ఆరబెట్టండి. హెక్సాకొనాజోల్ లేదా వాలిడామైసిన్ పిచికారీ."},
    {"stage": "tillering", "category": "disease", "urgency": "high",
     "question_en": "Greyish green water-soaked streaks on leaves from tip",
     "question_te": "ఆకు చివర నుండి బూడిద ఆకుపచ్చ నీటి మచ్చల గీతలు",
     "answer_en": "Bacterial Leaf Blight (Xanthomonas oryzae). Spreads through irrigation water.",
     "answer_te": "బాక్టీరియల్ లీఫ్ బ్లైట్. నీటిపారుదల నీటి ద్వారా వ్యాపిస్తుంది.",
     "action_en": "Drain excess water. Spray Streptocycline 6g + COC 50g per 15L water. Repeat 3 times.",
     "action_te": "అదనపు నీరు తీసివేయండి. స్ట్రెప్టోసైక్లిన్ + COC పిచికారీ. 3 సార్లు."},
    
    # FERTILIZER FAQs
    {"stage": "nursery", "category": "fertilizer", "urgency": "medium",
     "question_en": "How much fertilizer for nursery bed?",
     "question_te": "నారుమడికి ఎంత ఎరువు వేయాలి?",
     "answer_en": "For 100 sqm nursery: DAP 2.5 kg at sowing. Urea 1 kg at 10 DAS if needed.",
     "answer_te": "100 చ.మీ నారుమడికి: విత్తేటప్పుడు DAP 2.5 కిలో. అవసరమైతే 10 రోజులకు యూరియా 1 కిలో.",
     "action_en": "Apply DAP in nursery bed before sowing. Mix with soil.",
     "action_te": "విత్తడానికి ముందు నారుమడిలో DAP వేయండి. మట్టితో కలపండి."},
    {"stage": "tillering", "category": "fertilizer", "urgency": "high",
     "question_en": "Plants are light green despite fertilizer application",
     "question_te": "ఎరువు వేసినా మొక్కలు తేలికపాటి పచ్చగా ఉన్నాయి",
     "answer_en": "Possible Nitrogen deficiency or poor uptake due to waterlogging/improper pH.",
     "answer_te": "నత్రజని లోపం లేదా నీరు నిలవడం/సరికాని pH వల్ల పోషక స్వీకరణ లోపం.",
     "action_en": "Check water level. If excess, drain. Apply Urea 10 kg/acre as foliar spray (2% solution).",
     "action_te": "నీటి స్థాయి తనిఖీ చేయండి. అధికమైతే తీసివేయండి. యూరియా ఆకులపై పిచికారీ చేయండి."},
    {"stage": "panicle", "category": "fertilizer", "urgency": "critical",
     "question_en": "When to apply potash in paddy?",
     "question_te": "వరిలో పొటాష్ ఎప్పుడు వేయాలి?",
     "answer_en": "Apply MOP at panicle initiation (50-55 DAT) for better grain filling and quality.",
     "answer_te": "మెరుగైన గింజ నింపడం మరియు నాణ్యత కోసం కంకి ప్రారంభంలో (50-55 రోజులు) MOP వేయండి.",
     "action_en": "Apply MOP 20-25 kg/acre at panicle initiation. Combine with last Urea dose.",
     "action_te": "కంకి ప్రారంభంలో MOP 20-25 కిలో/ఎకరం వేయండి. చివరి యూరియాతో కలపండి."},
    
    # IRRIGATION FAQs
    {"stage": "transplanting", "category": "water", "urgency": "high",
     "question_en": "How much water depth immediately after transplanting?",
     "question_te": "నాటిన వెంటనే ఎంత నీటి లోతు ఉండాలి?",
     "answer_en": "Maintain 2-3 cm water for first 7 days. Then increase to 5 cm.",
     "answer_te": "మొదటి 7 రోజులు 2-3 సెం.మీ నీరు. తర్వాత 5 సెం.మీకి పెంచండి.",
     "action_en": "Shallow water initially helps transplants establish. Increase depth gradually.",
     "action_te": "నిస్సారంగా నీరు మొదట నాటిన మొక్కలు స్థిరపడటానికి సహాయపడుతుంది."},
    {"stage": "tillering", "category": "water", "urgency": "medium",
     "question_en": "Can I use AWD technique? When to refill water?",
     "question_te": "AWD పద్ధతి వాడవచ్చా? నీరు ఎప్పుడు పెట్టాలి?",
     "answer_en": "Yes, AWD saves 20-30% water. Refill when water drops 15cm below surface (use pipe method).",
     "answer_te": "అవును, AWD 20-30% నీరు ఆదా చేస్తుంది. నీరు ఉపరితలం కింద 15సెం.మీ పడినప్పుడు పెట్టండి.",
     "action_en": "Install observation tube. When no water visible in tube, irrigate to 5cm.",
     "action_te": "పరిశీలన గొట్టం పెట్టండి. గొట్టంలో నీరు కనిపించకపోతే, 5సెం.మీ నీరు పెట్టండి."},
    {"stage": "flowering", "category": "water", "urgency": "critical",
     "question_en": "Field dried up during flowering - will I lose crop?",
     "question_te": "పూత సమయంలో పొలం ఆరిపోయింది - పంట పోతుందా?",
     "answer_en": "Critical! Drought during flowering causes spikelet sterility. Yield can drop 30-50%.",
     "answer_te": "క్లిష్టమైన! పూత సమయంలో కరువు వల్ల గింజలు ఏర్పడవు. దిగుబడి 30-50% తగ్గవచ్చు.",
     "action_en": "Irrigate immediately. Maintain 5cm water continuously during flowering.",
     "action_te": "వెంటనే నీరు పెట్టండి. పూత సమయంలో నిరంతరం 5సెం.మీ నీరు నిలపండి."},
    
    # WEED FAQs
    {"stage": "tillering", "category": "weed", "urgency": "high",
     "question_en": "Grassy weeds like Echinochloa spreading in field",
     "question_te": "ఈచినోక్లోవా వంటి గడ్డి కలుపు మొక్కలు పొలంలో వ్యాపిస్తున్నాయి",
     "answer_en": "Common grass weed. Competes heavily for nutrients during tillering.",
     "answer_te": "సాధారణ గడ్డి కలుపు. పిల్లలు పట్టే సమయంలో పోషకాలకు తీవ్రంగా పోటీ పడుతుంది.",
     "action_en": "Apply Bispyribac sodium 10 SC @ 20ml/acre at 15-20 DAT. Or hand weed.",
     "action_te": "నాటిన 15-20 రోజులకు బిస్పైరిబాక్ సోడియం 20మి.లీ/ఎకరం వేయండి. లేదా చేతి కలుపు."},
    {"stage": "vegetative", "category": "weed", "urgency": "medium",
     "question_en": "Cyperus (sedge) weeds taking over field",
     "question_te": "సైప్రస్ (నాచు) కలుపు మొక్కలు పొలాన్ని ఆక్రమిస్తున్నాయి",
     "answer_en": "Sedges are difficult to control. Need specific herbicides.",
     "answer_te": "నాచు మొక్కలు నియంత్రించడం కష్టం. ప్రత్యేక కలుపు మందులు అవసరం.",
     "action_en": "Apply Ethoxysulfuron 15 WG @ 20g/acre. Or apply 2,4-D 80% @ 0.5 kg/acre.",
     "action_te": "ఎథాక్సీసల్ఫ్యూరాన్ 20గ్రా/ఎకరం వేయండి. లేదా 2,4-D 0.5 కిలో/ఎకరం."},
    
    # HARVEST FAQs
    {"stage": "harvest", "category": "harvest", "urgency": "high",
     "question_en": "Some panicles still green, some yellow - should I wait?",
     "question_te": "కొన్ని కంకులు ఇంకా పచ్చగా, కొన్ని పసుపు - వేచి ఉండాలా?",
     "answer_en": "Harvest when 80-85% panicles are golden. Waiting for 100% causes shattering loss.",
     "answer_te": "80-85% కంకులు బంగారు రంగు అయినప్పుడు కోయండి. 100% కోసం వేచి ఉంటే రాలిపోతాయి.",
     "action_en": "Harvest at 20-22% grain moisture. Don't wait for complete drying in field.",
     "action_te": "20-22% గింజ తేమలో కోయండి. పొలంలో పూర్తిగా ఆరడం కోసం వేచి ఉండకండి."},
    {"stage": "harvest", "category": "harvest", "urgency": "critical",
     "question_en": "Cyclone warning during harvest season - what to do?",
     "question_te": "కోత సీజన్‌లో తుఫాను హెచ్చరిక - ఏమి చేయాలి?",
     "answer_en": "Harvest immediately even if slightly early. Lodged crop is very difficult to harvest.",
     "answer_te": "కొంచెం ముందే అయినా వెంటనే కోయండి. పడిపోయిన పంట కోయడం చాలా కష్టం.",
     "action_en": "Priority harvest mature fields. Arrange immediate threshing and drying.",
     "action_te": "పరిపక్వ పొలాలను ప్రాధాన్యతగా కోయండి. వెంటనే నూర్చడం మరియు ఆరబెట్టడం ఏర్పాటు చేయండి."},
    
    # STORAGE FAQs
    {"stage": "post_harvest", "category": "storage", "urgency": "medium",
     "question_en": "How to store paddy to prevent storage pests?",
     "question_te": "నిల్వ పురుగులను నివారించడానికి వరి ఎలా నిల్వ చేయాలి?",
     "answer_en": "Dry to 12-14% moisture. Store in clean, dry place. Use neem leaves or Deltamethrin dust.",
     "answer_te": "12-14% తేమకు ఆరబెట్టండి. శుభ్రమైన, పొడి ప్రదేశంలో నిల్వ చేయండి. వేప ఆకులు లేదా డెల్టామెత్రిన్ వాడండి.",
     "action_en": "Check moisture before storage. Aerate periodically. Check for insect activity monthly.",
     "action_te": "నిల్వ చేయడానికి ముందు తేమ తనిఖీ చేయండి. కాలానుగుణంగా గాలి ఇవ్వండి. నెలవారీగా పురుగుల కార్యకలాపాలు తనిఖీ చేయండి."},
]

# Additional Cotton FAQs
COTTON_EXTRA = [
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "White powdery coating on leaves with sooty mold",
     "question_te": "ఆకులపై తెల్లని పొడి పూత మరియు మసి బూజు",
     "answer_en": "Whitefly (Bemisia tabaci) infestation. Also transmits leaf curl virus.",
     "answer_te": "వైట్‌ఫ్లై దాడి. లీఫ్ కర్ల్ వైరస్ కూడా వ్యాపిస్తుంది.",
     "action_en": "Spray Spiromesifen 22.9 SC @ 0.5ml/L or Diafenthiuron 50 WP @ 1g/L.",
     "action_te": "స్పైరోమెసిఫెన్ లేదా డయాఫెంథియురాన్ పిచికారీ చేయండి."},
    {"stage": "squaring", "category": "pest", "urgency": "critical",
     "question_en": "Squares with small holes and black frass",
     "question_te": "చదరాలపై చిన్న రంధ్రాలు మరియు నల్లని మలం",
     "answer_en": "Spotted Bollworm (Earias vittella). Attacks squares and young bolls.",
     "answer_te": "స్పాటెడ్ బోల్వార్మ్. చదరాలు మరియు చిన్న కాయలపై దాడి చేస్తుంది.",
     "action_en": "Spray Emamectin benzoate 5 SG @ 0.4g/L. Install pheromone traps @ 5/acre.",
     "action_te": "ఎమామెక్టిన్ బెంజోయేట్ పిచికారీ. ఎకరాకు 5 ఫెరమోన్ ట్రాప్స్ పెట్టండి."},
    {"stage": "flowering", "category": "pest", "urgency": "critical",
     "question_en": "Large green caterpillars eating leaves and squares voraciously",
     "question_te": "పెద్ద పచ్చ పురుగులు ఆకులు మరియు చదరాలను అత్యాశతో తింటున్నాయి",
     "answer_en": "Tobacco Caterpillar (Spodoptera litura). Night feeder causing severe defoliation.",
     "answer_te": "టొబాకో క్యాటర్‌పిల్లర్. రాత్రి తినే, తీవ్రమైన ఆకు రాలడం.",
     "action_en": "Spray Chlorantraniliprole 18.5 SC @ 0.3ml/L. Apply in evening for best results.",
     "action_te": "క్లోరాంట్రానిలిప్రోల్ పిచికారీ. మంచి ఫలితాల కోసం సాయంత్రం వేయండి."},
    {"stage": "boll", "category": "pest", "urgency": "high",
     "question_en": "White cottony masses on stems and leaves",
     "question_te": "కాండాలు మరియు ఆకులపై తెల్లని పత్తి వంటి పదార్థం",
     "answer_en": "Mealybug infestation. Serious pest especially late in season.",
     "answer_te": "మీలీబగ్ దాడి. ముఖ్యంగా సీజన్ చివరలో తీవ్రమైన పురుగు.",
     "action_en": "Spray Profenophos 50 EC @ 2ml/L + Neem oil 5ml/L. Ensure good coverage.",
     "action_te": "ప్రొఫెనోఫాస్ + వేప నూనె పిచికారీ. మంచి కవరేజ్ నిర్ధారించండి."},
    {"stage": "vegetative", "category": "disease", "urgency": "high",
     "question_en": "Stunted plants with small crinkled leaves - no treatment working",
     "question_te": "చిన్న ముడతలు పడిన ఆకులతో కుదించిన మొక్కలు - చికిత్స పని చేయడం లేదు",
     "answer_en": "Cotton Leaf Curl Virus (CLCuV). Transmitted by whitefly. No cure available.",
     "answer_te": "కాటన్ లీఫ్ కర్ల్ వైరస్. వైట్‌ఫ్లై ద్వారా వ్యాపిస్తుంది. చికిత్స లేదు.",
     "action_en": "Remove infected plants. Control whitefly vectors. Use resistant varieties next season.",
     "action_te": "సోకిన మొక్కలు తీసివేయండి. వైట్‌ఫ్లై నియంత్రించండి. తదుపరి సీజన్‌లో నిరోధక రకాలు వాడండి."},
    {"stage": "flowering", "category": "fertilizer", "urgency": "high",
     "question_en": "Heavy vegetative growth but no squares forming",
     "question_te": "భారీ శాకాహార పెరుగుదల కానీ చదరాలు ఏర్పడటం లేదు",
     "answer_en": "Excess nitrogen causing vegetative growth at expense of reproductive growth.",
     "answer_te": "అధిక నత్రజని వల్ల ప్రత్యుత్పత్తి పెరుగుదల కంటే శాకాహార పెరుగుదల.",
     "action_en": "Stop nitrogen. Apply potash 20kg/acre. Spray NAA 20ppm to induce flowering.",
     "action_te": "నత్రజని ఆపండి. పొటాష్ 20కిలో/ఎకరం వేయండి. పూత కోసం NAA పిచికారీ."},
]

# Additional Maize FAQs
MAIZE_EXTRA = [
    {"stage": "vegetative", "category": "pest", "urgency": "critical",
     "question_en": "Windows (translucent patches) on leaves with frass in whorl",
     "question_te": "ఆకులపై విండోలు (పారదర్శక మచ్చలు), గుండెలో మలం",
     "answer_en": "Classic Fall Armyworm (FAW) damage. Check whorl for larvae.",
     "answer_te": "క్లాసిక్ ఫాల్ ఆర్మీవార్మ్ నష్టం. లార్వా కోసం గుండెను తనిఖీ చేయండి.",
     "action_en": "Spray Spinetoram 11.7 SC @ 0.5ml/L into whorl early morning. Repeat after 7 days if needed.",
     "action_te": "ఉదయం గుండెలో స్పైనెటోరామ్ పిచికారీ. అవసరమైతే 7 రోజుల తర్వాత మళ్ళీ."},
    {"stage": "vegetative", "category": "pest", "urgency": "high",
     "question_en": "Dead heart in young maize plants (15-25 days old)",
     "question_te": "యువ మొక్కజొన్న మొక్కలలో డెడ్ హార్ట్ (15-25 రోజుల వయస్సు)",
     "answer_en": "Shoot Fly (Atherigona soccata) damage. Common in late-sown crops.",
     "answer_te": "షూట్ ఫ్లై నష్టం. ఆలస్యంగా విత్తిన పంటలలో సాధారణం.",
     "action_en": "Apply Carbofuran 3G @ 4-5 kg/acre in whorl. Remove dead hearts.",
     "action_te": "గుండెలో కార్బోఫ్యూరాన్ 4-5 కిలో/ఎకరం వేయండి. డెడ్ హార్ట్స్ తీసివేయండి."},
    {"stage": "tasseling", "category": "disease", "urgency": "high",
     "question_en": "White/grey streaks running parallel to veins on leaves",
     "question_te": "ఆకులపై ఈనెలకు సమాంతరంగా తెలుపు/బూడిద గీతలు",
     "answer_en": "Downy Mildew (Peronosclerospora sorghi). Systemic infection.",
     "answer_te": "డౌనీ మిల్డ్యూ. సిస్టమిక్ ఇన్ఫెక్షన్.",
     "action_en": "Spray Metalaxyl 35 WS @ 6g/kg seed treatment. Foliar spray Ridomil MZ @ 2.5g/L.",
     "action_te": "మెటలాక్సిల్ విత్తన శుద్ధి. రిడోమిల్ MZ ఆకులపై పిచికారీ."},
    {"stage": "silking", "category": "water", "urgency": "critical",
     "question_en": "Tassels emerged but silks not coming out",
     "question_te": "తురాయిలు వచ్చాయి కానీ పట్టు రావడం లేదు",
     "answer_en": "Asynchrony - usually due to drought stress. Poor pollination will result.",
     "answer_te": "అసమకాలీనత - సాధారణంగా కరువు ఒత్తిడి వల్ల. పేలవమైన పరాగసంపర్కం జరుగుతుంది.",
     "action_en": "Irrigate immediately. Apply light irrigation daily until silks emerge.",
     "action_te": "వెంటనే నీరు పెట్టండి. పట్టు వచ్చే వరకు రోజూ తేలికపాటి నీరు ఇవ్వండి."},
]

# Additional Groundnut FAQs
GROUNDNUT_EXTRA = [
    {"stage": "flowering", "category": "fertilizer", "urgency": "critical",
     "question_en": "Why is gypsum so important in groundnut?",
     "question_te": "వేరుశెనగలో జిప్సమ్ ఎందుకు చాలా ముఖ్యం?",
     "answer_en": "Gypsum provides Calcium + Sulphur. Calcium essential for peg penetration and pod filling.",
     "answer_te": "జిప్సమ్ కాల్షియం + సల్ఫర్ అందిస్తుంది. గూర్చి వెళ్ళడానికి మరియు కాయ నింపడానికి కాల్షియం అవసరం.",
     "action_en": "Apply 200 kg/acre at flowering + 100 kg at pegging. Apply in ring around plants.",
     "action_te": "పూతలో 200 కిలో/ఎకరం + గూర్చిలో 100 కిలో. మొక్కల చుట్టూ రింగ్‌లో వేయండి."},
    {"stage": "pod", "category": "disease", "urgency": "high",
     "question_en": "Orange-brown pustules on lower surface of leaves",
     "question_te": "ఆకుల దిగువ ఉపరితలంపై నారింజ-గోధుమ బొబ్బలు",
     "answer_en": "Groundnut Rust (Puccinia arachidis). Serious in high humidity conditions.",
     "answer_te": "వేరుశెనగ రస్ట్. అధిక తేమ పరిస్థితులలో తీవ్రం.",
     "action_en": "Spray Triadimefon 25 WP @ 1g/L or Hexaconazole 5 EC @ 2ml/L. Repeat after 15 days.",
     "action_te": "ట్రైయాడిమెఫాన్ లేదా హెక్సాకొనాజోల్ పిచికారీ. 15 రోజుల తర్వాత మళ్ళీ."},
    {"stage": "pegging", "category": "pest", "urgency": "medium",
     "question_en": "Irregular mines/tunnels in leaves",
     "question_te": "ఆకులలో అసమానమైన సొరంగాలు",
     "answer_en": "Leaf Miner (Aproaerema modicella) damage. Common during vegetative stage.",
     "answer_te": "లీఫ్ మైనర్ నష్టం. శాకాహార దశలో సాధారణం.",
     "action_en": "Spray Dimethoate 30 EC @ 1.5ml/L or Profenophos 50 EC @ 2ml/L.",
     "action_te": "డైమిథోయేట్ లేదా ప్రొఫెనోఫాస్ పిచికారీ."},
]

# Additional Chilli FAQs
CHILLI_EXTRA = [
    {"stage": "vegetative", "category": "pest", "urgency": "critical",
     "question_en": "Leaves curling upward and becoming boat-shaped",
     "question_te": "ఆకులు పైకి మడతపడి పడవ ఆకారంలో మారుతున్నాయి",
     "answer_en": "Severe Thrips + Mite damage. Combined infestation common in hot dry weather.",
     "answer_te": "తీవ్రమైన త్రిప్స్ + మైట్ నష్టం. వేడి పొడి వాతావరణంలో కలిసి దాడి సాధారణం.",
     "action_en": "Spray Fipronil 5 SC @ 1.5ml/L + Abamectin 1.9 EC @ 0.5ml/L. Repeat after 10 days.",
     "action_te": "ఫిప్రోనిల్ + అబామెక్టిన్ పిచికారీ. 10 రోజుల తర్వాత మళ్ళీ."},
    {"stage": "fruiting", "category": "disease", "urgency": "high",
     "question_en": "Fruits rotting from bottom with concentric rings",
     "question_te": "కాయలు దిగువ నుండి కేంద్ర వలయాలతో కుళ్ళిపోతున్నాయి",
     "answer_en": "Anthracnose (Colletotrichum capsici). Major post-rain disease.",
     "answer_te": "ఆంథ్రాక్నోస్. వర్షం తర్వాత ప్రధాన వ్యాధి.",
     "action_en": "Spray Azoxystrobin 23 SC @ 1ml/L or Carbendazim 50 WP @ 1g/L. Remove infected fruits.",
     "action_te": "అజోక్సీస్ట్రోబిన్ లేదా కార్బెండజిమ్ పిచికారీ. సోకిన కాయలు తీసివేయండి."},
    {"stage": "flowering", "category": "pest", "urgency": "high",
     "question_en": "Small holes in fruits with caterpillar inside",
     "question_te": "కాయలలో చిన్న రంధ్రాలు, లోపల పురుగు",
     "answer_en": "Fruit Borer (Helicoverpa armigera). Same as tomato fruit borer.",
     "answer_te": "ఫ్రూట్ బోరర్. టమాటా ఫ్రూట్ బోరర్ వలె.",
     "action_en": "Spray Spinosad 45 SC @ 0.3ml/L at flowering. Repeat every 10 days during fruiting.",
     "action_te": "పూతలో స్పినోసాడ్ పిచికారీ. కాయ సమయంలో ప్రతి 10 రోజులకు మళ్ళీ."},
    {"stage": "vegetative", "category": "disease", "urgency": "critical",
     "question_en": "Plants wilting despite adequate water, roots brown inside",
     "question_te": "తగినంత నీరు ఉన్నా మొక్కలు వాడిపోతున్నాయి, వేర్లు లోపల గోధుమ",
     "answer_en": "Fusarium Wilt. Soil-borne fungal disease. Very difficult to control once established.",
     "answer_te": "ఫ్యూసారియం విల్ట్. మట్టి ద్వారా వచ్చే బూజు వ్యాధి. స్థిరపడిన తర్వాత నియంత్రించడం చాలా కష్టం.",
     "action_en": "Remove infected plants. Drench Carbendazim 1g/L around healthy plants. Use resistant varieties.",
     "action_te": "సోకిన మొక్కలు తీసివేయండి. ఆరోగ్యకరమైన మొక్కల చుట్టూ కార్బెండజిమ్ డ్రెంచ్. నిరోధక రకాలు వాడండి."},
]

# Merge new FAQs
data['crops']['Paddy']['faqs'].extend(PADDY_EXTRA)
data['crops']['Cotton']['faqs'].extend(COTTON_EXTRA)
data['crops']['Maize']['faqs'].extend(MAIZE_EXTRA)
data['crops']['Groundnut']['faqs'].extend(GROUNDNUT_EXTRA)
data['crops']['Chilli']['faqs'].extend(CHILLI_EXTRA)

# Update total count
total = sum(len(c["faqs"]) for c in data["crops"].values())
data["total_faqs"] = total

# Save updated file
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Expanded FAQ database")
print(f"   Total FAQs: {total}")
for crop in data["crops"]:
    print(f"   {crop}: {len(data['crops'][crop]['faqs'])} FAQs")
