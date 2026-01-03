"""
SMS Bot Service for KisanMitra - Simplified Telugu Version
Only supports: CROP-city, SUB, SCH, SUB-N, SCH-N commands
All responses in Telugu with multi-part SMS support.
"""

import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

# Telugu crop names
CROP_NAMES_TE = {
    "Rice": "వరి", "Paddy": "వరి", "Maize": "మొక్కజొన్న", "Cotton": "పత్తి",
    "Sugarcane": "చెరకు", "Groundnut": "వేరుశెనగ", "Chilli": "మిరప",
    "Tomato": "టమాట", "Onion": "ఉల్లిపాయ", "Turmeric": "పసుపు",
    "Wheat": "గోధుమ", "Soybean": "సోయాబీన్", "Jowar": "జొన్న",
    "Banana": "అరటి", "Mango": "మామిడి", "Pulses": "పప్పు"
}

# Subsidies Database (Telugu)
SUBSIDIES = [
    {
        "id": 1,
        "name": "అన్నదాత సుఖీభవ",
        "short": "₹20,000/సం రైతులకు",
        "details": """📋 అన్నదాత సుఖీభవ పథకం

💵 మొత్తం: ₹20,000 సంవత్సరానికి
📅 రెండు విడతలు: ఖరీఫ్ + రబీ

✅ అర్హత:
• AP రైతు ఉండాలి
• భూమి రికార్డు ఉండాలి
• ఆధార్ లింక్ అవసరం

📞 సంప్రదించండి: 1902
🌐 meekosam.ap.gov.in"""
    },
    {
        "id": 2,
        "name": "వడ్డీ రహిత రుణాలు",
        "short": "₹3L వరకు 0% వడ్డీ",
        "details": """📋 వడ్డీ రహిత పంట రుణాలు

💵 మొత్తం: ₹3,00,000 వరకు
📊 వడ్డీ: 0% (ప్రభుత్వ సబ్సిడీ)

✅ అర్హత:
• చిన్న/సన్న రైతులు
• పంట రుణం చరిత్ర
• వ్యవసాయ భూమి ఉండాలి

📍 మీ బ్యాంక్/PACS సంప్రదించండి
📞 హెల్ప్‌లైన్: 1800-180-1551"""
    },
    {
        "id": 3,
        "name": "యంత్రాల సబ్సిడీ",
        "short": "50% ధర తగ్గింపు",
        "details": """📋 వ్యవసాయ యంత్రాల సబ్సిడీ

💵 సబ్సిడీ: 50% ధర తగ్గింపు
🚜 ట్రాక్టర్, హార్వెస్టర్, స్ప్రేయర్

✅ అర్హత:
• AP రైతు
• 2 ఎకరాలు+ భూమి
• ఆధార్, భూమి పత్రాలు

📍 వ్యవసాయ శాఖ కార్యాలయం
📞 హెల్ప్‌లైన్: 1902"""
    },
    {
        "id": 4,
        "name": "డ్రిప్ ఇరిగేషన్",
        "short": "80-90% సబ్సిడీ",
        "details": """📋 డ్రిప్/స్ప్రింక్లర్ ఇరిగేషన్

💵 సబ్సిడీ: 80-90%
💧 నీటి ఆదా: 40-60%
📈 దిగుబడి పెరుగుదల: 20-30%

✅ అర్హత:
• ఏ రైతైనా దరఖాస్తు చేయవచ్చు
• భూమి పత్రాలు అవసరం

📍 హార్టికల్చర్ డిపార్ట్‌మెంట్
📞 హెల్ప్‌లైన్: 1800-180-1551"""
    },
    {
        "id": 5,
        "name": "పంట బీమా (PMFBY)",
        "short": "2% ప్రీమియంతో పూర్తి బీమా",
        "details": """📋 ప్రధాన మంత్రి ఫసల్ బీమా

💵 ప్రీమియం: కేవలం 2%
🌾 ఖరీఫ్, రబీ పంటలకు

✅ ఆవరించేవి:
• ప్రకృతి వైపరీత్యాలు
• తెగుళ్లు/రోగాలు
• పంట నష్టం

📍 బ్యాంక్/CSC సెంటర్
📞 హెల్ప్‌లైన్: 1800-180-1551"""
    }
]

# Schemes Database (Telugu)
SCHEMES = [
    {
        "id": 1,
        "name": "YSR రైతు భరోసా",
        "short": "₹13,500/సం పెట్టుబడి",
        "details": """📋 YSR రైతు భరోసా

💵 మొత్తం: ₹13,500/సంవత్సరం
📅 మూడు విడతలు:
• మే: ₹4,000 (ఖరీఫ్)
• అక్టోబర్: ₹4,000 (రబీ)
• జనవరి: ₹5,500 (సన్‌స్ట్రోక్)

✅ అర్హత:
• AP రైతు
• భూమి క్రింద 5 ఎకరాలు

📞 హెల్ప్‌లైన్: 1902"""
    },
    {
        "id": 2,
        "name": "ఉచిత విత్తనాలు",
        "short": "నాణ్యమైన విత్తనాలు ఉచితం",
        "details": """📋 ఉచిత విత్తన పంపిణీ

🌾 అందించే విత్తనాలు:
• వరి - HMT, BPT, MTU
• మొక్కజొన్న - హైబ్రిడ్
• పత్తి - Bt వంగడాలు

✅ ఎలా పొందాలి:
• RBK (రైతు భరోసా కేంద్రం)
• మీ గ్రామంలో

📞 హెల్ప్‌లైన్: 1902
📍 సమీప RBK సంప్రదించండి"""
    },
    {
        "id": 3,
        "name": "సూక్ష్మ సేద్యం",
        "short": "₹10,000 సబ్సిడీ/హెక్టారు",
        "details": """📋 సూక్ష్మ సేద్యం పథకం

💵 సబ్సిడీ: ₹10,000/హెక్టారు
🌱 ఆవరించేవి:
• మట్టి పరీక్ష
• సమగ్ర ఎరువులు
• సాంకేతిక సలహా

✅ అర్హత:
• చిన్న/సన్న రైతులు
• 2 హెక్టారుల వరకు

📍 వ్యవసాయ శాఖ
📞 హెల్ప్‌లైన్: 1902"""
    },
    {
        "id": 4,
        "name": "సోలార్ పంపులు",
        "short": "90% సబ్సిడీతో సోలార్",
        "details": """📋 సోలార్ పంప్ సెట్ పథకం

💵 సబ్సిడీ: 90%
⚡ సామర్థ్యం: 3HP, 5HP, 7.5HP
🌞 విద్యుత్ ఖర్చు: ₹0

✅ అర్హత:
• విద్యుత్ కనెక్షన్ లేని రైతులు
• బోరు/బావి ఉండాలి

📍 APSPDCL/RBK
📞 హెల్ప్‌లైన్: 1912"""
    },
    {
        "id": 5,
        "name": "వ్యవసాయ క్లినిక్‌లు",
        "short": "ఉచిత సాంకేతిక సలహా",
        "details": """📋 వ్యవసాయ క్లినిక్‌లు (RBKs)

🏥 అందించే సేవలు:
• మట్టి పరీక్ష
• పంట సలహా
• పురుగు గుర్తింపు
• మార్కెట్ సమాచారం

✅ ఎక్కడ:
• ప్రతి గ్రామంలో RBK
• ఉచిత సేవలు

📞 హెల్ప్‌లైన్: 1902
📍 సమీప RBK సందర్శించండి"""
    }
]


class SMSBotService:
    """Simplified SMS bot with only CROP, SUB, SCH commands in Telugu."""
    
    VALID_COMMANDS = ["CROP", "SUB", "SCH"]
    
    def __init__(self):
        logger.info("SMS Bot Service initialized (Telugu version)")
    
    def is_valid_command(self, message: str) -> bool:
        """Check if message is a valid SMS command."""
        msg = message.strip().upper()
        
        # CROP-cityname
        if msg.startswith("CROP-") and len(msg) > 5:
            return True
        
        # SUB or SUB-N
        if msg == "SUB" or (msg.startswith("SUB-") and msg[4:].isdigit()):
            return True
        
        # SCH or SCH-N
        if msg == "SCH" or (msg.startswith("SCH-") and msg[4:].isdigit()):
            return True
        
        # PLAN-{subscription_id} - NEW!
        if msg.startswith("PLAN-"):
            return True
        
        return False
    
    def handle_command(self, message: str) -> List[str]:
        """
        Handle SMS command and return list of response messages.
        Returns multiple SMS parts for streaming.
        """
        msg = message.strip().upper()
        
        try:
            # CROP-cityname
            if msg.startswith("CROP-"):
                city = message.strip()[5:].strip()
                return self.format_crop_recommendation(city)
            
            # PLAN-{subscription_id} - NEW!
            if msg.startswith("PLAN-"):
                sub_id = message.strip()[5:].strip()
                return self.format_daily_plan(sub_id)
            
            # SUB - List subsidies
            if msg == "SUB":
                return self.format_subsidies_list()
            
            # SUB-N - Subsidy details
            if msg.startswith("SUB-") and msg[4:].isdigit():
                sub_id = int(msg[4:])
                return self.format_subsidy_detail(sub_id)
            
            # SCH - List schemes
            if msg == "SCH":
                return self.format_schemes_list()
            
            # SCH-N - Scheme details
            if msg.startswith("SCH-") and msg[4:].isdigit():
                sch_id = int(msg[4:])
                return self.format_scheme_detail(sch_id)
            
            return [self.format_help()]
            
        except Exception as e:
            logger.error(f"SMS command error: {e}")
            return ["❌ లోపం. మళ్ళీ ప్రయత్నించండి."]
    def format_crop_recommendation(self, location: str) -> List[str]:
        """Format crop recommendation using ML engine and internal services with AI research for any location."""
        try:
            from services.soil_service import SoilService
            from services.season_service import SeasonService
            from services.ml_recommendation_service import MLRecommendationService
            from services.weather_service import WeatherService
            from services.crop_monitoring_service import get_crop_monitoring_service
            
            soil_service = SoilService()
            season_service = SeasonService()
            weather_service = WeatherService()
            ml_service = MLRecommendationService()
            monitoring_service = get_crop_monitoring_service()
            
            # Parse location (mandal, district format)
            parts = location.split(',')
            if len(parts) > 1:
                mandal = parts[0].strip()
                district = parts[1].strip()
            else:
                mandal = None
                district = parts[0].strip()
            
            # Get soil info from database first
            soil_data = soil_service.get_soil_info(district, mandal)
            soil_source = "database"
            
            # If unknown region, trigger AI research (just like the app)
            if soil_data.get("zone") == "Unknown Region":
                logger.info(f"SMS: Unknown region '{location}' - triggering AI research...")
                try:
                    from services.soil_research_agent import SoilResearchAgent
                    agent = SoilResearchAgent()
                    
                    # Try to geocode location first
                    lat, lon = None, None
                    try:
                        import requests
                        geo_resp = requests.get(
                            f"https://nominatim.openstreetmap.org/search",
                            params={"q": f"{location}, India", "format": "json", "limit": 1},
                            headers={"User-Agent": "KisanMitra-SMS/1.0"},
                            timeout=5
                        )
                        if geo_resp.status_code == 200 and geo_resp.json():
                            geo_data = geo_resp.json()[0]
                            lat = float(geo_data.get("lat", 17.385))
                            lon = float(geo_data.get("lon", 78.487))
                            logger.info(f"SMS: Geocoded '{location}' to ({lat}, {lon})")
                    except Exception as geo_err:
                        logger.warning(f"SMS: Geocoding failed: {geo_err}")
                    
                    # Research soil data for this region
                    researched = agent.research_region(district, mandal, lat=lat, lon=lon)
                    if researched and researched.get("soil"):
                        soil_data = researched
                        soil_source = "ai_researched"
                        logger.info(f"SMS: AI research found: {soil_data.get('soil', 'Unknown')}")
                    else:
                        # Use defaults based on general India soil
                        soil_data = {
                            "soil": "Loamy",
                            "ph": 6.8, "n": 180, "p": 50, "k": 200,
                            "zone": "Default (AI research pending)",
                            "lat": lat or 17.385,
                            "lon": lon or 78.487
                        }
                        soil_source = "default"
                except Exception as research_err:
                    logger.warning(f"SMS: Research failed: {research_err}")
                    # Fallback to defaults
                    soil_data = {
                        "soil": "Loamy",
                        "ph": 6.8, "n": 180, "p": 50, "k": 200,
                        "zone": "Default",
                        "lat": 17.385, "lon": 78.487
                    }
            
            # Get weather and season
            lat = soil_data.get('lat', 17.385)
            lon = soil_data.get('lon', 78.4867)
            weather = weather_service.get_current_weather(lat, lon)
            season = season_service.get_season()
            season_te = {"Kharif": "ఖరీఫ్", "Rabi": "రబీ", "Zaid": "జైద్"}.get(season, season)
            
            # Soil parameters for ML
            soil_type = soil_data.get("soil", "Loamy")
            soil_ph = soil_data.get("ph", 7.0)
            soil_n = soil_data.get("n", 150)
            soil_p = soil_data.get("p", 50)
            soil_k = soil_data.get("k", 150)
            temp = weather.get('temp', 28)
            humidity = weather.get('humidity', 60)
            
            # Get ML recommendations
            recs = ml_service.get_recommendations(
                soil_type=soil_type,
                season=season,
                temp=temp,
                humidity=humidity,
                soil_ph=soil_ph,
                soil_n=soil_n,
                soil_p=soil_p,
                soil_k=soil_k
            )
            
            # Handle both list and dict returns
            if isinstance(recs, list):
                top_crops = recs[:3]
            else:
                top_crops = recs.get('recommendations', [])[:3]
            
            if not top_crops:
                return [f"❌ సిఫార్సులు లభించలేదు."]
            
            # Build concise SMS
            crops_list = ""
            for i, rec in enumerate(top_crops, 1):
                crop = rec.get("crop", "N/A")
                crop_te = CROP_NAMES_TE.get(crop, crop)
                score = rec.get("score", 85)
                
                # Duration from monitoring data
                crop_data = monitoring_service.stages.get('crops', {}).get(crop, {})
                duration = crop_data.get('duration_days', 120)
                
                crops_list += f"\n{i}. {crop_te} - {score:.0f}% ({duration}రో)"
            
            # Build message
            msg = f"""🌾 {location.upper()} AI సిఫార్సులు

🌡️ {temp:.0f}°C | 🌱 {soil_type[:8]} | 📅 {season_te}
{crops_list}

📲 వివరాలకు: kisanmitra.in"""
            
            return [msg]
            
        except Exception as e:
            import traceback
            logger.error(f"Crop recommendation error: {e}")
            logger.error(traceback.format_exc())
            return [f"❌ లోపం: {str(e)[:50]}"]
    
    def format_subsidies_list(self) -> List[str]:
        """Format subsidies list - 2 SMS parts max."""
        messages = []
        
        # Part 1: List
        msg1 = "📋 AP రైతు సబ్సిడీలు\n\n"
        for sub in SUBSIDIES:
            msg1 += f"{sub['id']}. {sub['name']}\n   {sub['short']}\n"
        messages.append(msg1.strip())
        
        # Part 2: Instructions
        msg2 = """📱 వివరాలకు:
SUB-1 (అన్నదాత సుఖీభవ)
SUB-2 (వడ్డీ రహిత రుణాలు)
SUB-3 (యంత్రాల సబ్సిడీ)
SUB-4 (డ్రిప్ ఇరిగేషన్)
SUB-5 (పంట బీమా)

📞 హెల్ప్‌లైన్: 1902"""
        messages.append(msg2)
        
        return messages
    
    def format_subsidy_detail(self, sub_id: int) -> List[str]:
        """Format specific subsidy details - 2 SMS parts max."""
        if sub_id < 1 or sub_id > len(SUBSIDIES):
            return [f"❌ సబ్సిడీ {sub_id} కనుగొనబడలేదు.\n\nSUB-1 నుండి SUB-5 వరకు ప్రయత్నించండి."]
        
        sub = SUBSIDIES[sub_id - 1]
        
        # Split long details into 2 parts if needed
        details = sub['details']
        if len(details) > 300:
            mid = len(details) // 2
            # Find a good split point
            split_point = details.rfind('\n', 0, mid + 50)
            if split_point == -1:
                split_point = mid
            return [details[:split_point].strip(), details[split_point:].strip()]
        
        return [details]
    
    def format_schemes_list(self) -> List[str]:
        """Format schemes list - 2 SMS parts max."""
        messages = []
        
        # Part 1: List
        msg1 = "📋 AP ప్రభుత్వ పథకాలు\n\n"
        for sch in SCHEMES:
            msg1 += f"{sch['id']}. {sch['name']}\n   {sch['short']}\n"
        messages.append(msg1.strip())
        
        # Part 2: Instructions
        msg2 = """📱 వివరాలకు:
SCH-1 (YSR రైతు భరోసా)
SCH-2 (ఉచిత విత్తనాలు)
SCH-3 (సూక్ష్మ సేద్యం)
SCH-4 (సోలార్ పంపులు)
SCH-5 (వ్యవసాయ క్లినిక్‌లు)

📞 హెల్ప్‌లైన్: 1902"""
        messages.append(msg2)
        
        return messages
    
    def format_scheme_detail(self, sch_id: int) -> List[str]:
        """Format specific scheme details - 2 SMS parts max."""
        if sch_id < 1 or sch_id > len(SCHEMES):
            return [f"❌ పథకం {sch_id} కనుగొనబడలేదు.\n\nSCH-1 నుండి SCH-5 వరకు ప్రయత్నించండి."]
        
        sch = SCHEMES[sch_id - 1]
        
        # Split long details into 2 parts if needed
        details = sch['details']
        if len(details) > 300:
            mid = len(details) // 2
            split_point = details.rfind('\n', 0, mid + 50)
            if split_point == -1:
                split_point = mid
            return [details[:split_point].strip(), details[split_point:].strip()]
        
        return [details]
    
    def format_help(self) -> str:
        """Format help message."""
        return """🌾 కిసాన్‌మిత్ర SMS

📱 కమాండ్లు:
CROP-గుంటూరు (పంట సిఫార్సులు)
PLAN-SUB123 (రోజు ప్లాన్)
SUB (సబ్సిడీల జాబితా)
SCH (పథకాల జాబితా)

📞 హెల్ప్: 1902"""
    
    def format_daily_plan(self, subscription_id: str) -> List[str]:
        """Format daily plan for a subscription in Telugu."""
        try:
            from services.crop_monitoring_service import get_crop_monitoring_service
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from database import get_subscription_by_id
            
            subscription = get_subscription_by_id(subscription_id)
            if not subscription:
                return [f"❌ సబ్‌స్క్రిప్షన్ {subscription_id} కనుగొనబడలేదు."]
            
            monitoring_service = get_crop_monitoring_service()
            action_plan = monitoring_service.generate_daily_action_plan(subscription)
            
            crop = subscription.get('crop', 'పంట')
            crop_te = CROP_NAMES_TE.get(crop, crop)
            stage_info = action_plan.get('stage_info', {})
            das = stage_info.get('days_after_sowing', 0)
            stage_name = stage_info.get('stage_name', 'Unknown')
            weather = action_plan.get('current_weather', {})
            tasks = action_plan.get('today_tasks', [])
            
            messages = []
            
            # Part 1: Status
            msg1 = f"""📋 {crop_te} - రోజు {das}

దశ: {stage_name}
🌡️ {weather.get('temp', 28):.0f}°C | 💧 {weather.get('humidity', 60)}%

{action_plan.get('summary_te', action_plan.get('summary_en', ''))}"""
            messages.append(msg1)
            
            # Part 2: Tasks
            task_list = ""
            for i, task in enumerate(tasks[:4], 1):
                task_text = task.get('task_te', task.get('task_en', ''))
                priority = task.get('priority', '')
                icon = "⚠️" if priority == 'urgent' else "✅"
                task_list += f"{i}. {icon} {task_text}\n"
            
            if task_list:
                msg2 = f"""ఈరోజు పనులు:

{task_list.strip()}

📲 PLAN-{subscription_id} మరిన్ని"""
                messages.append(msg2)
            
            return messages
            
        except Exception as e:
            logger.error(f"Daily plan format error: {e}")
            return [f"❌ లోపం: {str(e)[:30]}"]
    
    def format_welcome_sms(self, subscription: Dict) -> List[str]:
        """Format welcome SMS for new subscription in Telugu."""
        try:
            from services.crop_monitoring_service import get_crop_monitoring_service
            
            crop = subscription.get('crop', 'పంట')
            crop_te = CROP_NAMES_TE.get(crop, crop)
            location = subscription.get('locationName', subscription.get('location', {}).get('name', ''))
            sowing_date = subscription.get('sowingDate', '')
            sub_id = subscription.get('subscriptionId', '')
            
            monitoring_service = get_crop_monitoring_service()
            action_plan = monitoring_service.generate_daily_action_plan(subscription)
            tasks = action_plan.get('today_tasks', [])
            weather = action_plan.get('current_weather', {})
            
            messages = []
            
            # Welcome message
            msg1 = f"""🌾 కిసాన్‌మిత్ర స్వాగతం!

మీ {crop_te} పంట నమోదు అయింది ✅
📅 విత్తు: {sowing_date}
📍 {location}

🌤️ వాతావరణం: {weather.get('temp', 28):.0f}°C"""
            messages.append(msg1)
            
            # Today's tasks
            task_list = ""
            for i, task in enumerate(tasks[:3], 1):
                task_text = task.get('task_te', task.get('task_en', ''))
                task_list += f"✅ {task_text}\n"
            
            if task_list:
                msg2 = f"""ఈరోజు చేయండి:

{task_list.strip()}

📲 PLAN-{sub_id} రోజు ప్లాన్ కోసం"""
                messages.append(msg2)
            
            return messages
            
        except Exception as e:
            logger.error(f"Welcome SMS format error: {e}")
            return [f"🌾 స్వాగతం! మీ పంట నమోదు అయింది. ❌ వివరాలు లోపం."]


# Singleton
_sms_bot = None

def get_sms_bot() -> SMSBotService:
    global _sms_bot
    if _sms_bot is None:
        _sms_bot = SMSBotService()
    return _sms_bot
