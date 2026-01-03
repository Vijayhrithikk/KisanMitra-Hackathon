"""
WhatsApp Bot Service for KisanMitra
Uses Twilio WhatsApp API with rich features:
- Text messages in Telugu + English
- Interactive buttons and lists
- Image messages (crop cards, pest photos)
- Location-based recommendations
- Farmer onboarding and marketplace
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '+14155238886')

# Backend API for marketplace
BACKEND_API = "http://localhost:5000/api"

# Telugu translations
CROP_NAMES_TE = {
    "Rice": "వరి", "Paddy": "వరి", "Maize": "మొక్కజొన్న", "Cotton": "పత్తి",
    "Sugarcane": "చెరకు", "Groundnut": "వేరుశెనగ", "Ground Nuts": "వేరుశెనగ",
    "Chilli": "మిరప", "Wheat": "గోధుమ", "Turmeric": "పసుపు",
    "Pulses": "పప్పులు", "Millets": "చిరుధాన్యాలు"
}

# Updated menu with marketplace
MAIN_MENU = """🌾 *కిసాన్‌మిత్ర WhatsApp*

మీకు ఏ సహాయం కావాలి?

1️⃣ పంట సిఫార్సులు
2️⃣ సబ్సిడీలు/పథకాలు
3️⃣ వాతావరణం
4️⃣ మార్కెట్ ధరలు
5️⃣ తెగులు గుర్తింపు
6️⃣ 🏪 మార్కెట్‌ప్లేస్ (అమ్మండి/కొనండి)
7️⃣ సహాయం

*నంబర్ టైప్ చేయండి*"""

MARKETPLACE_MENU = """🏪 *కిసాన్‌మిత్ర మార్కెట్‌ప్లేస్*

మీరు ఏం చేయాలనుకుంటున్నారు?

A️ నా లిస్టింగ్‌లు చూడండి
B️ కొత్త పంట జాబితా చేయండి
C️ అందుబాటులో ఉన్న పంటలు చూడండి

*అక్షరం టైప్ చేయండి (A/B/C)*"""


class WhatsAppBotService:
    """WhatsApp bot with rich messaging features."""
    
    def __init__(self):
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            self.enabled = True
            logger.info("WhatsApp Bot initialized with Twilio")
        else:
            self.client = None
            self.enabled = False
            logger.warning("WhatsApp Bot disabled - Twilio credentials missing")
        
        self.whatsapp_number = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        self.user_sessions = {}  # Track user conversation state
    
    def handle_incoming_message(self, from_number: str, message: str, 
                                 media_url: str = None, latitude: float = None, 
                                 longitude: float = None) -> Dict:
        """
        Handle incoming WhatsApp message and generate response.
        
        Args:
            from_number: User's WhatsApp number
            message: Text message content
            media_url: URL of attached media (for pest detection)
            latitude: User's latitude (if location shared)
            longitude: User's longitude (if location shared)
        
        Returns:
            Response dict with message type and content
        """
        msg_lower = message.strip().lower()
        original_message = message.strip()
        
        # Store/retrieve user session
        session = self.user_sessions.get(from_number, {"state": "menu"})
        state = session.get("state", "menu")
        
        try:
            # Handle ongoing conversation flows first
            if state.startswith("listing_"):
                return self._handle_listing_flow(from_number, original_message, session)
            
            if state == "awaiting_registration":
                return self._handle_registration(from_number, original_message, session)
            
            # Location shared - give crop recommendations or use for listing
            if latitude and longitude:
                if state == "listing_location":
                    session["listing_data"]["location"] = f"{latitude:.4f},{longitude:.4f}"
                    session["state"] = "listing_quantity"
                    self.user_sessions[from_number] = session
                    return {"type": "text", "to": from_number, "body": "📍 లొకేషన్ అందింది!\n\n📦 *ఎంత పరిమాణం (క్వింటాల్లో)?*\n\nఉదా: 10"}
                return self._handle_location(from_number, latitude, longitude)
            
            # Image shared - pest detection or listing image
            if media_url:
                if state == "listing_image":
                    session["listing_data"]["image_url"] = media_url
                    return self._finalize_listing(from_number, session)
                return self._handle_image(from_number, media_url)
            
            # Menu navigation
            if msg_lower in ["hi", "hello", "start", "menu", "హాయ్", "మెను", "cancel", "రద్దు"]:
                self.user_sessions[from_number] = {"state": "menu"}
                return self._send_main_menu(from_number)
            
            if msg_lower in ["1", "పంట", "crop", "crops"]:
                return self._handle_crop_request(from_number)
            
            if msg_lower in ["2", "సబ్సిడీ", "subsidy", "scheme", "పథకం"]:
                return self._handle_subsidy_list(from_number)
            
            if msg_lower in ["3", "వాతావరణం", "weather"]:
                return self._handle_weather(from_number, session.get("lat", 17.385), session.get("lon", 78.4867))
            
            if msg_lower in ["4", "ధర", "price", "market"]:
                return self._handle_market_prices(from_number)
            
            if msg_lower in ["5", "తెగులు", "pest", "disease"]:
                return self._handle_pest_help(from_number)
            
            # Marketplace - Option 6
            if msg_lower in ["6", "marketplace", "మార్కెట్", "sell", "అమ్మండి"]:
                return self._handle_marketplace_menu(from_number)
            
            if msg_lower in ["7", "help", "సహాయం"]:
                return self._send_help(from_number)
            
            # Marketplace sub-options
            if msg_lower in ["a", "my listings", "నా లిస్టింగ్"]:
                return self._handle_my_listings(from_number)
            
            if msg_lower in ["b", "new listing", "కొత్త లిస్టింగ్", "sell"]:
                return self._start_listing_flow(from_number)
            
            if msg_lower in ["c", "browse", "చూడండి"]:
                return self._handle_browse_listings(from_number)
            
            # Subsidy details (SUB-1, SUB-2, etc.)
            if msg_lower.startswith("sub-") and msg_lower[4:].isdigit():
                return self._handle_subsidy_detail(from_number, int(msg_lower[4:]))
            
            # Crop recommendation with location name
            if msg_lower.startswith("crop-") or msg_lower.startswith("పంట-"):
                location = original_message.split("-", 1)[1].strip()
                return self._handle_crop_by_location(from_number, location)
            
            # Default: try to understand as a question
            return self._handle_free_text(from_number, msg_lower)
            
        except Exception as e:
            logger.error(f"WhatsApp handler error: {e}")
            return self._error_response(from_number)
    
    def _send_main_menu(self, to_number: str) -> Dict:
        """Send main menu with options."""
        return {
            "type": "text",
            "to": to_number,
            "body": MAIN_MENU
        }
    
    def _handle_crop_request(self, to_number: str) -> Dict:
        """Ask user to share location for crop recommendations."""
        message = """🌱 *పంట సిఫార్సులు*

మీ ప్రాంతానికి సరైన పంటలు చెప్పడానికి:

📍 *మీ లొకేషన్ షేర్ చేయండి*
లేదా
✍️ *CROP-గుంటూరు* అని టైప్ చేయండి

(మీ జిల్లా/మండలం పేరు వాడండి)"""
        
        return {
            "type": "text",
            "to": to_number,
            "body": message
        }
    
    def _handle_location(self, to_number: str, lat: float, lon: float) -> Dict:
        """Handle location share and give crop recommendations with comprehensive data."""
        try:
            # Store location in session
            self.user_sessions[to_number] = {"lat": lat, "lon": lon, "state": "has_location"}
            
            # Get recommendations
            from services.soil_service import SoilService
            from services.ml_recommendation_service import get_ml_recommender
            from services.season_service import SeasonService
            from services.weather_service import WeatherService
            from services.crop_monitoring_service import get_crop_monitoring_service
            
            soil_service = SoilService()
            soil_data = soil_service.get_soil_info_by_coords(lat, lon)
            
            weather_service = WeatherService()
            weather = weather_service.get_current_weather(lat, lon)
            
            season_service = SeasonService()
            season = season_service.get_season()
            
            ml_service = get_ml_recommender()
            recs = ml_service.get_recommendations(
                soil_type=soil_data.get("soil", "Loamy"),
                season=season,
                temp=weather.get("temp", 28),
                humidity=weather.get("humidity", 60)
            )[:5]
            
            # Get monitoring service for stage data
            monitoring_service = get_crop_monitoring_service()
            
            # Format response
            season_te = {"Kharif": "ఖరీఫ్", "Rabi": "రబీ", "Zaid": "జైద్"}.get(season, season)
            
            # Weather alert
            weather_alert = ""
            if weather.get('temp', 25) > 38:
                weather_alert = "\n⚠️ అధిక వేడి - సాయంత్రం పనులు చేయండి"
            elif weather.get('humidity', 60) > 85:
                weather_alert = "\n⚠️ అధిక తేమ - తెగుళ్ల కోసం జాగ్రత్త"
            
            message = f"""🌾 *మీ ప్రాంతానికి సిఫార్సులు*

📍 Location: {lat:.2f}, {lon:.2f}
🌡️ ఉష్ణోగ్రత: {weather.get('temp', '--')}°C
💧 తేమ: {weather.get('humidity', '--')}%
🌱 మట్టి: {soil_data.get('soil', 'N/A')}
📅 సీజన్: {season_te}{weather_alert}

✅ *టాప్ పంటలు:*
"""
            for i, rec in enumerate(recs[:3], 1):
                crop = rec.get('crop', 'N/A')
                crop_te = CROP_NAMES_TE.get(crop, crop)
                confidence = rec.get('confidence', 85)
                
                # Get comprehensive stage data
                crop_data = monitoring_service.stages.get('crops', {}).get(crop, {})
                duration = crop_data.get('total_duration_days', 120)
                first_stage = crop_data.get('stages', [{}])[0] if crop_data.get('stages') else {}
                stage_name = first_stage.get('name', 'విత్తనం')
                pest_focus = first_stage.get('pest_focus', [])[:1]
                
                message += f"\n{i}. *{crop_te}* - {confidence}% match"
                message += f"\n   ⏱️ {duration} రోజులు | 🌱 {stage_name}"
                if pest_focus:
                    message += f"\n   🐛 {', '.join(pest_focus)}"
            
            message += "\n\n💡 _సబ్‌స్క్రైబ్ చేసి రోజువారీ ప్లాన్ పొందండి_"
            message += "\n📲 _PLAN- కమాండ్ > రోజు పనులు_"
            
            return {
                "type": "text",
                "to": to_number,
                "body": message
            }
            
        except Exception as e:
            logger.error(f"Location handler error: {e}")
            return {
                "type": "text",
                "to": to_number,
                "body": f"📍 లొకేషన్ అందింది!\n\nసిఫార్సులు తయారు చేస్తున్నాం...\n\nమీ ప్రాంతం: {lat:.2f}°N, {lon:.2f}°E"
            }
    
    def _handle_crop_by_location(self, to_number: str, location: str) -> Dict:
        """Handle CROP-location command with comprehensive data."""
        try:
            from services.soil_service import SoilService
            from services.ml_recommendation_service import get_ml_recommender
            from services.season_service import SeasonService
            from services.crop_monitoring_service import get_crop_monitoring_service
            
            soil_service = SoilService()
            soil_data = soil_service.get_soil_info(location)
            
            if soil_data.get("zone") == "Unknown Region":
                return {
                    "type": "text", 
                    "to": to_number,
                    "body": f"❌ '{location}' కనుగొనబడలేదు.\n\nజిల్లా లేదా మండలం పేరు సరిచూడండి.\n\nఉదా: CROP-గుంటూరు"
                }
            
            season_service = SeasonService()
            season = season_service.get_season()
            season_te = {"Kharif": "ఖరీఫ్", "Rabi": "రబీ", "Zaid": "జైద్"}.get(season, season)
            
            ml_service = get_ml_recommender()
            recs = ml_service.get_recommendations(
                soil_type=soil_data.get("soil", "Loamy"),
                season=season,
                temp=28,
                humidity=60
            )[:3]
            
            monitoring_service = get_crop_monitoring_service()
            
            message = f"""🌾 *{location.upper()} పంట సిఫార్సులు*

🌱 మట్టి: {soil_data.get('soil', 'N/A')} | 📅 {season_te}

✅ *టాప్ పంటలు:*"""
            
            for i, rec in enumerate(recs, 1):
                crop = rec.get('crop', 'N/A')
                crop_te = CROP_NAMES_TE.get(crop, crop)
                crop_data = monitoring_service.stages.get('crops', {}).get(crop, {})
                duration = crop_data.get('total_duration_days', 120)
                
                message += f"\n{i}. *{crop_te}* - {rec.get('confidence', 85)}%"
                message += f" ({duration} రోజులు)"
            
            message += "\n\n📲 _సబ్‌స్క్రైబ్ > రోజువారీ ప్లాన్_"
            
            return {"type": "text", "to": to_number, "body": message}
            
        except Exception as e:
            logger.error(f"Crop location error: {e}")
            return {"type": "text", "to": to_number, "body": "❌ లోపం. మళ్ళీ ప్రయత్నించండి."}
    
    def _handle_subsidy_list(self, to_number: str) -> Dict:
        """Send list of subsidies."""
        message = """📋 *AP రైతు సబ్సిడీలు & పథకాలు*

1️⃣ అన్నదాత సుఖీభవ - ₹20,000/సం
2️⃣ వడ్డీ రహిత రుణాలు - ₹3L వరకు
3️⃣ యంత్రాల సబ్సిడీ - 50% తగ్గింపు
4️⃣ డ్రిప్ ఇరిగేషన్ - 80-90% సబ్సిడీ
5️⃣ పంట బీమా (PMFBY) - 2% ప్రీమియం

*వివరాలకు SUB-1 నుండి SUB-5 టైప్ చేయండి*

📞 హెల్ప్‌లైన్: 1902"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    def _handle_subsidy_detail(self, to_number: str, sub_id: int) -> Dict:
        """Send detailed info about a specific subsidy."""
        subsidies = {
            1: """💰 *అన్నదాత సుఖీభవ*

✅ మొత్తం: ₹20,000/సంవత్సరం
📅 రెండు విడతలు: ఖరీఫ్ + రబీ

*అర్హత:*
• AP రైతు ఉండాలి
• భూమి రికార్డు ఉండాలి
• ఆధార్ లింక్ అవసరం

📞 సంప్రదించండి: 1902
🌐 meekosam.ap.gov.in""",
            2: """💵 *వడ్డీ రహిత పంట రుణాలు*

✅ మొత్తం: ₹3,00,000 వరకు
📊 వడ్డీ: 0% (ప్రభుత్వ సబ్సిడీ)

*అర్హత:*
• చిన్న/సన్న రైతులు
• వ్యవసాయ భూమి ఉండాలి

📍 మీ బ్యాంక్/PACS సంప్రదించండి
📞 1800-180-1551""",
            3: """🚜 *వ్యవసాయ యంత్రాల సబ్సిడీ*

✅ సబ్సిడీ: 50% ధర తగ్గింపు
🛠️ ట్రాక్టర్, హార్వెస్టర్, స్ప్రేయర్

*అర్హత:*
• AP రైతు
• 2 ఎకరాలు+ భూమి

📍 వ్యవసాయ శాఖ కార్యాలయం
📞 1902""",
            4: """💧 *డ్రిప్/స్ప్రింక్లర్ ఇరిగేషన్*

✅ సబ్సిడీ: 80-90%
💧 నీటి ఆదా: 40-60%
📈 దిగుబడి పెరుగుదల: 20-30%

*అర్హత:*
• ఏ రైతైనా దరఖాస్తు చేయవచ్చు

📍 హార్టికల్చర్ డిపార్ట్‌మెంట్
📞 1800-180-1551""",
            5: """🛡️ *ప్రధాన మంత్రి ఫసల్ బీమా*

✅ ప్రీమియం: కేవలం 2%
🌾 ఖరీఫ్, రబీ పంటలకు

*ఆవరించేవి:*
• ప్రకృతి వైపరీత్యాలు
• తెగుళ్లు/రోగాలు
• పంట నష్టం

📍 బ్యాంక్/CSC సెంటర్
📞 1800-180-1551"""
        }
        
        if sub_id in subsidies:
            return {"type": "text", "to": to_number, "body": subsidies[sub_id]}
        else:
            return {"type": "text", "to": to_number, "body": "❌ సబ్సిడీ కనుగొనబడలేదు.\n\nSUB-1 నుండి SUB-5 వరకు ట్రై చేయండి."}
    
    def _handle_weather(self, to_number: str, lat: float, lon: float) -> Dict:
        """Send weather information."""
        try:
            from services.weather_service import WeatherService
            
            weather_service = WeatherService()
            weather = weather_service.get_current_weather(lat, lon)
            forecast = weather_service.get_forecast(lat, lon)
            
            message = f"""🌤️ *వాతావరణ సమాచారం*

🌡️ ఉష్ణోగ్రత: {weather.get('temp', '--')}°C
💧 తేమ: {weather.get('humidity', '--')}%
☁️ {weather.get('desc', 'N/A')}

*రాబోయే రోజులు:*
{forecast.get('outlook', 'మంచి వాతావరణం ఉంటుంది')}

📍 _లొకేషన్ షేర్ చేస్తే మీ ప్రాంత వాతావరణం చెప్తాను_"""
            
            return {"type": "text", "to": to_number, "body": message}
            
        except Exception as e:
            return {"type": "text", "to": to_number, "body": "🌤️ వాతావరణం లోడ్ అవుతోంది...\n\n📍 మీ లొకేషన్ షేర్ చేయండి"}
    
    def _handle_market_prices(self, to_number: str) -> Dict:
        """Send current market prices."""
        message = """💰 *మార్కెట్ ధరలు (MSP 2024-25)*

🌾 *ధాన్యాలు:*
• వరి (Paddy): ₹2,183/క్వి
• గోధుమ (Wheat): ₹2,275/క్వి
• మొక్కజొన్న (Maize): ₹2,090/క్వి

🧶 *వాణిజ్య పంటలు:*
• పత్తి (Cotton): ₹6,620/క్వి ↑
• చెరకు (Sugarcane): ₹315/క్వి

🌶️ *ఇతరాలు:*
• మిరప (Chilli): ₹12,000/క్వి
• పసుపు (Turmeric): ₹8,500/క్వి ↑
• వేరుశెనగ: ₹5,850/క్వి

_ధరలు రోజుకు మారవచ్చు_
📞 మార్కెట్ హెల్ప్‌లైన్: 14461"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    def _handle_pest_help(self, to_number: str) -> Dict:
        """Instructions for pest/disease identification."""
        message = """🔍 *తెగులు/రోగం గుర్తింపు*

📸 *మీ పంట ఫోటో పంపండి!*

ఆకు/కాయ/మొక్క ఫోటో పంపితే:
• తెగులు గుర్తించి చెప్తాం
• మందు సిఫార్సు ఇస్తాం
• నివారణ చర్యలు చెప్తాం

*ఫోటో తీసేటప్పుడు:*
✅ దగ్గరగా తీయండి
✅ మంచి వెలుగులో
✅ లక్షణాలు స్పష్టంగా కనిపించేలా

📍 ప్రత్యక్ష సహాయం: సమీప RBK సందర్శించండి
📞 హెల్ప్‌లైన్: 1902"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    def _handle_image(self, to_number: str, media_url: str) -> Dict:
        """Handle image upload for pest detection."""
        # In a full implementation, this would call a pest detection ML model
        message = """📸 *ఫోటో అందింది!*

🔍 విశ్లేషణ జరుగుతోంది...

_త్వరలో ఫలితాలు వస్తాయి_

💡 *సలహా:* అనుమానంగా ఉంటే సమీప RBK సందర్శించి నిపుణులను సంప్రదించండి.

📞 హెల్ప్‌లైన్: 1902"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    def _handle_free_text(self, to_number: str, message: str) -> Dict:
        """Handle free-form text questions."""
        # Could integrate with chatbot service here
        response = f"""🤔 మీ ప్రశ్న: "{message}"

మీకు సహాయం చేయడానికి:

1️⃣ *పంట సిఫార్సులు* కోసం "1" టైప్ చేయండి
2️⃣ *సబ్సిడీలు* కోసం "2" టైప్ చేయండి
3️⃣ *వాతావరణం* కోసం "3" టైప్ చేయండి
4️⃣ *మార్కెట్ ధరలు* కోసం "4" టైప్ చేయండి
5️⃣ *తెగులు గుర్తింపు* కోసం పంట ఫోటో పంపండి

📍 లొకేషన్ షేర్ చేయండి - మీ ప్రాంత సిఫార్సులు ఇస్తాం!"""
        
        return {"type": "text", "to": to_number, "body": response}
    
    def _send_help(self, to_number: str) -> Dict:
        """Send help message."""
        message = """📚 *కిసాన్‌మిత్ర సహాయం*

*కమాండ్లు:*
• *1* - పంట సిఫార్సులు
• *2* - సబ్సిడీలు/పథకాలు
• *3* - వాతావరణం
• *4* - మార్కెట్ ధరలు
• *5* - తెగులు గుర్తింపు
• *CROP-గుంటూరు* - ప్రాంత పంటలు
• *SUB-1* - సబ్సిడీ వివరాలు

*ఫీచర్లు:*
📍 లొకేషన్ షేర్ → పంట సిఫార్సులు
📸 ఫోటో పంపు → తెగులు గుర్తింపు

📞 హెల్ప్‌లైన్: 1902
🌐 KisanMitra App: kisanmitra.app"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    # ============ MARKETPLACE HANDLERS ============
    
    def _check_farmer_registered(self, phone: str) -> Optional[Dict]:
        """Check if farmer is registered in the system."""
        try:
            # Clean phone number
            clean_phone = phone.replace("whatsapp:", "").replace("+", "")
            resp = requests.get(f"{BACKEND_API}/farmers/phone/{clean_phone}", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("farmer")
        except Exception as e:
            logger.error(f"Farmer lookup error: {e}")
        return None
    
    def _handle_marketplace_menu(self, to_number: str) -> Dict:
        """Show marketplace menu, check if farmer is registered."""
        farmer = self._check_farmer_registered(to_number)
        
        if farmer:
            session = {"state": "marketplace", "farmer": farmer}
            self.user_sessions[to_number] = session
            
            message = f"""🏪 *కిసాన్‌మిత్ర మార్కెట్‌ప్లేస్*

స్వాగతం, *{farmer.get('name', 'రైతు')}*! 👨‍🌾

మీరు ఏం చేయాలనుకుంటున్నారు?

A️⃣ నా లిస్టింగ్‌లు చూడండి
B️⃣ కొత్త పంట జాబితా చేయండి
C️⃣ అందుబాటులో ఉన్న పంటలు చూడండి

*అక్షరం టైప్ చేయండి (A/B/C)*"""
        else:
            # New user - need to register
            session = {"state": "awaiting_registration", "step": "name"}
            self.user_sessions[to_number] = session
            
            message = """🏪 *కిసాన్‌మిత్ర మార్కెట్‌ప్లేస్‌కు స్వాగతం!*

మార్కెట్‌ప్లేస్ వాడటానికి ముందు మిమ్మల్ని రిజిస్టర్ చేసుకోవాలి.

👤 *మీ పేరు చెప్పండి:*

(ఉదా: రాము, సీతారామయ్య)"""
        
        return {"type": "text", "to": to_number, "body": message}
    
    def _handle_registration(self, to_number: str, message: str, session: Dict) -> Dict:
        """Handle farmer registration flow."""
        step = session.get("step", "name")
        reg_data = session.get("reg_data", {})
        
        if step == "name":
            reg_data["name"] = message
            session["reg_data"] = reg_data
            session["step"] = "village"
            self.user_sessions[to_number] = session
            
            return {"type": "text", "to": to_number, "body": f"👋 నమస్తే *{message}*!\n\n🏘️ *మీ గ్రామం/మండలం పేరు:*"}
        
        elif step == "village":
            reg_data["village"] = message
            session["reg_data"] = reg_data
            session["step"] = "district"
            self.user_sessions[to_number] = session
            
            return {"type": "text", "to": to_number, "body": "📍 *మీ జిల్లా పేరు:*"}
        
        elif step == "district":
            reg_data["district"] = message
            # Register the farmer
            clean_phone = to_number.replace("whatsapp:", "").replace("+", "")
            
            try:
                resp = requests.post(f"{BACKEND_API}/farmers", json={
                    "name": reg_data["name"],
                    "phone": clean_phone,
                    "village": reg_data["village"],
                    "district": reg_data["district"]
                }, timeout=5)
                
                if resp.status_code in [200, 201]:
                    farmer = resp.json().get("farmer", reg_data)
                    session = {"state": "marketplace", "farmer": farmer}
                    self.user_sessions[to_number] = session
                    
                    return {"type": "text", "to": to_number, "body": f"""✅ *రిజిస్ట్రేషన్ విజయవంతం!*

👤 పేరు: {reg_data['name']}
🏘️ గ్రామం: {reg_data['village']}
📍 జిల్లా: {reg_data['district']}

ఇప్పుడు మీరు పంటలు అమ్మవచ్చు!

A️⃣ నా లిస్టింగ్‌లు
B️⃣ కొత్త లిస్టింగ్
C️⃣ పంటలు చూడండి"""}
            except Exception as e:
                logger.error(f"Registration error: {e}")
            
            # Fallback - save locally in session
            session = {"state": "marketplace", "farmer": reg_data}
            self.user_sessions[to_number] = session
            return {"type": "text", "to": to_number, "body": "✅ రిజిస్ట్రేషన్ అయింది!\n\nB టైప్ చేసి పంట లిస్ట్ చేయండి."}
        
        return self._handle_marketplace_menu(to_number)
    
    def _handle_my_listings(self, to_number: str) -> Dict:
        """Show farmer's listings."""
        try:
            clean_phone = to_number.replace("whatsapp:", "").replace("+", "")
            resp = requests.get(f"{BACKEND_API}/listings?seller_phone={clean_phone}", timeout=5)
            
            if resp.status_code == 200:
                listings = resp.json().get("listings", [])
                
                if not listings:
                    return {"type": "text", "to": to_number, "body": "📦 మీకు ఇంకా లిస్టింగ్‌లు లేవు.\n\n*B* టైప్ చేసి కొత్త లిస్టింగ్ చేయండి!"}
                
                message = "📦 *మీ లిస్టింగ్‌లు:*\n"
                for i, listing in enumerate(listings[:5], 1):
                    crop = listing.get("crop", "N/A")
                    qty = listing.get("quantity", 0)
                    price = listing.get("price", 0)
                    status = "✅" if listing.get("status") == "active" else "❌"
                    message += f"\n{i}. {status} *{crop}* - {qty} క్వి @ ₹{price}"
                
                message += "\n\n*B* - కొత్త లిస్టింగ్"
                return {"type": "text", "to": to_number, "body": message}
        except Exception as e:
            logger.error(f"Listings fetch error: {e}")
        
        return {"type": "text", "to": to_number, "body": "❌ లిస్టింగ్‌లు లోడ్ కాలేదు. మళ్ళీ ప్రయత్నించండి."}
    
    def _start_listing_flow(self, to_number: str) -> Dict:
        """Start the listing creation flow."""
        session = self.user_sessions.get(to_number, {})
        session["state"] = "listing_crop"
        session["listing_data"] = {}
        self.user_sessions[to_number] = session
        
        return {"type": "text", "to": to_number, "body": """🌾 *కొత్త లిస్టింగ్ తయారు చేయండి*

ఏ పంట అమ్మాలనుకుంటున్నారు?

(ఉదా: వరి, పత్తి, మిరప, వేరుశెనగ)

*cancel* - రద్దు చేయడానికి"""}
    
    def _handle_listing_flow(self, to_number: str, message: str, session: Dict) -> Dict:
        """Handle multi-step listing creation."""
        state = session.get("state", "")
        listing_data = session.get("listing_data", {})
        
        if message.lower() in ["cancel", "రద్దు"]:
            self.user_sessions[to_number] = {"state": "menu"}
            return {"type": "text", "to": to_number, "body": "❌ రద్దు అయింది.\n\n*menu* - మెయిన్ మెనూ"}
        
        if state == "listing_crop":
            listing_data["crop"] = message
            session["listing_data"] = listing_data
            session["state"] = "listing_price"
            self.user_sessions[to_number] = session
            
            crop_te = CROP_NAMES_TE.get(message.title(), message)
            return {"type": "text", "to": to_number, "body": f"🌾 పంట: *{crop_te}*\n\n💰 *ధర ఎంత? (₹/క్వింటాల్)*\n\nఉదా: 2500"}
        
        elif state == "listing_price":
            try:
                price = int(message.replace(",", "").replace("₹", ""))
                listing_data["price"] = price
            except:
                return {"type": "text", "to": to_number, "body": "❌ సరైన ధర టైప్ చేయండి.\n\nఉదా: 2500"}
            
            session["listing_data"] = listing_data
            session["state"] = "listing_quantity"
            self.user_sessions[to_number] = session
            
            return {"type": "text", "to": to_number, "body": f"💰 ధర: *₹{price}/క్వి*\n\n📦 *ఎంత పరిమాణం (క్వింటాల్లో)?*\n\nఉదా: 10"}
        
        elif state == "listing_quantity":
            try:
                qty = float(message.replace(",", ""))
                listing_data["quantity"] = qty
            except:
                return {"type": "text", "to": to_number, "body": "❌ సరైన పరిమాణం టైప్ చేయండి.\n\nఉదా: 10"}
            
            session["listing_data"] = listing_data
            session["state"] = "listing_location"
            self.user_sessions[to_number] = session
            
            return {"type": "text", "to": to_number, "body": f"📦 పరిమాణం: *{qty} క్వింటాళ్లు*\n\n📍 *మీ లొకేషన్ షేర్ చేయండి*\n\nలేదా గ్రామం పేరు టైప్ చేయండి"}
        
        elif state == "listing_location":
            listing_data["location"] = message
            session["listing_data"] = listing_data
            session["state"] = "listing_image"
            self.user_sessions[to_number] = session
            
            return {"type": "text", "to": to_number, "body": f"📍 స్థలం: *{message}*\n\n📸 *పంట ఫోటో పంపండి* (ఐచ్ఛికం)\n\nలేదా *skip* టైప్ చేయండి"}
        
        elif state == "listing_image":
            if message.lower() in ["skip", "వదిలేయండి"]:
                listing_data["image_url"] = None
                return self._finalize_listing(to_number, session)
            return {"type": "text", "to": to_number, "body": "📸 ఫోటో పంపండి లేదా *skip* చేయండి"}
        
        return self._send_main_menu(to_number)
    
    def _finalize_listing(self, to_number: str, session: Dict) -> Dict:
        """Submit the listing to backend."""
        listing_data = session.get("listing_data", {})
        farmer = session.get("farmer", {})
        
        try:
            clean_phone = to_number.replace("whatsapp:", "").replace("+", "")
            
            payload = {
                "crop": listing_data.get("crop"),
                "price": listing_data.get("price"),
                "quantity": listing_data.get("quantity"),
                "location": listing_data.get("location"),
                "image_url": listing_data.get("image_url"),
                "seller_phone": clean_phone,
                "seller_name": farmer.get("name", "WhatsApp రైతు")
            }
            
            resp = requests.post(f"{BACKEND_API}/listings", json=payload, timeout=5)
            
            if resp.status_code in [200, 201]:
                self.user_sessions[to_number] = {"state": "marketplace", "farmer": farmer}
                
                crop = listing_data.get("crop", "N/A")
                return {"type": "text", "to": to_number, "body": f"""✅ *లిస్టింగ్ విజయవంతం!*

🌾 పంట: *{crop}*
💰 ధర: ₹{listing_data.get('price')}/క్వి
📦 పరిమాణం: {listing_data.get('quantity')} క్వి
📍 స్థలం: {listing_data.get('location')}

మీ లిస్టింగ్ ఇప్పుడు మార్కెట్‌ప్లేస్‌లో చూడవచ్చు!

*A* - నా లిస్టింగ్‌లు
*menu* - మెయిన్ మెనూ"""}
        except Exception as e:
            logger.error(f"Listing submission error: {e}")
        
        self.user_sessions[to_number] = {"state": "menu"}
        return {"type": "text", "to": to_number, "body": "❌ లిస్టింగ్ సేవ్ కాలేదు. మళ్ళీ ప్రయత్నించండి."}
    
    def _handle_browse_listings(self, to_number: str) -> Dict:
        """Browse available listings."""
        try:
            resp = requests.get(f"{BACKEND_API}/listings?status=active&limit=5", timeout=5)
            
            if resp.status_code == 200:
                listings = resp.json().get("listings", [])
                
                if not listings:
                    return {"type": "text", "to": to_number, "body": "📦 ప్రస్తుతం లిస్టింగ్‌లు లేవు.\n\n*B* - మీ పంట లిస్ట్ చేయండి"}
                
                message = "🛒 *అందుబాటులో ఉన్న పంటలు:*\n"
                for i, listing in enumerate(listings, 1):
                    crop = listing.get("crop", "N/A")
                    qty = listing.get("quantity", 0)
                    price = listing.get("price", 0)
                    seller = listing.get("seller_name", "రైతు")
                    loc = listing.get("location", "")[:15]
                    message += f"\n{i}. *{crop}* - {qty} క్వి\n   💰 ₹{price}/క్వి | 📍 {loc}"
                
                message += "\n\n_వివరాలకు సంప్రదించండి_"
                return {"type": "text", "to": to_number, "body": message}
        except Exception as e:
            logger.error(f"Browse listings error: {e}")
        
        return {"type": "text", "to": to_number, "body": "❌ లిస్టింగ్‌లు లోడ్ కాలేదు."}
    
    def _error_response(self, to_number: str) -> Dict:
        """Send error response."""
        return {
            "type": "text",
            "to": to_number,
            "body": "❌ లోపం జరిగింది. మళ్ళీ ప్రయత్నించండి.\n\n📞 సహాయం: 1902"
        }
    
    def send_message(self, to_number: str, body: str, media_url: str = None) -> bool:
        """
        Send a WhatsApp message via Twilio.
        
        Args:
            to_number: Recipient's WhatsApp number (with country code)
            body: Message text
            media_url: Optional image/document URL
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.warning("WhatsApp sending disabled - no Twilio credentials")
            return False
        
        try:
            to_whatsapp = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
            
            message_params = {
                "from_": self.whatsapp_number,
                "to": to_whatsapp,
                "body": body
            }
            
            if media_url:
                message_params["media_url"] = [media_url]
            
            message = self.client.messages.create(**message_params)
            logger.info(f"WhatsApp message sent: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return False


# Singleton instance
_whatsapp_bot = None

def get_whatsapp_bot() -> WhatsAppBotService:
    global _whatsapp_bot
    if _whatsapp_bot is None:
        _whatsapp_bot = WhatsAppBotService()
    return _whatsapp_bot
