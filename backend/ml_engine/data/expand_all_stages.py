"""
Expand all crops to have comprehensive stage data (minimum 6 stages)
"""
import json
import os

DATA_DIR = os.path.dirname(__file__)
STAGES_PATH = os.path.join(DATA_DIR, 'crop_stages.json')
FAQS_PATH = os.path.join(DATA_DIR, 'crop_faqs_complete.json')

# Common stage templates that can be adapted for any crop
def get_standard_stages(crop_name, crop_name_te, duration_days):
    """Generate standard 7 stages for a crop"""
    week_per_stage = max(1, duration_days // 7 // 7)  # Distribute across 7 stages
    
    return [
        {
            "name": "Land Preparation",
            "name_en": "Land Preparation",
            "name_te": "భూమి సిద్ధం",
            "week_start": 1,
            "week_end": 1,
            "tasks_en": [
                f"Prepare land for {crop_name} cultivation",
                "Plow 2-3 times to fine tilth",
                "Apply FYM or compost as basal dose",
                "Level the field and prepare beds/ridges as needed"
            ],
            "tasks_te": [
                f"{crop_name_te} సాగు కోసం భూమి సిద్ధం చేయండి",
                "2-3 సార్లు దున్నండి",
                "FYM లేదా కంపోస్ట్ వేయండి",
                "పొలం సమం చేసి బెడ్లు/వరదలు తయారు చేయండి"
            ],
            "irrigation_en": "Pre-sowing irrigation for moisture",
            "irrigation_te": "విత్తే ముందు తేమ కోసం నీరు"
        },
        {
            "name": "Sowing/Planting",
            "name_en": "Sowing/Planting",
            "name_te": "విత్తడం/నాటడం",
            "week_start": 2,
            "week_end": 2,
            "tasks_en": [
                f"Sow/plant {crop_name} at recommended spacing",
                "Treat seeds with fungicide before sowing",
                "Ensure proper depth of sowing",
                "Apply starter fertilizer"
            ],
            "tasks_te": [
                f"{crop_name_te}ను సిఫార్సు చేసిన దూరంలో విత్తండి/నాటండి",
                "విత్తే ముందు విత్తనాలకు ఫంగిసైడ్ శుద్ధి చేయండి",
                "సరైన లోతు నిర్ధారించండి",
                "స్టార్టర్ ఎరువు వేయండి"
            ],
            "irrigation_en": "Light irrigation after sowing",
            "irrigation_te": "విత్తిన తర్వాత తేలికపాటి నీరు"
        },
        {
            "name": "Germination/Establishment",
            "name_en": "Germination/Establishment",
            "name_te": "మొలకెత్తడం/స్థాపన",
            "week_start": 3,
            "week_end": 4,
            "tasks_en": [
                "Monitor germination and fill gaps",
                "Maintain adequate soil moisture",
                "Protect from birds and pests",
                "First weeding if needed"
            ],
            "tasks_te": [
                "మొలకెత్తడం పర్యవేక్షించండి మరియు ఖాళీలు నింపండి",
                "తగినంత మట్టి తేమ నిలపండి",
                "పక్షులు మరియు పురుగుల నుండి రక్షించండి",
                "అవసరమైతే మొదటి కలుపు"
            ],
            "irrigation_en": "Regular light irrigation every 3-4 days",
            "irrigation_te": "3-4 రోజులకు ఒకసారి తేలికపాటి నీరు"
        },
        {
            "name": "Vegetative Growth",
            "name_en": "Vegetative Growth",
            "name_te": "వృక్ష పెరుగుదల",
            "week_start": 5,
            "week_end": max(6, duration_days // 7 // 2),
            "tasks_en": [
                "Apply first top dressing of nitrogen",
                "Weed control - manual or herbicide",
                "Monitor for pest and disease symptoms",
                "Ensure proper plant nutrition"
            ],
            "tasks_te": [
                "మొదటి టాప్ డ్రెస్సింగ్ నత్రజని వేయండి",
                "కలుపు నియంత్రణ",
                "పురుగులు మరియు వ్యాధుల లక్షణాలు పరిశీలించండి",
                "సరైన మొక్క పోషణ నిర్ధారించండి"
            ],
            "irrigation_en": f"Regular irrigation as per {crop_name} requirement",
            "irrigation_te": f"{crop_name_te} అవసరానికి అనుగుణంగా నీరు"
        },
        {
            "name": "Flowering/Fruiting",
            "name_en": "Flowering/Fruiting",
            "name_te": "పూత/కాయ",
            "week_start": max(7, duration_days // 7 // 2 + 1),
            "week_end": max(9, duration_days // 7 * 2 // 3),
            "tasks_en": [
                "Critical growth stage - maintain adequate moisture",
                "Apply second top dressing",
                "Monitor for pest and disease pressure",
                "Avoid water stress during this period"
            ],
            "tasks_te": [
                "క్లిష్టమైన పెరుగుదల దశ - తగినంత తేమ నిలపండి",
                "రెండవ టాప్ డ్రెస్సింగ్ వేయండి",
                "పురుగులు మరియు వ్యాధులు పర్యవేక్షించండి",
                "ఈ సమయంలో నీటి ఒత్తిడి నివారించండి"
            ],
            "irrigation_en": "Critical - maintain uniform moisture",
            "irrigation_te": "క్లిష్టమైన - ఏకరీతి తేమ నిలపండి"
        },
        {
            "name": "Maturity",
            "name_en": "Maturity",
            "name_te": "పరిపక్వత",
            "week_start": max(10, duration_days // 7 * 2 // 3 + 1),
            "week_end": max(11, duration_days // 7 - 1),
            "tasks_en": [
                f"Monitor {crop_name} maturity signs",
                "Reduce irrigation as crop matures",
                "Prepare for harvest",
                "Protect from late season pests"
            ],
            "tasks_te": [
                f"{crop_name_te} పరిపక్వత సంకేతాలు పర్యవేక్షించండి",
                "పంట పరిపక్వమవుతున్నప్పుడు నీరు తగ్గించండి",
                "కోత కోసం సిద్ధం చేయండి",
                "ఆలస్యంగా వచ్చే పురుగుల నుండి రక్షించండి"
            ],
            "irrigation_en": "Reduce irrigation before harvest",
            "irrigation_te": "కోతకు ముందు నీరు తగ్గించండి"
        },
        {
            "name": "Harvest",
            "name_en": "Harvest",
            "name_te": "కోత",
            "week_start": max(12, duration_days // 7),
            "week_end": max(13, duration_days // 7 + 1),
            "tasks_en": [
                f"Harvest {crop_name} at proper maturity",
                "Use appropriate harvesting tools",
                "Handle carefully to avoid damage",
                "Prepare for storage or sale"
            ],
            "tasks_te": [
                f"{crop_name_te}ను సరైన పరిపక్వతలో కోయండి",
                "సరైన కోత సాధనాలు వాడండి",
                "నష్టం నివారించడానికి జాగ్రత్తగా నిర్వహించండి",
                "నిల్వ లేదా అమ్మకం కోసం సిద్ధం చేయండి"
            ],
            "irrigation_en": "Stop irrigation before harvest",
            "irrigation_te": "కోతకు ముందు నీరు ఆపండి"
        }
    ]

def expand_all_crops():
    with open(STAGES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    crops = data.get('crops', {})
    
    # Crops that need expansion (less than 5 stages)
    crops_to_expand = [c for c in crops if len(crops[c].get('stages', [])) < 5]
    
    print(f"Found {len(crops_to_expand)} crops with less than 5 stages")
    
    for crop_name in crops_to_expand:
        crop_data = crops[crop_name]
        crop_name_te = crop_data.get('name_te', crop_name)
        duration = crop_data.get('duration_days', 120)
        
        # Generate new stages
        new_stages = get_standard_stages(crop_name, crop_name_te, duration)
        
        # Keep existing pests and diseases if present
        pests = crop_data.get('pests', [])
        diseases = crop_data.get('diseases', [])
        
        # Update crop data
        crops[crop_name].update({
            'stages': new_stages
        })
        
        print(f"  ✓ Expanded {crop_name} from {len(crop_data.get('stages', []))} to {len(new_stages)} stages")
    
    # Save
    with open(STAGES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Expanded {len(crops_to_expand)} crops to full stage data")
    
    # Summary of all crops
    print("\nFinal crop status:")
    for crop in sorted(crops.keys()):
        stages = crops[crop].get('stages', [])
        print(f"  {crop}: {len(stages)} stages")

if __name__ == "__main__":
    expand_all_crops()
