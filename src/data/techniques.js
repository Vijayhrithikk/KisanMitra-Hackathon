import dripIrrigationImg from '../assets/drip-irrigation.png';
import droneSprayingImg from '../assets/drone-spraying.png';
import soilTestingImg from '../assets/soil-testing.png';
import zbnfImg from '../assets/zbnf.png';
import hydroponicsImg from '../assets/hydroponics.png';
import sriPaddyImg from '../assets/sri-paddy.png';
import solarPumpImg from '../assets/solar-pump.png';

// Placeholder images for others (reusing existing ones for now to save generation time/tokens, 
// in a real app we'd generate unique ones for all)
const mulchingImg = dripIrrigationImg;
const laserLevelingImg = droneSprayingImg;
const vermicompostImg = zbnfImg;
const azollaImg = sriPaddyImg;
const greenhouseImg = hydroponicsImg;
const precisionFarmingImg = droneSprayingImg;
const fishFarmingImg = sriPaddyImg;
const intercroppingImg = zbnfImg;

export const techniques = [
    {
        id: 'drip-irrigation',
        title: { en: 'Drip Irrigation', te: 'బిందు సేద్యం (Drip Irrigation)' },
        image: dripIrrigationImg,
        summary: { en: 'Precision water delivery system saving 70% water while doubling crop yield.', te: '70% వరకు నీటిని ఆదా చేస్తూ, పంట దిగుబడిని రెట్టింపు చేసే అత్యుత్తమ సాగునీటి పద్ధతి.' },
        content: {
            en: {
                whatIsIt: "Drip irrigation is a micro-irrigation system that saves water and nutrients by allowing water to drip slowly to the roots of plants, either from above the soil surface or buried below the surface. The goal is to place water directly into the root zone and minimize evaporation.",
                whyNeedIt: "With Andhra Pradesh facing depleting groundwater levels (especially in Rayalaseema), traditional flood irrigation wastes 50-60% of water. Drip irrigation is essential for sustainable farming in water-scarce regions.",
                benefits: [
                    "Water Efficiency: 90-95% application efficiency compared to 30-50% in flood irrigation.",
                    "Yield Increase: 30-50% higher yields due to consistent moisture levels.",
                    "Fertilizer Savings: 30-40% reduction through Fertigation (applying fertilizer with water).",
                    "Weed Control: Reduced weed growth as water is applied only to the crop root zone.",
                    "Labor Saving: Automated operation reduces manual labor for watering."
                ],
                mistakes: [
                    "Ignoring Filtration: Not cleaning sand/screen filters leads to emitter clogging.",
                    "Incorrect Pressure: Operating at pressure higher/lower than recommended (usually 1.0-1.5 kg/cm²).",
                    "Shallow Installation: Laterals placed too shallow can be damaged during weeding.",
                    "Acid Treatment Neglect: Failing to flush lines with acid to remove salt deposits."
                ],
                implementation: [
                    { step: "1. Site Survey", desc: "Measure field topography and soil type. Calculate water requirement based on crop." },
                    { step: "2. Design Layout", desc: "Plan Main line, Sub-main, and Laterals. Select emitter spacing (e.g., 40cm for vegetables)." },
                    { step: "3. Installation", desc: "Install pump, filtration unit (Sand+Screen), and Fertigation venturi. Lay PVC mains and LLDPE laterals." },
                    { step: "4. Testing", desc: "Flush the system. Check pressure at tail ends (should be >0.8 kg/cm²). Check for leaks." },
                    { step: "5. Operation", desc: "Run system for calculated duration (e.g., 45 mins/day). Clean filters daily." }
                ],
                apSpecifics: {
                    soil: "Suitable for all soils, especially Red Sandy Loams of Anantapur/Kurnool.",
                    crops: "Chillies, Cotton, Groundnut, Tomato, Banana, Papaya.",
                    climate: "Ideal for semi-arid zones of Rayalaseema and uplands of Coastal AP."
                },
                layout: "Source -> Pump -> Hydrocyclone/Sand Filter -> Fertigation Unit -> Screen Filter -> Main Line -> Sub-main -> Lateral -> Emitter",
                stats: {
                    yield: "+40-60% (Proven in AP Groundnut)",
                    water: "Save 50-70% (approx 15-20 Lakh Liters/acre/season)",
                    cost: "₹45,000 - ₹60,000 per acre (varies by spacing)"
                },
                risks: [
                    "Clogging: Emitters blocked by salts/algae.",
                    "Rodent Damage: Rats chewing LLDPE pipes.",
                    "High Initial Cost: Capital intensive without subsidy."
                ],
                faq: [
                    { q: "How long should I run the drip?", a: "Depends on crop stage and weather. Typically 1-2 hours daily in summer." },
                    { q: "Can I use soluble fertilizers?", a: "Yes, use 19:19:19, Urea, or White Potash. Avoid SSP (clogs emitters)." },
                    { q: "How to clean clogged drippers?", a: "Flush with Sulphuric/Hydrochloric acid (pH 2-3) periodically." }
                ],
                troubleshooting: [
                    { symptom: "Low Pressure at End", cause: "Leakage or Filter choke", action: "Clean filters, check for leaks." },
                    { symptom: "Uneven Wetting", cause: "Clogged emitters", action: "Acid treatment or Chlorine flushing." }
                ],
                costBenefit: {
                    cost: "₹50,000 (Subsidized: ₹10k-15k)",
                    savings: "Labor: ₹5000, Fertilizer: ₹3000",
                    profit: "Extra Yield: ₹30,000+",
                    payback: "1-2 Crop Seasons"
                },
                finalGuidance: "Apply for APMIP (Andhra Pradesh Micro Irrigation Project) subsidy (up to 90% for small farmers). Maintain filters strictly."
            },
            te: {
                whatIsIt: "బిందు సేద్యం (డ్రిప్ ఇరిగేషన్) అనేది మొక్కల వేర్లకు నేరుగా, చుక్కలు చుక్కలుగా నీటిని అందించే అత్యంత సమర్థవంతమైన పద్ధతి. ఇది నీటి వృధాను అరికట్టి, మొక్కకు అవసరమైన తేమను మాత్రమే అందిస్తుంది.",
                whyNeedIt: "ఆంధ్రప్రదేశ్‌లో, ముఖ్యంగా రాయలసీమ వంటి ప్రాంతాల్లో భూగర్భ జలాలు అడుగంటుతున్నాయి. సంప్రదాయ వరద పారకం పద్ధతిలో 50-60% నీరు వృధా అవుతుంది. బిందు సేద్యం ద్వారా ఈ నీటిని ఆదా చేసి, తక్కువ నీటితో ఎక్కువ పంట పండించవచ్చు.",
                benefits: [
                    "నీటి ఆదా: 90-95% నీటి వినియోగ సామర్థ్యం (వరద పారకంలో కేవలం 30-50%).",
                    "దిగుబడి పెరుగుదల: మొక్కకు నిరంతరం తేమ అందడం వల్ల 30-50% అధిక దిగుబడి.",
                    "ఎరువుల ఆదా: ఫెర్టిగేషన్ (నీటితో పాటు ఎరువులు) ద్వారా 30-40% ఎరువుల ఆదా.",
                    "కలుపు నివారణ: నీరు కేవలం మొక్క వేరు దగ్గరే పడుతుంది కాబట్టి, ఖాళీ స్థలంలో కలుపు పెరగదు.",
                    "కూలీల ఖర్చు ఆదా: నీరు పెట్టడానికి మనిషి అవసరం లేదు, వాల్వ్ తిప్పితే చాలు."
                ],
                mistakes: [
                    "ఫిల్టర్లు శుభ్రం చేయకపోవడం: ఇసుక/స్క్రీన్ ఫిల్టర్లను రోజు శుభ్రం చేయకపోతే డ్రిప్పర్లు మూసుకుపోతాయి.",
                    "తప్పు ఒత్తిడి (Pressure): సిఫార్సు చేసిన దానికంటే ఎక్కువ లేదా తక్కువ ఒత్తిడితో నడపడం.",
                    "ఆమ్ల శుద్ధి (Acid Wash) చేయకపోవడం: పైపుల్లో ఉప్పు పేరుకుపోయినప్పుడు యాసిడ్ వాష్ చేయకపోవడం."
                ],
                implementation: [
                    { step: "1. క్షేత్ర పరిశీలన", desc: "పొలం కొలతలు, నేల రకం మరియు నీటి లభ్యతను బట్టి డిజైన్ చేయాలి." },
                    { step: "2. డిజైన్ & లేఅవుట్", desc: "మెయిన్ లైన్, సబ్-మెయిన్, మరియు లేటరల్ పైపుల అమరిక. పంటను బట్టి డ్రిప్పర్ల దూరం (ఉదా: కూరగాయలకు 40cm)." },
                    { step: "3. ఏర్పాటు (Installation)", desc: "మోటార్, ఫిల్టర్లు (శాండ్+స్క్రీన్), ఫెర్టిగేషన్ ట్యాంక్, మరియు పైపుల ఏర్పాటు." },
                    { step: "4. టెస్టింగ్", desc: "సిస్టమ్ ఆన్ చేసి, చివర వరకు నీరు వస్తుందో లేదో, లీకులు ఉన్నాయో లేదో చూడాలి. ప్రెజర్ 1 kg/cm² ఉండాలి." },
                    { step: "5. నిర్వహణ", desc: "రోజూ ఫిల్టర్లు కడగాలి. పంట దశను బట్టి రోజుకు 45 నిమిషాల నుండి 2 గంటలు నడపాలి." }
                ],
                apSpecifics: {
                    soil: "అన్ని రకాల నేలలకు అనుకూలం, ముఖ్యంగా అనంతపురం/కర్నూలు ఎర్ర నేలలకు.",
                    crops: "మిరప, పత్తి, వేరుశనగ, టమాటా, అరటి, బొప్పాయి.",
                    climate: "రాయలసీమ మరియు మెట్ట ప్రాంతాలకు అత్యంత ఆవశ్యకం."
                },
                layout: "నీటి వనరు -> మోటార్ -> శాండ్ ఫిల్టర్ -> ఫెర్టిగేషన్ -> స్క్రీన్ ఫిల్టర్ -> మెయిన్ -> సబ్-మెయిన్ -> లేటరల్ -> డ్రిప్పర్",
                stats: {
                    yield: "+40-60% (వేరుశనగలో నిరూపించబడింది)",
                    water: "50-70% ఆదా (ఎకరానికి 15-20 లక్షల లీటర్లు ఆదా)",
                    cost: "₹45,000 - ₹60,000 ఎకరానికి (సబ్సిడీ పోను)"
                },
                risks: [
                    "బ్లాకేజ్ (Clogging): ఉప్పు నీటి వల్ల డ్రిప్పర్లు మూసుకుపోవడం.",
                    "ఎలుకల బెడద: లేటరల్ పైపులను ఎలుకలు కొరకడం.",
                    "ప్రారంభ ఖర్చు: సబ్సిడీ లేకపోతే ఖర్చు ఎక్కువ."
                ],
                faq: [
                    { q: "రోజుకు ఎంత సేపు డ్రిప్ వేయాలి?", a: "పంట దశ మరియు ఎండను బట్టి. సాధారణంగా రోజుకు 1-2 గంటలు." },
                    { q: "ఎలాంటి ఎరువులు వాడాలి?", a: "నీటిలో పూర్తిగా కరిగే 19:19:19, యూరియా, వైట్ పొటాష్ వాడాలి. SSP వాడకూడదు." },
                    { q: "డ్రిప్పర్లు మూసుకుపోతే ఏం చేయాలి?", a: "యాసిడ్ (Sulphuric Acid) ట్రీట్మెంట్ లేదా క్లోరిన్ వాష్ చేయాలి." }
                ],
                troubleshooting: [
                    { symptom: "చివరలో తక్కువ ప్రెజర్", cause: "లీకేజీ లేదా ఫిల్టర్ జామ్", action: "ఫిల్టర్లు శుభ్రం చేయండి, లీకులు అరికట్టండి." },
                    { symptom: "అసమానంగా నీరు పడటం", cause: "డ్రిప్పర్ల బ్లాకేజ్", action: "యాసిడ్ వాష్ చేయండి." }
                ],
                costBenefit: {
                    cost: "₹50,000 (సబ్సిడీలో ₹10k-15k)",
                    savings: "కూలీలు: ₹5000, ఎరువులు: ₹3000",
                    profit: "అదనపు దిగుబడి: ₹30,000+",
                    payback: "1-2 పంటలు"
                },
                finalGuidance: "APMIP (ఆంధ్రప్రదేశ్ సూక్ష్మ సేద్యం ప్రాజెక్ట్) ద్వారా 90% వరకు సబ్సిడీ పొందండి. ఫిల్టర్ల నిర్వహణ ముఖ్యం."
            }
        }
    },
    {
        id: 'drone-spraying',
        title: { en: 'Drone Spraying', te: 'డ్రోన్ స్ప్రేయింగ్ (Drone Spraying)' },
        image: droneSprayingImg,
        summary: { en: 'Advanced aerial spraying technology covering 1 acre in 10 minutes with 90% water saving.', te: 'కేవలం 10 నిమిషాల్లో ఒక ఎకరం మందు పిచికారీ చేసే అధునాతన డ్రోన్ టెక్నాలజీ.' },
        content: {
            en: {
                whatIsIt: "Agricultural drones (UAVs) are equipped with spray tanks and nozzles to apply pesticides and liquid fertilizers from the air. They use GPS and sensors to ensure uniform coverage and avoid overlapping.",
                whyNeedIt: "Manual spraying is labor-intensive, hazardous to health, and inefficient. Drones solve labor shortages, protect farmers from chemical exposure, and complete tasks 20x faster.",
                benefits: [
                    "Speed: Covers 1 acre in just 7-10 minutes (Manual takes 4-5 hours).",
                    "Safety: Zero direct contact with harmful chemicals for the farmer.",
                    "Water Saving: Uses Ultra Low Volume (ULV) spraying, requiring only 10L water/acre (Manual needs 150-200L).",
                    "Efficiency: Propeller downdraft pushes chemical to the underside of leaves.",
                    "Accessibility: Can spray in wet fields or tall crops (like Maize/Sugarcane) where walking is difficult."
                ],
                mistakes: [
                    "Wrong Flight Height: Flying too high causes drift; too low misses coverage (Ideal: 1.5-2m above crop).",
                    "Unfiltered Mix: Not filtering the chemical mix leads to nozzle clogging mid-flight.",
                    "Windy Conditions: Spraying when wind speed is >15 km/h leads to chemical drift to neighboring fields.",
                    "Battery Neglect: Not charging batteries fully before field visits."
                ],
                implementation: [
                    { step: "1. Field Mapping", desc: "Identify field boundaries and obstacles (trees, poles). Mark the flight path." },
                    { step: "2. Chemical Prep", desc: "Pre-mix chemical in a bucket. Filter it thoroughly before pouring into drone tank. Use anti-drift agents if needed." },
                    { step: "3. Calibration", desc: "Set flow rate and droplet size (usually 150-200 microns). Check nozzle spray pattern." },
                    { step: "4. Flight Operation", desc: "Launch drone. Monitor flight via remote controller screen. Maintain visual line of sight." },
                    { step: "5. Post-Flight", desc: "Clean tank and nozzles with fresh water immediately to prevent corrosion." }
                ],
                apSpecifics: {
                    soil: "Works on all terrains, including wet paddy fields in Godavari districts.",
                    crops: "Paddy, Maize, Sugarcane, Cotton, Chillies.",
                    climate: "Avoid spraying during high temperatures (noon) or high winds."
                },
                layout: "Remote Pilot -> Ground Station -> Drone -> Nozzles -> Crop Canopy",
                stats: {
                    yield: "Better pest control = +10-15% Yield",
                    water: "Save 90-95% (10L vs 200L)",
                    cost: "₹500 - ₹600 per acre (Service Charge)"
                },
                risks: [
                    "Drift: Chemicals affecting neighboring crops.",
                    "Technical Glitch: GPS failure or battery drain causing crash.",
                    "Regulatory: Requires DGCA certified pilot and drone."
                ],
                faq: [
                    { q: "Is it expensive?", a: "Service cost is comparable to manual labor (₹500-600/acre)." },
                    { q: "Does it kill all pests?", a: "Yes, the mist covers both sides of leaves effectively." },
                    { q: "Can I buy a drone?", a: "Yes, but it costs ₹6-10 Lakhs. Better to rent or use CHC (Custom Hiring Center)." }
                ],
                troubleshooting: [
                    { symptom: "Uneven Spray", cause: "Wind or blocked nozzle", action: "Stop, clean nozzle, wait for wind to settle." },
                    { symptom: "Drone Drifting", cause: "GPS calibration error", action: "Recalibrate compass." }
                ],
                costBenefit: {
                    cost: "₹500/acre (Rental)",
                    savings: "Health: Priceless, Time: 4 hours saved",
                    profit: "Timely intervention saves crop",
                    payback: "Immediate (Service Model)"
                },
                finalGuidance: "Book a drone service through your local RBK (Rythu Bharosa Kendra). Ensure the pilot is certified."
            },
            te: {
                whatIsIt: "వ్యవసాయ డ్రోన్లు పురుగుమందులు మరియు ద్రవ ఎరువులను గాలి నుండి పిచికారీ చేయడానికి ఉపయోగపడతాయి. ఇవి GPS మరియు సెన్సార్లను ఉపయోగించి పొలం అంతటా సమానంగా మందును చల్లుతాయి.",
                whyNeedIt: "కూలీల కొరత మరియు పురుగుమందుల ప్రభావం నుండి రైతులను రక్షించడానికి డ్రోన్లు అవసరం. ఇవి మాన్యువల్ స్ప్రేయింగ్ కంటే 20 రెట్లు వేగంగా పని చేస్తాయి.",
                benefits: [
                    "వేగం: కేవలం 7-10 నిమిషాల్లో ఒక ఎకరం స్ప్రే చేస్తుంది (మనుషులైతే 4-5 గంటలు).",
                    "ఆరోగ్య భద్రత: రైతుకు విషపూరిత మందులతో ఎటువంటి స్పర్శ ఉండదు.",
                    "నీటి ఆదా: ఎకరానికి కేవలం 10 లీటర్ల నీరు సరిపోతుంది (సాధారణ పద్ధతిలో 200 లీటర్లు కావాలి).",
                    "సామర్థ్యం: డ్రోన్ రెక్కల గాలికి మందు ఆకు అడుగు భాగంలో కూడా చేరుతుంది.",
                    "సౌలభ్యం: బురద పొలాలు లేదా ఎత్తైన పంటల్లో (మొక్కజొన్న/చెరకు) కూడా సులభంగా స్ప్రే చేయవచ్చు."
                ],
                mistakes: [
                    "ఎత్తు సరిగా లేకపోవడం: మరీ ఎత్తుగా ఎగిరితే మందు గాలికి పోతుంది, మరీ కిందకు ఎగిరితే కవరేజ్ ఉండదు (పంటకు 1.5-2 మీటర్ల ఎత్తు ఉండాలి).",
                    "వడపోయకపోవడం: మందును వడపోయకుండా ట్యాంకులో పోస్తే నాజిల్స్ మూసుకుపోతాయి.",
                    "గాలి ఉన్నప్పుడు స్ప్రే చేయడం: గాలి వేగం 15 km/h కంటే ఎక్కువ ఉంటే మందు పక్క పొలాలపై పడుతుంది.",
                    "బ్యాటరీ ఛార్జింగ్: ఫీల్డ్‌కు వెళ్లే ముందు బ్యాటరీలు ఫుల్ ఛార్జ్ చేయకపోవడం."
                ],
                implementation: [
                    { step: "1. పొలం మ్యాపింగ్", desc: "పొలం సరిహద్దులు, చెట్లు, కరెంట్ స్తంభాలను గుర్తించి డ్రోన్ ఎగిరే మార్గాన్ని సెట్ చేయాలి." },
                    { step: "2. మందు తయారీ", desc: "మందును బకెట్‌లో కలిపి, వడపోసిన తర్వాతే డ్రోన్ ట్యాంకులో పోయాలి." },
                    { step: "3. కాలిబ్రేషన్", desc: "ఎంత మందు పడాలో సెట్ చేసుకోవాలి (సాధారణంగా ఎకరానికి 10 లీటర్లు). నాజిల్స్ సరిగా పనిచేస్తున్నాయో లేదో చూడాలి." },
                    { step: "4. ఆపరేషన్", desc: "డ్రోన్‌ను ఎగురవేయాలి. రిమోట్ స్క్రీన్‌లో గమనిస్తూ ఉండాలి." },
                    { step: "5. శుభ్రం చేయడం", desc: "పని పూర్తయ్యాక ట్యాంక్ మరియు నాజిల్స్ మంచినీటితో కడగాలి." }
                ],
                apSpecifics: {
                    soil: "అన్ని రకాల నేలలకు, ముఖ్యంగా గోదావరి జిల్లాల్లోని వరి పొలాలకు చాలా ఉపయోగకరం.",
                    crops: "వరి, మొక్కజొన్న, చెరకు, పత్తి, మిరప.",
                    climate: "ఎక్కువ ఎండ లేదా గాలి ఉన్నప్పుడు స్ప్రే చేయకూడదు."
                },
                layout: "పైలట్ -> గ్రౌండ్ స్టేషన్ -> డ్రోన్ -> నాజిల్స్ -> పంట",
                stats: {
                    yield: "పురుగుల నివారణ బాగుంటుంది = +10-15% దిగుబడి",
                    water: "90-95% ఆదా (10 లీటర్లు vs 200 లీటర్లు)",
                    cost: "₹500 - ₹600 ఎకరానికి (సర్వీస్ ఛార్జీ)"
                },
                risks: [
                    "డ్రిఫ్ట్ (Drift): గాలికి మందు పక్క పొలాలపై పడటం.",
                    "సాంకేతిక సమస్యలు: GPS పనిచేయకపోవడం లేదా బ్యాటరీ అయిపోవడం.",
                    "నిబంధనలు: డ్రోన్ నడపడానికి లైసెన్స్ మరియు శిక్షణ అవసరం."
                ],
                faq: [
                    { q: "ఖర్చు ఎంత అవుతుంది?", a: "కూలీల ఖర్చుతో సమానమే (₹500-600/ఎకరం)." },
                    { q: "పురుగులు చనిపోతాయా?", a: "అవును, డ్రోన్ గాలి ఒత్తిడికి మందు ఆకు వెనుక కూడా చేరుతుంది." },
                    { q: "డ్రోన్ కొనాలా?", a: "అవసరం లేదు, అద్దెకు తీసుకోవచ్చు లేదా RBK ద్వారా బుక్ చేసుకోవచ్చు." }
                ],
                troubleshooting: [
                    { symptom: "సరిగా పడకపోవడం", cause: "నాజిల్ బ్లాక్ లేదా గాలి", action: "నాజిల్ క్లీన్ చేయాలి, గాలి తగ్గే వరకు ఆగాలి." },
                    { symptom: "డ్రోన్ పక్కకు వెళ్లడం", cause: "GPS సమస్య", action: "కాలిబ్రేషన్ చేయాలి." }
                ],
                costBenefit: {
                    cost: "₹500/ఎకరం (అద్దె)",
                    savings: "ఆరోగ్యం: వెలకట్టలేనిది, సమయం: 4 గంటలు ఆదా",
                    profit: "సకాలంలో మందు కొట్టడం వల్ల పంట రక్షణ",
                    payback: "వెంటనే (సర్వీస్ మోడల్)"
                },
                finalGuidance: "మీ దగ్గర్లోని RBK (రైతు భరోసా కేంద్రం) ద్వారా డ్రోన్ సర్వీస్ బుక్ చేసుకోండి."
            }
        }
    },
    {
        id: 'soil-testing',
        title: { en: 'Soil Testing', te: 'భూసార పరీక్ష (Soil Testing)' },
        image: soilTestingImg,
        summary: { en: 'Scientific analysis of soil health to optimize fertilizer use and boost yield by 15%.', te: 'నేల ఆరోగ్యాన్ని శాస్త్రీయంగా పరీక్షించి, ఎరువుల ఖర్చు తగ్గించి, దిగుబడిని 15% పెంచే విధానం.' },
        content: {
            en: {
                whatIsIt: "Soil testing is a comprehensive chemical analysis that determines the nutrient content (N, P, K, etc.), composition, and pH level of the soil. It acts as a 'health report card' for the farm.",
                whyNeedIt: "Farmers often apply excess Urea/DAP without knowing what the soil actually needs. This damages soil health, increases cost, and reduces yield. Testing ensures balanced nutrition.",
                benefits: [
                    "Cost Saving: Avoids unnecessary fertilizer application (Save ₹2000-3000/acre).",
                    "Yield Boost: Correct nutrient balance improves crop growth and grain filling (+15-20% yield).",
                    "Soil Health: Prevents soil acidity/alkalinity and preserves microbial life.",
                    "Disease Resistance: Balanced nutrition makes crops stronger against pests and diseases."
                ],
                mistakes: [
                    "Wrong Sampling: Taking soil only from the surface or near bunds/trees.",
                    "Mixing Samples: Mixing samples from different soil types or fields.",
                    "Wet Soil: Collecting samples when the soil is too wet or immediately after fertilizing.",
                    "Delay: Testing after sowing instead of before."
                ],
                implementation: [
                    { step: "1. Sampling Time", desc: "Best time is summer (April-May) or after harvest, before sowing next crop." },
                    { step: "2. Digging", desc: "Remove surface litter. Dig a 'V' shaped pit 15cm deep (6 inches) using a spade." },
                    { step: "3. Collection", desc: "Slice a 1-inch thick layer from top to bottom of the 'V' pit. Collect this in a clean bucket." },
                    { step: "4. Composite Sample", desc: "Repeat this at 8-10 spots in a zig-zag pattern across the field. Mix all soil in the bucket." },
                    { step: "5. Quartering", desc: "Spread soil on paper, divide into 4 parts, discard opposite 2 parts. Repeat until 500g remains. Pack in a cloth bag with details." }
                ],
                apSpecifics: {
                    soil: "Essential for all AP soils. Coastal soils often need Zinc; Rayalaseema soils need Organic Carbon.",
                    crops: "Mandatory for high-input crops like Paddy, Cotton, Chillies, Maize.",
                    climate: "Perform test before Monsoon onset."
                },
                layout: "Zig-Zag Pattern across the field (avoiding shade/bunds)",
                stats: {
                    yield: "+15-20% (Due to balanced nutrition)",
                    water: "N/A (Indirectly improves water use efficiency)",
                    cost: "₹100-300 (Free in some Govt Labs)"
                },
                risks: [
                    "Inaccurate Report: If sampling is done wrongly, the report will be misleading.",
                    "Lab Delay: Reports taking too long (plan 1 month ahead)."
                ],
                faq: [
                    { q: "How often should I test?", a: "Once every 2-3 years. If growing vegetables, every year." },
                    { q: "Where to give the sample?", a: "Nearest Rythu Bharosa Kendra (RBK) or Agriculture Lab." },
                    { q: "What details to write on bag?", a: "Farmer Name, Survey No, Crop planned, Previous crop." }
                ],
                troubleshooting: [
                    { symptom: "High pH (>8.5)", cause: "Alkaline soil", action: "Apply Gypsum as per report." },
                    { symptom: "Low pH (<6.0)", cause: "Acidic soil", action: "Apply Lime." }
                ],
                costBenefit: {
                    cost: "₹100 (Lab fee)",
                    savings: "Fertilizer: ₹2500/acre",
                    profit: "Yield: ₹5000+",
                    payback: "Immediate (First Crop)"
                },
                finalGuidance: "Don't guess, Test! Submit sample to your Village Agriculture Assistant (VAA) at RBK."
            },
            te: {
                whatIsIt: "భూసార పరీక్ష అనేది నేలలోని పోషకాలు (నత్రజని, భాస్వరం, పొటాష్ మొదలైనవి), ఉదజని సూచిక (pH) మరియు లవణ సూచిక (EC) లను తెలుసుకునే శాస్త్రీయ పద్ధతి. ఇది మీ పొలానికి 'హెల్త్ రిపోర్ట్' లాంటిది.",
                whyNeedIt: "చాలా మంది రైతులు నేలకు ఏం కావాలో తెలియక విపరీతంగా యూరియా, డి.ఎ.పి వాడుతున్నారు. దీనివల్ల ఖర్చు పెరుగుతుంది, నేల పాడవుతుంది. పరీక్ష చేస్తే ఎంత వేయాలో అంతే వేయవచ్చు.",
                benefits: [
                    "ఖర్చు ఆదా: అనవసరమైన ఎరువులు కొనాల్సిన పనిలేదు (ఎకరానికి ₹2000-3000 ఆదా).",
                    "దిగుబడి పెరుగుదల: సరైన పోషకాలు అందడం వల్ల పంట ఏపుగా పెరిగి 15-20% ఎక్కువ దిగుబడి వస్తుంది.",
                    "నేల ఆరోగ్యం: నేల చౌడు బారకుండా లేదా ఆమ్లంగా మారకుండా కాపాడుకోవచ్చు.",
                    "చీడపీడల నివారణ: బలమైన మొక్కలకు రోగనిరోధక శక్తి ఎక్కువ."
                ],
                mistakes: [
                    "తప్పుగా తీయడం: గట్ల దగ్గర, చెట్ల కింద, లేదా ఎరువుల కుప్పల దగ్గర మట్టి తీయడం.",
                    "కలపడం: వేర్వేరు పొలాల మట్టిని లేదా వేర్వేరు నేల రకాల మట్టిని కలపడం.",
                    "తడి మట్టి: మట్టి బాగా తడిగా ఉన్నప్పుడు తీయడం.",
                    "ఆలస్యం: విత్తనాలు వేసాక పరీక్ష చేయడం (విత్తే ముందే చేయాలి)."
                ],
                implementation: [
                    { step: "1. సమయం", desc: "వేసవిలో (ఏప్రిల్-మే) లేదా పంట కోత తర్వాత, తదుపరి పంటకు ముందు చేయడం ఉత్తమం." },
                    { step: "2. గుంత తీయడం", desc: "పొలంలో పైన ఉన్న చెత్తను తీసివేసి, పారతో 'V' ఆకారంలో 15 సెం.మీ (6 అంగుళాలు) లోతు గుంత తీయాలి." },
                    { step: "3. మట్టి సేకరణ", desc: "గుంత పై నుండి కింద వరకు ఒక పొరలాగా (1 అంగుళం మందం) మట్టిని చెక్కి, శుభ్రమైన ప్లాస్టిక్ బకెట్‌లో వేయాలి." },
                    { step: "4. మిశ్రమ నమూనా", desc: "ఇలా పొలం అంతటా జిగ్-జాగ్ పద్ధతిలో 8-10 చోట్ల తీసి, బకెట్‌లో బాగా కలపాలి." },
                    { step: "5. క్వార్టరింగ్", desc: "మట్టిని పేపర్‌పై పరచి 4 భాగాలు చేయాలి. ఎదురెదురు భాగాలు తీసేసి, మిగిలినవి కలపాలి. ఇలా అరకిలో మట్టి మిగిలే వరకు చేయాలి. దీనిని గుడ్డ సంచిలో కట్టి వివరాలు రాయాలి." }
                ],
                apSpecifics: {
                    soil: "అన్ని రకాల నేలలకు అవసరం. కోస్తాలో జింక్ లోపం, రాయలసీమలో సేంద్రియ కర్బనం లోపం ఎక్కువ.",
                    crops: "వరి, పత్తి, మిరప, మొక్కజొన్న వంటి అధిక పెట్టుబడి పంటలకు తప్పనిసరి.",
                    climate: "తొలకరి వర్షాలకు ముందే పరీక్ష చేయించుకోవాలి."
                },
                layout: "పొలం అంతటా జిగ్-జాగ్ (Zig-Zag) పద్ధతిలో",
                stats: {
                    yield: "+15-20% (సమతుల్య పోషకాల వల్ల)",
                    water: "వర్తించదు",
                    cost: "₹100-300 (ప్రభుత్వ ల్యాబ్‌లో ఉచితం)"
                },
                risks: [
                    "తప్పు రిపోర్ట్: మట్టి సరిగా తీయకపోతే రిపోర్ట్ తప్పు వస్తుంది.",
                    "ఆలస్యం: రిపోర్ట్ రావడానికి టైమ్ పట్టొచ్చు (నెల ముందే ప్లాన్ చేయాలి)."
                ],
                faq: [
                    { q: "ఎన్ని రోజులకు ఒకసారి చేయాలి?", a: "2-3 ఏళ్లకు ఒకసారి. కూరగాయలైతే ప్రతి ఏటా." },
                    { q: "మట్టిని ఎక్కడ ఇవ్వాలి?", a: "మీ దగ్గర్లోని రైతు భరోసా కేంద్రం (RBK) లేదా వ్యవసాయ ల్యాబ్." },
                    { q: "సంచిపై ఏం రాయాలి?", a: "రైతు పేరు, సర్వే నెంబర్, వేయబోయే పంట, గత పంట వివరాలు." }
                ],
                troubleshooting: [
                    { symptom: "pH > 8.5 (క్షార నేల)", cause: "సోడియం ఎక్కువ", action: "జిప్సం వేయాలి." },
                    { symptom: "pH < 6.0 (ఆమ్ల నేల)", cause: "ఆమ్ల గుణం", action: "సున్నం (Lime) వేయాలి." }
                ],
                costBenefit: {
                    cost: "₹100 (ఫీజు)",
                    savings: "ఎరువులు: ₹2500/ఎకరం",
                    profit: "దిగుబడి: ₹5000+",
                    payback: "వెంటనే (మొదటి పంటలోనే)"
                },
                finalGuidance: "అంచనాలతో వ్యవసాయం వద్దు, పరీక్షతోనే ముద్దు! మీ నమూనాను VAA (గ్రామ వ్యవసాయ సహాయకుడు) కి ఇవ్వండి."
            }
        }
    },
    {
        id: 'zbnf',
        title: { en: 'Zero Budget Natural Farming', te: 'పెట్టుబడి లేని ప్రకృతి వ్యవసాయం (ZBNF)' },
        image: zbnfImg,
        summary: { en: 'A holistic farming method using nature\'s principles to eliminate chemical costs and restore soil fertility.', te: 'రసాయన ఖర్చులను పూర్తిగా తగ్గించి, ప్రకృతి సిద్ధాంతాలతో నేల సారాన్ని పెంచే అద్భుత విధానం.' },
        content: {
            en: {
                whatIsIt: "Zero Budget Natural Farming (ZBNF), now often called Andhra Pradesh Community Managed Natural Farming (APCNF), is a set of farming methods that involve zero credit and no use of chemical fertilizers. It relies on 4 pillars: Jeevamrutham, Bijamrutham, Acchadana (Mulching), and Whapasa (Moisture).",
                whyNeedIt: "Farmers are trapped in a debt cycle due to high input costs (seeds, fertilizers, pesticides). ZBNF breaks this cycle by using locally available inputs (cow dung/urine), making farming profitable and sustainable.",
                benefits: [
                    "Zero Input Cost: No need to buy expensive chemicals; inputs are homemade.",
                    "Healthier Food: Produce is free from toxic residues, fetching premium prices.",
                    "Soil Restoration: Earthworm activity increases, making soil soft and porous.",
                    "Climate Resilience: ZBNF crops withstand drought and heavy rains better than chemical crops.",
                    "Water Saving: Requires 10% less water due to mulching and humus formation."
                ],
                mistakes: [
                    "Using Jersey Cow Dung: Only Desi (Indigenous) cow dung should be used as it has more beneficial microbes.",
                    "Fresh Dung Usage: Using fresh dung directly can cause heat; it must be fermented.",
                    "Lack of Patience: Expecting immediate high yields in the first season (yield may dip slightly initially).",
                    "Ignoring Mulching: Without mulching, soil microbes cannot survive."
                ],
                implementation: [
                    { step: "1. Bijamrutham (Seed Treatment)", desc: "Treat seeds with a mix of cow dung, urine, lime, and soil to protect from fungal diseases." },
                    { step: "2. Jeevamrutham Prep", desc: "Mix 10kg Desi cow dung + 10L urine + 2kg Jaggery + 2kg Pulse flour + Handful of soil in 200L water. Ferment for 48 hours in shade." },
                    { step: "3. Application", desc: "Apply Jeevamrutham with irrigation water (200L/acre) every 15 days. Or spray filtered Jeevamrutham." },
                    { step: "4. Acchadana (Mulching)", desc: "Cover soil with crop residue or live mulch (intercrops) to retain moisture." },
                    { step: "5. Pest Management", desc: "Use Neemasthram, Agniasthram, or Brahmastra for pest control." }
                ],
                apSpecifics: {
                    soil: "Works on all soils. Highly successful in drought-prone Anantapur and tribal areas of Vizag.",
                    crops: "Paddy, Groundnut, Coffee, Cashew, Mango, Vegetables.",
                    climate: "Suitable for all agro-climatic zones of AP."
                },
                layout: "5-Layer Models (Pre-monsoon dry sowing) are popular.",
                stats: {
                    yield: "Sustainable long-term (+10-20% after 3 years)",
                    water: "Save 10-20%",
                    cost: "Near Zero (Only labor)"
                },
                risks: [
                    "Initial Yield Dip: Yield might drop by 10-15% in the first year during transition.",
                    "Labor Intensive: Preparation of inputs requires regular manual effort."
                ],
                faq: [
                    { q: "Can I use Buffalo dung?", a: "Desi Cow dung is best (millions of microbes). Buffalo is second best." },
                    { q: "Does it work for Paddy?", a: "Yes, SRI + ZBNF gives excellent results." },
                    { q: "Where to sell?", a: "High demand for 'Natural/Organic' produce in cities." }
                ],
                troubleshooting: [
                    { symptom: "Yellowing Leaves", cause: "Nitrogen deficiency initially", action: "Spray Jeevamrutham weekly." },
                    { symptom: "Pest Attack", cause: "Imbalance", action: "Spray Agniasthram or Dashaparni Kashayam." }
                ],
                costBenefit: {
                    cost: "₹2000-3000 (Jaggery/Flour)",
                    savings: "₹15,000-20,000 (Chemicals)",
                    profit: "Premium Price + Low Cost",
                    payback: "1 Year"
                },
                finalGuidance: "Join a local Rythu Sadhikara Samstha (RySS) SHG group for training and support."
            },
            te: {
                whatIsIt: "పెట్టుబడి లేని ప్రకృతి వ్యవసాయం (ZBNF), దీనినే ఇప్పుడు APCNF అని కూడా పిలుస్తున్నారు. ఇది రసాయన ఎరువులు లేకుండా, కేవలం ప్రకృతి వనరులతో చేసే సాగు. ఇది 4 స్తంభాలపై ఆధారపడి ఉంటుంది: బీజామృతం, జీవామృతం, ఆచ్ఛాదన (మల్చింగ్), మరియు వాఫసా (తేమ).",
                whyNeedIt: "విత్తనాలు, ఎరువులు, పురుగుమందుల ఖర్చులతో రైతులు అప్పుల పాలవుతున్నారు. ZBNF ఈ ఖర్చులను సున్నా చేసి, స్థానికంగా దొరికే ఆవు పేడ/మూత్రంతో వ్యవసాయాన్ని లాభసాటిగా మారుస్తుంది.",
                benefits: [
                    "సున్నా పెట్టుబడి: ఖరీదైన మందులు కొనక్కర్లేదు; అన్నీ ఇంట్లోనే తయారు చేసుకోవచ్చు.",
                    "ఆరోగ్యకరమైన ఆహారం: విష రసాయనాలు లేని పంట, మార్కెట్లో మంచి ధరకు అమ్ముడుపోతుంది.",
                    "నేల పునరుజ్జీవం: వానపాములు పెరిగి, నేల గుల్లగా, సారవంతంగా మారుతుంది.",
                    "వాతావరణ తట్టుకునే శక్తి: కరువును, అతివృష్టిని రసాయన పంటల కంటే బాగా తట్టుకుంటుంది.",
                    "నీటి ఆదా: మల్చింగ్ వల్ల 10% తక్కువ నీరు అవసరం."
                ],
                mistakes: [
                    "జెర్సీ ఆవు పేడ వాడకం: దేశవాళీ ఆవు పేడలోనే కోట్లాది సూక్ష్మజీవులు ఉంటాయి. జెర్సీ పనికిరాదు.",
                    "తాజా పేడ వాడకం: తాజా పేడ వేడిని పుట్టిస్తుంది. దానిని పులియబెట్టాలి.",
                    "ఓపిక లేకపోవడం: మొదటి ఏడాదే అద్భుతాలు ఆశించడం (మొదట్లో దిగుబడి కొంచెం తగ్గవచ్చు).",
                    "మల్చింగ్ చేయకపోవడం: మల్చింగ్ లేకపోతే సూక్ష్మజీవులు బతకలేవు."
                ],
                implementation: [
                    { step: "1. బీజామృతం (విత్తన శుద్ధి)", desc: "ఆవు పేడ, మూత్రం, సున్నం, పుట్ట మన్ను మిశ్రమంతో విత్తనాలను శుద్ధి చేయాలి. ఇది శిలీంధ్రాల నుండి కాపాడుతుంది." },
                    { step: "2. జీవామృతం తయారీ", desc: "10kg ఆవు పేడ + 10L మూత్రం + 2kg బెల్లం + 2kg పప్పు ధాన్యాల పిండి + పిడికెడు పుట్ట మన్ను 200L నీటిలో కలపాలి. 48 గంటలు నీడలో పులియబెట్టాలి." },
                    { step: "3. వాడకం", desc: "ఎకరానికి 200 లీటర్ల జీవామృతాన్ని నీటితో పాటు 15 రోజులకోసారి ఇవ్వాలి. లేదా వడపోసి పిచికారీ చేయాలి." },
                    { step: "4. ఆచ్ఛాదన (Mulching)", desc: "పంట వ్యర్థాలతో లేదా అంతర పంటలతో నేలను కప్పి ఉంచాలి." },
                    { step: "5. కషాయాలు", desc: "చీడపీడలకు నీమాస్త్రం, అగ్నిఅస్త్రం, లేదా బ్రహ్మాస్త్రం వాడాలి." }
                ],
                apSpecifics: {
                    soil: "అన్ని నేలలకు అనుకూలం. అనంతపురం కరువు ప్రాంతాల్లో మరియు విశాఖ మన్యం ప్రాంతాల్లో అద్భుత ఫలితాలు.",
                    crops: "వరి, వేరుశనగ, కాఫీ, జీడిమామిడి, మామిడి, కూరగాయలు.",
                    climate: "AP లోని అన్ని వాతావరణ మండలాలకు అనుకూలం."
                },
                layout: "5-అంచెల నమూనా (5-Layer Model) మరియు PMDS (ప్రీ-మాన్సూన్ డ్రై సోయింగ్) ప్రసిద్ధం.",
                stats: {
                    yield: "దీర్ఘకాలికంగా పెరుగుతుంది (3 ఏళ్ల తర్వాత +10-20%)",
                    water: "10-20% ఆదా",
                    cost: "దాదాపు సున్నా (కూలీలు తప్ప)"
                },
                risks: [
                    "ప్రారంభ దిగుబడి తగ్గుదల: రసాయనాల నుండి మారిన మొదటి ఏడాది 10-15% దిగుబడి తగ్గవచ్చు.",
                    "శ్రమ ఎక్కువ: కషాయాలు, జీవామృతం తయారీకి రెగ్యులర్ గా పని చేయాలి."
                ],
                faq: [
                    { q: "గేదె పేడ వాడవచ్చా?", a: "దేశవాళీ ఆవు పేడ శ్రేష్టం. లేకపోతే గేదె పేడ వాడవచ్చు కానీ ఫలితం తక్కువ." },
                    { q: "వరికి పనిచేస్తుందా?", a: "అవును, SRI పద్ధతిలో ZBNF చేస్తే మంచి ఫలితాలు ఉంటాయి." },
                    { q: "ఎక్కడ అమ్మాలి?", a: "నగరాల్లో 'నేచురల్/ఆర్గానిక్' పంటలకు మంచి డిమాండ్ ఉంది." }
                ],
                troubleshooting: [
                    { symptom: "ఆకులు పసుపు రంగు", cause: "నైట్రోజన్ అందక (మొదట్లో)", action: "వారానికి ఒకసారి జీవామృతం పిచికారీ చేయాలి." },
                    { symptom: "పురుగు దాడి", cause: "అసమతుల్యత", action: "అగ్నిఅస్త్రం లేదా దశపర్ణి కషాయం కొట్టాలి." }
                ],
                costBenefit: {
                    cost: "₹2000-3000 (బెల్లం/పిండి)",
                    savings: "₹15,000-20,000 (రసాయనాలు)",
                    profit: "ప్రీమియం ధర + తక్కువ ఖర్చు",
                    payback: "1 సంవత్సరం"
                },
                finalGuidance: "RySS (రైతు సాధికార సంస్థ) వారి స్థానిక SHG గ్రూపులో చేరి శిక్షణ తీసుకోండి."
            }
        }
    },
    {
        id: 'sri-paddy',
        title: { en: 'SRI Paddy Cultivation', te: 'శ్రీ వరి సాగు (SRI Method)' },
        image: sriPaddyImg,
        summary: { en: 'More rice with less water.', te: 'తక్కువ నీటితో ఎక్కువ వరి.' },
        content: {
            en: {
                whatIsIt: "System of Rice Intensification - planting single seedlings with wide spacing.",
                whyNeedIt: "Save water and seed cost.",
                benefits: ["Seed: 2kg/acre vs 25kg", "Water: 30-50% saving"],
                mistakes: ["Old seedlings", "Flooding field"],
                implementation: [{ step: "1. Nursery", desc: "Raise on raised beds." }, { step: "2. Transplant", desc: "8-12 day old seedlings." }],
                apSpecifics: { soil: "Clay/Loam", crops: "Paddy", climate: "Godavari/Krishna" },
                layout: "Grid (25x25cm)",
                stats: { yield: "+20-30%", water: "-40%", cost: "Low seed cost" },
                risks: ["Labor skill"],
                faq: [{ q: "Why young seedlings?", a: "More tillers." }],
                troubleshooting: [{ symptom: "Weeds", cause: "No water", action: "Conoweeder" }],
                costBenefit: { cost: "Labor", savings: "Seed/Water", profit: "High yield", payback: "1 Season" },
                finalGuidance: "Use Conoweeder for aeration."
            },
            te: {
                whatIsIt: "శ్రీ వరి సాగు - వెడల్పు దూరంతో ఒక్కొక్క మొక్కను నాటడం.",
                whyNeedIt: "నీరు మరియు విత్తన ఖర్చు ఆదా.",
                benefits: ["విత్తనం: 2kg/ఎకరం vs 25kg", "నీరు: 30-50% ఆదా"],
                mistakes: ["ముదురు నారు", "పొలం నింపడం"],
                implementation: [{ step: "1. నారుమడి", desc: "ఎత్తైన మడులపై పెంచండి." }, { step: "2. నాటడం", desc: "8-12 రోజుల నారు." }],
                apSpecifics: { soil: "బంకమట్టి/లోమ్", crops: "వరి", climate: "గోదావరి/కృష్ణా" },
                layout: "గ్రిడ్ (25x25cm)",
                stats: { yield: "+20-30%", water: "-40%", cost: "తక్కువ విత్తన ఖర్చు" },
                risks: ["కూలీల నైపుణ్యం"],
                faq: [{ q: "లేత నారు ఎందుకు?", a: "ఎక్కువ పిలకలు వస్తాయి." }],
                troubleshooting: [{ symptom: "కలుపు", cause: "నీరు లేకపోవడం", action: "కోనోవీడర్" }],
                costBenefit: { cost: "కూలీలు", savings: "విత్తనం/నీరు", profit: "అధిక దిగుబడి", payback: "1 పంట" },
                finalGuidance: "గాలి కోసం కోనోవీడర్ వాడండి."
            }
        }
    },
    {
        id: 'solar-pumps',
        title: { en: 'Solar Pumps', te: 'సోలార్ పంపులు (Solar Pumps)' },
        image: solarPumpImg,
        summary: { en: 'Free electricity for irrigation.', te: 'సాగునీటి కోసం ఉచిత విద్యుత్.' },
        content: {
            en: {
                whatIsIt: "Photovoltaic systems that pump water using solar energy, eliminating fuel costs.",
                whyNeedIt: "To overcome irregular power supply and high diesel costs.",
                benefits: ["Zero running cost", "Daytime irrigation", "Low maintenance", "Eco-friendly"],
                mistakes: ["Shadow on panels", "Wrong pump sizing", "Ignoring cleaning"],
                implementation: [
                    { step: "1. Site Selection", desc: "Shadow-free area, close to water source." },
                    { step: "2. Installation", desc: "Mount panels facing True South." },
                    { step: "3. Maintenance", desc: "Clean panels weekly." }
                ],
                apSpecifics: { soil: "All types", crops: "All crops", climate: "High solar irradiance districts" },
                layout: "South-facing, 25-30 degree tilt",
                stats: { yield: "Timely irrigation", water: "N/A", cost: "One-time investment" },
                risks: ["Theft of panels", "Cloudy days"],
                faq: [{ q: "Does it work at night?", a: "No, unless battery backup is added (expensive)." }],
                troubleshooting: [{ symptom: "Low water flow", cause: "Dusty panels", action: "Clean with water and soft cloth." }],
                costBenefit: { cost: "₹1-2 Lakhs (Subsidized)", savings: "₹50k/year (Diesel)", profit: "Energy independence", payback: "3-4 Years" },
                finalGuidance: "Apply for PM-KUSUM scheme for subsidies."
            },
            te: {
                whatIsIt: "సౌర శక్తిని ఉపయోగించి నీటిని తోడే పంపులు.",
                whyNeedIt: "కరెంట్ కోతలు మరియు డీజిల్ ఖర్చు తగ్గించడానికి.",
                benefits: ["కరెంట్ బిల్లు సున్నా", "పగటి పూట సాగునీరు", "తక్కువ నిర్వహణ", "పర్యావరణ హితం"],
                mistakes: ["ప్యానెల్స్ పై నీడ పడటం", "తప్పుడు పంపు ఎంపిక", "శుభ్రం చేయకపోవడం"],
                implementation: [
                    { step: "1. స్థల ఎంపిక", desc: "నీడ లేని, నీటి వనరు దగ్గర." },
                    { step: "2. ఏర్పాటు", desc: "ప్యానెల్స్ దక్షిణం వైపు ఉండేలా చూడాలి." },
                    { step: "3. నిర్వహణ", desc: "వారానికి ఒకసారి శుభ్రం చేయాలి." }
                ],
                apSpecifics: { soil: "అన్ని రకాలు", crops: "అన్ని పంటలు", climate: "ఎండ ఎక్కువగా ఉండే జిల్లాలు" },
                layout: "దక్షిణం వైపు, 25-30 డిగ్రీల వంపు",
                stats: { yield: "సకాలంలో నీరు", water: "వర్తించదు", cost: "ఒకసారి పెట్టుబడి" },
                risks: ["దొంగతనం", "మబ్బు రోజులు"],
                faq: [{ q: "రాత్రి పూట పనిచేస్తుందా?", a: "లేదు, బ్యాటరీ ఉంటేనే (ఖర్చు ఎక్కువ)." }],
                troubleshooting: [{ symptom: "నీరు తక్కువ రావడం", cause: "దుమ్ము", action: "నీటితో శుభ్రం చేయండి." }],
                costBenefit: { cost: "₹1-2 లక్షలు (సబ్సిడీ)", savings: "₹50వేలు/ఏడాది", profit: "కరెంట్ కష్టాలు ఉండవు", payback: "3-4 ఏళ్లు" },
                finalGuidance: "PM-KUSUM పథకం ద్వారా సబ్సిడీ పొందండి."
            }
        }
    },
    {
        id: 'mulching',
        title: { en: 'Mulching', te: 'మల్చింగ్ (Mulching)' },
        image: mulchingImg,
        summary: { en: 'Cover soil to save water and stop weeds.', te: 'నీటిని ఆదా చేయడానికి మరియు కలుపును ఆపడానికి నేలను కప్పడం.' },
        content: {
            en: {
                whatIsIt: "Covering soil with plastic film or organic matter to conserve moisture.",
                whyNeedIt: "To suppress weeds and reduce water evaporation.",
                benefits: ["Water saving: 30-50%", "Weed control: 90%", "Temperature regulation", "Prevents soil erosion"],
                mistakes: ["Using thin plastic", "Loose laying", "Burning used plastic"],
                implementation: [
                    { step: "1. Bed Prep", desc: "Prepare raised beds with drip lines." },
                    { step: "2. Laying", desc: "Stretch mulch film tight over beds." },
                    { step: "3. Planting", desc: "Punch holes using heated pipe." }
                ],
                apSpecifics: { soil: "Red/Sandy soils", crops: "Chilli, Tomato, Papaya", climate: "Rayalaseema" },
                layout: "Raised beds covered with silver/black film",
                stats: { yield: "+20-25%", water: "-40%", cost: "₹12,000/acre" },
                risks: ["Plastic disposal", "Initial cost"],
                faq: [{ q: "Which color to use?", a: "Silver-black is best for most crops." }],
                troubleshooting: [{ symptom: "Film tearing", cause: "Loose laying/Wind", action: "Cover edges with more soil." }],
                costBenefit: { cost: "₹12k-15k/acre", savings: "₹10k (Weeding labor)", profit: "Higher yield quality", payback: "1 Season" },
                finalGuidance: "Dispose of plastic responsibly after harvest."
            },
            te: {
                whatIsIt: "ప్లాస్టిక్ కవర్ లేదా ఆకులతో నేలను కప్పే పద్ధతి.",
                whyNeedIt: "కలుపు నివారణకు మరియు తేమను కాపాడటానికి.",
                benefits: ["నీటి ఆదా: 30-50%", "కలుపు నివారణ: 90%", "నేల ఉష్ణోగ్రత నియంత్రణ", "నేల కోత నివారణ"],
                mistakes: ["పల్చని ప్లాస్టిక్ వాడకం", "వదులుగా వేయడం", "ప్లాస్టిక్ కాల్చడం"],
                implementation: [
                    { step: "1. బెడ్ తయారీ", desc: "డ్రిప్ లైన్లతో ఎత్తైన బెడ్లు చేయాలి." },
                    { step: "2. పరచడం", desc: "మల్చింగ్ షీట్ ను గట్టిగా పరచాలి." },
                    { step: "3. నాటడం", desc: "వేడి పైపుతో రంధ్రాలు చేయాలి." }
                ],
                apSpecifics: { soil: "ఎర్ర/ఇసుక నేలలు", crops: "మిరప, టమాటా, బొప్పాయి", climate: "రాయలసీమ" },
                layout: "ఎత్తైన బెడ్లపై సిల్వర్/బ్లాక్ షీట్",
                stats: { yield: "+20-25%", water: "-40%", cost: "₹12,000/ఎకరం" },
                risks: ["ప్లాస్టిక్ వ్యర్థాలు", "మొదటి ఖర్చు"],
                faq: [{ q: "ఏ రంగు వాడాలి?", a: "సిల్వర్-బ్లాక్ చాలా పంటలకు మంచిది." }],
                troubleshooting: [{ symptom: "షీట్ చిరగడం", cause: "గాలి/వదులు", action: "అంచులపై మట్టి వేయండి." }],
                costBenefit: { cost: "₹12k-15k/ఎకరం", savings: "₹10k (కలుపు కూలీలు)", profit: "నాణ్యమైన పంట", payback: "1 పంట" },
                finalGuidance: "పంట తర్వాత ప్లాస్టిక్ ను జాగ్రత్తగా తొలగించండి."
            }
        }
    },
    {
        id: 'laser-leveling',
        title: { en: 'Laser Land Leveling', te: 'లేజర్ ల్యాండ్ లెవలింగ్' },
        image: laserLevelingImg,
        summary: { en: 'Perfectly flat land for even water distribution.', te: 'సమాన నీటి పంపిణీ కోసం చదునైన భూమి.' },
        content: {
            en: {
                whatIsIt: "Precision land leveling using laser-equipped drag buckets.",
                whyNeedIt: "To ensure uniform water distribution and crop growth.",
                benefits: ["Water saving: 20-30%", "Uniform germination", "Increased cultivable area", "Reduced weed problems"],
                mistakes: ["Leveling when wet", "Deep cuts exposing subsoil"],
                implementation: [
                    { step: "1. Survey", desc: "Topographic survey of the field." },
                    { step: "2. Setup", desc: "Install laser transmitter and receiver." },
                    { step: "3. Leveling", desc: "Drive tractor in circular motion." }
                ],
                apSpecifics: { soil: "All types", crops: "Paddy, Wheat", climate: "Delta regions" },
                layout: "Perfectly flat field",
                stats: { yield: "+10-15%", water: "-25%", cost: "₹600-800/hour" },
                risks: ["Topsoil disturbance (if too deep)"],
                faq: [{ q: "How often to do?", a: "Once every 3-4 years." }],
                troubleshooting: [{ symptom: "Water stagnation", cause: "Improper leveling", action: "Re-check levels." }],
                costBenefit: { cost: "₹3000-4000/acre", savings: "Water/Labor", profit: "Uniform crop", payback: "1-2 Seasons" },
                finalGuidance: "Best done during summer before paddy season."
            },
            te: {
                whatIsIt: "లేజర్ పరికరంతో భూమిని సమానంగా చదును చేయడం.",
                whyNeedIt: "నీరు సమానంగా పారడానికి మరియు పంట పెరుగుదలకు.",
                benefits: ["నీటి ఆదా: 20-30%", "సమాన మొలకలు", "సాగు విస్తీర్ణం పెరుగుదల", "కలుపు సమస్య తగ్గుదల"],
                mistakes: ["తడి నేలలో చేయడం", "ఎక్కువ లోతు తీయడం"],
                implementation: [
                    { step: "1. సర్వే", desc: "పొలం ఎత్తుపల్లాల గుర్తింపు." },
                    { step: "2. అమరిక", desc: "లేజర్ పరికరాల ఏర్పాటు." },
                    { step: "3. చదును", desc: "ట్రాక్టర్ తో మట్టిని సమానం చేయడం." }
                ],
                apSpecifics: { soil: "అన్ని రకాలు", crops: "వరి, గోధుమ", climate: "డెల్టా ప్రాంతాలు" },
                layout: "పూర్తిగా చదునైన పొలం",
                stats: { yield: "+10-15%", water: "-25%", cost: "₹600-800/గంటకు" },
                risks: ["పై మట్టి పోవడం (ఎక్కువ లోతు తీస్తే)"],
                faq: [{ q: "ఎన్ని సార్లు చేయాలి?", a: "3-4 ఏళ్లకు ఒకసారి." }],
                troubleshooting: [{ symptom: "నీరు నిల్వ ఉండటం", cause: "సరైన లెవలింగ్ లేకపోవడం", action: "మళ్ళీ సరిచూడండి." }],
                costBenefit: { cost: "₹3000-4000/ఎకరం", savings: "నీరు/కూలీలు", profit: "సమాన పంట", payback: "1-2 పంటలు" },
                finalGuidance: "వేసవిలో వరి సాగుకు ముందు చేయడం మంచిది."
            }
        }
    },
    {
        id: 'vermicompost',
        title: { en: 'Vermicompost', te: 'వర్మికంపోస్ట్ (వానపాముల ఎరువు)' },
        image: vermicompostImg,
        summary: { en: 'Turn waste into gold with earthworms.', te: 'వానపాములతో వ్యర్థాలను బంగారంగా మార్చండి.' },
        content: {
            en: {
                whatIsIt: "Bio-fertilizer produced by earthworms digesting organic waste.",
                whyNeedIt: "To restore soil health damaged by chemical fertilizers.",
                benefits: ["Soil Structure: Improves aeration", "Nutrients: Rich in NPK & micronutrients", "Water retention: Increases", "Cost: Low production cost"],
                mistakes: ["Adding acidic waste (citrus)", "Too much water (drowning worms)", "Direct sunlight"],
                implementation: [
                    { step: "1. Pit Prep", desc: "Construct brick pit or use plastic bed in shade." },
                    { step: "2. Layering", desc: "Layer dry grass, cow dung, and organic waste." },
                    { step: "3. Worms", desc: "Release Eisenia fetida worms (1kg/ton)." }
                ],
                apSpecifics: { soil: "All types", crops: "All crops", climate: "Shaded area required" },
                layout: "Rectangular beds (10x3x2 ft)",
                stats: { yield: "Harvest in 45-60 days", water: "Sprinkle daily", cost: "₹3000/unit" },
                risks: ["Ants/Rats", "Overheating"],
                faq: [{ q: "Can I use kitchen waste?", a: "Yes, but avoid oily/spicy food and citrus." }],
                troubleshooting: [{ symptom: "Bad smell", cause: "Anaerobic condition (too wet)", action: "Turn the pile and stop watering." }],
                costBenefit: { cost: "₹3k-5k (Setup)", savings: "₹10k (Fertilizer)", profit: "Sell surplus worms/compost", payback: "1st Harvest" },
                finalGuidance: "Use vermiwash (liquid) as a foliar spray for extra boost."
            },
            te: {
                whatIsIt: "వానపాములు సేంద్రీయ వ్యర్థాలను తిని తయారు చేసే ఎరువు.",
                whyNeedIt: "రసాయన ఎరువుల వల్ల పాడైన నేల ఆరోగ్యాన్ని బాగు చేయడానికి.",
                benefits: ["నేల నిర్మాణం: గాలి ప్రసరణ పెరుగుతుంది", "పోషకాలు: NPK మరియు సూక్ష్మ పోషకాలు", "నీటి నిల్వ: పెరుగుతుంది", "ఖర్చు: తక్కువ"],
                mistakes: ["పుల్లటి పదార్థాలు వేయడం (నిమ్మ)", "ఎక్కువ నీరు (వానపాములు చనిపోతాయి)", "నేరుగా ఎండ తగలడం"],
                implementation: [
                    { step: "1. గుంత తయారీ", desc: "నీడలో ఇటుక గుంత లేదా ప్లాస్టిక్ బెడ్ ఏర్పాటు." },
                    { step: "2. పొరలు", desc: "ఎండు గడ్డి, ఆవు పేడ, వ్యర్థాలను పొరలుగా వేయాలి." },
                    { step: "3. వానపాములు", desc: "ఎసీనియా ఫెటిడా వానపాములను వదలాలి (1kg/టన్ను)." }
                ],
                apSpecifics: { soil: "అన్ని రకాలు", crops: "అన్ని పంటలు", climate: "నీడ అవసరం" },
                layout: "దీర్ఘచతురస్రాకార బెడ్లు (10x3x2 అడుగులు)",
                stats: { yield: "45-60 రోజుల్లో ఎరువు", water: "రోజూ చల్లాలి", cost: "₹3000/యూనిట్" },
                risks: ["చీమలు/ఎలుకలు", "వేడెక్కడం"],
                faq: [{ q: "వంటగది వ్యర్థాలు వాడవచ్చా?", a: "వాడవచ్చు, కానీ నూనె/కారం/పులుపు వద్దు." }],
                troubleshooting: [{ symptom: "దుర్వాసన", cause: "ఎక్కువ తేమ", action: "కుప్పను తిరగేసి నీరు ఆపండి." }],
                costBenefit: { cost: "₹3k-5k (ఏర్పాటు)", savings: "₹10k (ఎరువులు)", profit: "వానపాములు/ఎరువు అమ్మకం", payback: "మొదటి పంట" },
                finalGuidance: "వర్మివాష్ (ద్రవం) పిచికారీ చేస్తే పంట బాగా పెరుగుతుంది."
            }
        }
    },
    {
        id: 'azolla',
        title: { en: 'Azolla Cultivation', te: 'అజోల్లా సాగు' },
        image: azollaImg,
        summary: { en: 'Nutritious feed for cattle and paddy.', te: 'పశువులకు మరియు వరికి పోషకమైన ఆహారం.' },
        content: {
            en: {
                whatIsIt: "Fast-growing aquatic fern rich in protein and nitrogen.",
                whyNeedIt: "Alternative low-cost feed for cattle and bio-fertilizer for paddy.",
                benefits: ["Cattle: Increases milk yield by 15-20%", "Paddy: Fixes atmospheric nitrogen", "Cost: Very low production cost"],
                mistakes: ["Full sunlight (needs partial shade)", "Stagnant water without nutrients", "Overcrowding"],
                implementation: [
                    { step: "1. Pond", desc: "Dig a small pit (2x2m) lined with silpaulin." },
                    { step: "2. Mix", desc: "Add fertile soil, cow dung, and SSP." },
                    { step: "3. Seed", desc: "Inoculate fresh Azolla culture." }
                ],
                apSpecifics: { soil: "Ponds/Tanks", crops: "Cattle Feed, Paddy", climate: "Coastal AP suitable" },
                layout: "Small pits or paddy fields",
                stats: { yield: "1kg/day per pit", water: "Maintain 10cm depth", cost: "₹500/pit" },
                risks: ["Pests", "Extreme heat (>35°C)"],
                faq: [{ q: "How to feed cattle?", a: "Wash thoroughly and mix with fodder (1:1)." }],
                troubleshooting: [{ symptom: "Turning red/brown", cause: "High temp or low phosphate", action: "Provide shade and add SSP." }],
                costBenefit: { cost: "₹1000 (Setup)", savings: "₹3000/month (Feed)", profit: "More milk", payback: "1 Month" },
                finalGuidance: "Harvest daily to prevent overcrowding."
            },
            te: {
                whatIsIt: "ప్రోటీన్ మరియు నైట్రోజన్ అధికంగా ఉండే నీటి మొక్క.",
                whyNeedIt: "పశువులకు తక్కువ ఖర్చుతో కూడిన దాణా మరియు వరికి జీవ ఎరువు.",
                benefits: ["పశువులు: పాల దిగుబడి 15-20% పెరుగుతుంది", "వరి: నైట్రోజన్ అందిస్తుంది", "ఖర్చు: చాలా తక్కువ"],
                mistakes: ["పూర్తి ఎండ (పాక్షిక నీడ అవసరం)", "పోషకాలు లేని నీరు", "ఎక్కువగా పెరగడం"],
                implementation: [
                    { step: "1. గుంత", desc: "సిల్వార్పాలిన్ షీట్ తో చిన్న గుంత (2x2m) చేయాలి." },
                    { step: "2. మిశ్రమం", desc: "మట్టి, ఆవు పేడ, SSP కలపాలి." },
                    { step: "3. విత్తనం", desc: "తాజా అజోల్లా కల్చర్ వేయాలి." }
                ],
                apSpecifics: { soil: "గుంటలు/చెరువులు", crops: "పశుగ్రాసం, వరి", climate: "కోస్తా ప్రాంతం అనుకూలం" },
                layout: "చిన్న గుంతలు లేదా వరి పొలాలు",
                stats: { yield: "రోజుకు 1kg/గుంతకు", water: "10cm లోతు ఉంచాలి", cost: "₹500/గుంతకు" },
                risks: ["పురుగులు", "ఎక్కువ ఎండ (>35°C)"],
                faq: [{ q: "పశువులకు ఎలా పెట్టాలి?", a: "బాగా కడిగి దాణాతో కలపాలి (1:1)." }],
                troubleshooting: [{ symptom: "ఎరుపు/గోధుమ రంగు", cause: "ఎక్కువ వేడి లేదా ఫాస్ఫేట్ తక్కువ", action: "నీడ కల్పించి SSP వేయండి." }],
                costBenefit: { cost: "₹1000 (ఏర్పాటు)", savings: "₹3000/నెల (దాణా)", profit: "ఎక్కువ పాలు", payback: "1 నెల" },
                finalGuidance: "రోజూ సేకరిస్తే బాగా పెరుగుతుంది."
            }
        }
    },
    {
        id: 'greenhouse',
        title: { en: 'Greenhouse Farming', te: 'గ్రీన్ హౌస్ సాగు' },
        image: greenhouseImg,
        summary: { en: 'Grow crops year-round in controlled climate.', te: 'నియంత్రిత వాతావరణంలో ఏడాది పొడవునా పంటలు.' },
        content: {
            en: {
                whatIsIt: "Growing crops in controlled environment structures (Polyhouse/Net house).",
                whyNeedIt: "To grow high-value crops year-round protecting from pests and weather.",
                benefits: ["Yield: 5-10 times higher", "Quality: Export quality produce", "Water: 50% saving via drip", "Pest control: Easier"],
                mistakes: ["Poor ventilation", "Ignoring soil sterilization", "Wrong crop selection"],
                implementation: [
                    { step: "1. Structure", desc: "Build GI frame with UV stabilized film." },
                    { step: "2. Bed Prep", desc: "Sterilize soil and make raised beds." },
                    { step: "3. Fertigation", desc: "Install drip with automation." }
                ],
                apSpecifics: { soil: "Red soil/Cocopeat", crops: "Capsicum, Cucumber, Gerbera", climate: "Chittoor, Kuppam" },
                layout: "Sawtooth or naturally ventilated",
                stats: { yield: "50-80 tons/acre", water: "-50%", cost: "₹30-40 Lakhs/acre" },
                risks: ["High initial capital", "Cyclone damage"],
                faq: [{ q: "Is subsidy available?", a: "Yes, 50-75% under MIDH scheme." }],
                troubleshooting: [{ symptom: "Fungal diseases", cause: "High humidity", action: "Improve ventilation and use fungicides." }],
                costBenefit: { cost: "High (₹30L)", savings: "Labor/Water", profit: "Very High (₹10L/year)", payback: "3-4 Years" },
                finalGuidance: "Start with a small unit or visit a successful farm first."
            },
            te: {
                whatIsIt: "నియంత్రిత వాతావరణంలో (పాలిహౌస్/నెట్ హౌస్) పంటలు సాగు చేయడం.",
                whyNeedIt: "సంవత్సరం పొడవునా అధిక విలువ గల పంటలు పండించడానికి.",
                benefits: ["దిగుబడి: 5-10 రెట్లు ఎక్కువ", "నాణ్యత: ఎగుమతి రకం", "నీరు: 50% ఆదా", "చీడపీడలు: నియంత్రణ సులభం"],
                mistakes: ["గాలి ప్రసరణ లేకపోవడం", "నేల శుద్ధి చేయకపోవడం", "తప్పుడు పంట ఎంపిక"],
                implementation: [
                    { step: "1. నిర్మాణం", desc: "UV షీట్ తో GI ఫ్రేమ్ నిర్మాణం." },
                    { step: "2. బెడ్ తయారీ", desc: "నేల శుద్ధి చేసి ఎత్తైన బెడ్లు చేయాలి." },
                    { step: "3. ఫెర్టిగేషన్", desc: "ఆటోమేషన్ తో డ్రిప్ ఏర్పాటు." }
                ],
                apSpecifics: { soil: "ఎర్ర మట్టి/కోకోపీట్", crops: "క్యాప్సికం, దోస, జెర్బెరా", climate: "చిత్తూరు, కుప్పం" },
                layout: "సాటూత్ లేదా సహజ వెంటిలేషన్",
                stats: { yield: "50-80 టన్నులు/ఎకరం", water: "-50%", cost: "₹30-40 లక్షలు/ఎకరం" },
                risks: ["అధిక పెట్టుబడి", "తుఫాను నష్టం"],
                faq: [{ q: "సబ్సిడీ ఉందా?", a: "ఉంది, MIDH పథకం కింద 50-75%." }],
                troubleshooting: [{ symptom: "శిలీంధ్ర తెగుళ్లు", cause: "ఎక్కువ తేమ", action: "గాలి ప్రసరణ పెంచాలి." },],
                costBenefit: { cost: "ఎక్కువ (₹30L)", savings: "కూలీలు/నీరు", profit: "చాలా ఎక్కువ (₹10L/ఏడాది)", payback: "3-4 ఏళ్లు" },
                finalGuidance: "చిన్న యూనిట్ తో మొదలుపెట్టండి లేదా నిపుణులను సంప్రదించండి."
            }
        }
    },
    {
        id: 'precision-farming',
        title: { en: 'Precision Farming (IoT)', te: 'ఖచ్చితమైన వ్యవసాయం (IoT)' },
        image: precisionFarmingImg,
        summary: { en: 'Use technology to monitor every plant.', te: 'ప్రతి మొక్కను పర్యవేక్షించడానికి సాంకేతికత.' },
        content: {
            en: {
                whatIsIt: "Using IoT sensors, drones, and data analytics to optimize crop management.",
                whyNeedIt: "To reduce input costs and maximize yield through precise application.",
                benefits: ["Yield: +15-20%", "Inputs: -30% fertilizer/water", "Data: Real-time monitoring", "Labor: Reduced"],
                mistakes: ["Ignoring sensor calibration", "Over-reliance on automation without manual check"],
                implementation: [
                    { step: "1. Sensors", desc: "Install soil moisture and NPK sensors." },
                    { step: "2. Connectivity", desc: "Connect to mobile app via Wi-Fi/GSM." },
                    { step: "3. Action", desc: "Irrigate/Fertilize based on app alerts." }
                ],
                apSpecifics: { soil: "All types", crops: "High value (Chilli, Cotton)", climate: "All" },
                layout: "Sensor network grid",
                stats: { yield: "+15%", water: "-30%", cost: "₹50k-1L/acre" },
                risks: ["Technical failure", "Connectivity issues"],
                faq: [{ q: "Is internet required?", a: "Yes, for remote monitoring." }],
                troubleshooting: [{ symptom: "No data", cause: "Battery dead/No signal", action: "Replace battery/Check SIM." }],
                costBenefit: { cost: "High (₹50k+)", savings: "Inputs (₹20k/season)", profit: "High", payback: "2-3 Years" },
                finalGuidance: "Start with basic automation (drip) before full IoT."
            },
            te: {
                whatIsIt: "సెన్సార్లు, డ్రోన్లు మరియు డేటా ఉపయోగించి పంట సాగు.",
                whyNeedIt: "పెట్టుబడి తగ్గించి, దిగుబడి పెంచడానికి.",
                benefits: ["దిగుబడి: +15-20%", "పెట్టుబడి: -30% ఎరువులు/నీరు", "డేటా: ఎప్పటికప్పుడు సమాచారం", "కూలీలు: తక్కువ"],
                mistakes: ["సెన్సార్ల కాలిబ్రేషన్ మర్చిపోవడం", "పూర్తిగా మిషన్లపై ఆధారపడటం"],
                implementation: [
                    { step: "1. సెన్సార్లు", desc: "తేమ మరియు NPK సెన్సార్ల ఏర్పాటు." },
                    { step: "2. కనెక్టివిటీ", desc: "ఫోన్ యాప్ కు అనుసంధానం." },
                    { step: "3. చర్య", desc: "యాప్ సూచనల ప్రకారం నీరు/ఎరువులు ఇవ్వడం." }
                ],
                apSpecifics: { soil: "అన్ని రకాలు", crops: "వాణిజ్య పంటలు (మిరప, పత్తి)", climate: "అన్నీ" },
                layout: "సెన్సార్ల గ్రిడ్",
                stats: { yield: "+15%", water: "-30%", cost: "₹50వేలు-1లక్ష/ఎకరం" },
                risks: ["సాంకేతిక లోపాలు", "సిగ్నల్ సమస్యలు"],
                faq: [{ q: "ఇంటర్నెట్ అవసరమా?", a: "అవును, ఫోన్ లో చూడటానికి." }],
                troubleshooting: [{ symptom: "డేటా రావట్లేదు", cause: "బ్యాటరీ అయిపోయింది", action: "బ్యాటరీ మార్చండి." }],
                costBenefit: { cost: "ఎక్కువ (₹50k+)", savings: "పెట్టుబడి (₹20k/పంట)", profit: "ఎక్కువ", payback: "2-3 ఏళ్లు" },
                finalGuidance: "ముందు డ్రిప్ ఆటోమేషన్ తో మొదలుపెట్టండి."
            }
        }
    },
    {
        id: 'fish-farming',
        title: { en: 'Fish Farming (Aquaculture)', te: 'చేపల పెంపకం (Aquaculture)' },
        image: fishFarmingImg,
        summary: { en: 'Profitable business in ponds.', te: 'చెరువుల్లో లాభదాయకమైన వ్యాపారం.' },
        content: {
            en: {
                whatIsIt: "Breeding and rearing fish in ponds or tanks (Aquaculture).",
                whyNeedIt: "High demand for protein and profitable diversification.",
                benefits: ["Income: High returns", "Efficiency: Low FCR", "Integration: Can mix with poultry/paddy"],
                mistakes: ["Overstocking", "Poor water quality management", "Overfeeding"],
                implementation: [
                    { step: "1. Pond Prep", desc: "Dry, plough, and lime the pond." },
                    { step: "2. Stocking", desc: "Release fingerlings (Catla, Rohu, Mrigal)." },
                    { step: "3. Feeding", desc: "Feed floating pellets twice daily." }
                ],
                apSpecifics: { soil: "Clayey soil", crops: "Fish/Prawn", climate: "Coastal districts (Godavari/Krishna)" },
                layout: "Rectangular ponds (1 acre)",
                stats: { yield: "3-4 tons/acre", water: "Perennial source", cost: "₹2-3 Lakhs/acre" },
                risks: ["Disease outbreaks", "Market price fluctuation"],
                faq: [{ q: "Best fish for AP?", a: "Rohu, Catla, and Vennamei Prawn." }],
                troubleshooting: [{ symptom: "Fish gasping", cause: "Low Oxygen", action: "Run aerators immediately." }],
                costBenefit: { cost: "Medium", savings: "N/A", profit: "Very High", payback: "1-2 Crops" },
                finalGuidance: "Test water quality (pH, Ammonia) weekly."
            },
            te: {
                whatIsIt: "చెరువులు లేదా ట్యాంకుల్లో చేపల పెంపకం.",
                whyNeedIt: "అధిక ఆదాయం మరియు ప్రోటీన్ డిమాండ్.",
                benefits: ["ఆదాయం: ఎక్కువ లాభాలు", "సామర్థ్యం: తక్కువ ఖర్చు", "మిశ్రమ సాగు: కోళ్లు/వరితో కలిపి చేయవచ్చు"],
                mistakes: ["ఎక్కువ చేపలు వేయడం", "నీటి నాణ్యత చూడకపోవడం", "ఎక్కువ దాణా వేయడం"],
                implementation: [
                    { step: "1. చెరువు తయారీ", desc: "ఎండబెట్టి, దున్ని, సున్నం చల్లాలి." },
                    { step: "2. పిల్లలు", desc: "చేప పిల్లలను (కట్ల, రోహు) వదలాలి." },
                    { step: "3. మేత", desc: "రోజుకు రెండుసార్లు దాణా వేయాలి." }
                ],
                apSpecifics: { soil: "బంకమట్టి", crops: "చేపలు/రొయ్యలు", climate: "కోస్తా జిల్లాలు (గోదావరి/కృష్ణా)" },
                layout: "దీర్ఘచతురస్రాకార చెరువులు (1 ఎకరం)",
                stats: { yield: "3-4 టన్నులు/ఎకరం", water: "నీరు ఉండాలి", cost: "₹2-3 లక్షలు/ఎకరం" },
                risks: ["వ్యాధులు", "ధరల హెచ్చుతగ్గులు"],
                faq: [{ q: "AP కి ఏ చేప మంచిది?", a: "రోహు, కట్ల మరియు వెన్నామై రొయ్య." }],
                troubleshooting: [{ symptom: "చేపలు పైకి రావడం", cause: "ఆక్సిజన్ తక్కువ", action: "ఏరేటర్లు ఆన్ చేయండి." }],
                costBenefit: { cost: "మధ్యస్థం", savings: "వర్తించదు", profit: "చాలా ఎక్కువ", payback: "1-2 పంటలు" },
                finalGuidance: "వారానికి ఒకసారి నీటి పరీక్ష (pH, అమ్మోనియా) చేయండి."
            }
        }
    },
    {
        id: 'intercropping',
        title: { en: 'Intercropping', te: 'అంతర పంటలు (Intercropping)' },
        image: intercroppingImg,
        summary: { en: 'Grow two crops together for bonus income.', te: 'బోనస్ ఆదాయం కోసం రెండు పంటలు కలిసి పెంచండి.' },
        content: {
            en: {
                whatIsIt: "Growing two or more crops simultaneously in the same field.",
                whyNeedIt: "Risk reduction, better resource use, and bonus income.",
                benefits: ["Risk: Insurance against failure", "Soil: Nitrogen fixation (pulses)", "Pest: Trap crops reduce pests", "Income: Additional source"],
                mistakes: ["Choosing competing crops", "Wrong spacing", "Herbicide incompatibility"],
                implementation: [
                    { step: "1. Selection", desc: "Select compatible crops (e.g., Cotton + Redgram)." },
                    { step: "2. Sowing", desc: "Sow in specific row ratio (e.g., 6:1)." },
                    { step: "3. Care", desc: "Manage pests for both crops." }
                ],
                apSpecifics: { soil: "All types", crops: "Cotton+Redgram, Groundnut+Castor", climate: "Rainfed areas" },
                layout: "Row planting (e.g., 4 rows main, 1 row intercrop)",
                stats: { yield: "Main crop + 20% bonus", water: "Same usage", cost: "Marginal increase" },
                risks: ["Harvesting difficulty (if mechanized)", "Shading effect"],
                faq: [{ q: "Can I use herbicides?", a: "Be careful, select selective herbicides." }],
                troubleshooting: [{ symptom: "Main crop weak", cause: "Intercrop competition", action: "Increase spacing." }],
                costBenefit: { cost: "Seed cost only", savings: "Land/Water", profit: "Bonus Income", payback: "Same Season" },
                finalGuidance: "Choose pulses as intercrop for soil health."
            },
            te: {
                whatIsIt: "ఒకే పొలంలో రెండు లేదా అంతకంటే ఎక్కువ పంటలు పండించడం.",
                whyNeedIt: "రిస్క్ తగ్గించడానికి మరియు అదనపు ఆదాయం కోసం.",
                benefits: ["రిస్క్: పంట నష్టపోతే మరొకటి ఆదుకుంటుంది", "నేల: నైట్రోజన్ బలం (పప్పుధాన్యాలు)", "చీడపీడలు: కొన్ని పంటలు పురుగులను ఆకర్షించి ప్రధాన పంటను కాపాడతాయి", "ఆదాయం: అదనపు ఆదాయం"],
                mistakes: ["పోటీ పడే పంటలు ఎంచుకోవడం", "తప్పుడు దూరం", "కలుపు మందుల సమస్య"],
                implementation: [
                    { step: "1. ఎంపిక", desc: "అనుకూలమైన పంటలు (ఉదా: పత్తి + కంది)." },
                    { step: "2. విత్తడం", desc: "నిర్ణీత నిష్పత్తిలో (ఉదా: 6:1) విత్తాలి." },
                    { step: "3. సంరక్షణ", desc: "రెండు పంటలకు చీడపీడల నివారణ." }
                ],
                apSpecifics: { soil: "అన్ని రకాలు", crops: "పత్తి+కంది, వేరుశనగ+ఆముదం", climate: "వర్షాధార ప్రాంతాలు" },
                layout: "వరుసలు (ఉదా: 4 వరుసలు ప్రధాన పంట, 1 అంతర పంట)",
                stats: { yield: "ప్రధాన పంట + 20% బోనస్", water: "అదే నీరు", cost: "కొంచెం పెరుగుతుంది" },
                risks: ["కోత కష్టం (యంత్రాలు వాడితే)", "నీడ పడటం"],
                faq: [{ q: "కలుపు మందులు వాడవచ్చా?", a: "జాగ్రత్త, ఎంపిక చేసిన మందులే వాడాలి." }],
                troubleshooting: [{ symptom: "ప్రధాన పంట బలహీనం", cause: "అంతర పంట పోటీ", action: "దూరం పెంచండి." }],
                costBenefit: { cost: "విత్తన ఖర్చు మాత్రమే", savings: "భూమి/నీరు", profit: "బోనస్ ఆదాయం", payback: "అదే సీజన్" },
                finalGuidance: "నేల బలం కోసం పప్పుధాన్యాలను అంతర పంటగా ఎంచుకోండి."
            }
        }
    },
];
