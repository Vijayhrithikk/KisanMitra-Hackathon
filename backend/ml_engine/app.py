from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.season_service import SeasonService
from services.soil_service import SoilService
from services.recommendation_service import RecommendationService
from services.ml_recommendation_service import MLRecommendationService
from services.weather_service import WeatherService
from services.soil_image_service import get_classifier
from services.sms_bot_service import get_sms_bot
from services.alert_service import get_alert_service
from services.pest_warning_service import get_pest_warning_service
from services.crop_calendar_service import get_crop_calendar_service
from services.daily_advisory_service import get_daily_advisory_service
# Decision Intelligence Services (Hackathon Enhancement)
from services.decision_simulator_service import decision_simulator
from services.counterfactual_engine import counterfactual_engine
from services.explainability_service import explainability_service
from services.confidence_scoring_service import confidence_scorer
# Tier 1: Real-world data integrations
from services.market_price_service import get_market_price_service
from services.weather_history_service import get_weather_history_service
from services.soil_research_agent import get_soil_research_agent
from services.nasa_power_service import get_nasa_power_service
# Crop Monitoring Services
from services.crop_monitoring_service import get_crop_monitoring_service
from services.crop_faq_service import get_crop_faq_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
import os
# Search for .env in current, parent, and ../.. directories
env_paths = [
    os.path.join(os.getcwd(), '.env'),
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
]
for path in env_paths:
    if os.path.exists(path):
        load_dotenv(path)
        break
else:
    load_dotenv() # Fallback to default

app = FastAPI(title="KisanMitra ML Engine", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
season_service = SeasonService()
soil_service = SoilService()
recommendation_service = RecommendationService()  # Rule-based (backup)
ml_recommendation_service = MLRecommendationService()  # ML-trained
weather_service = WeatherService()


class LocationRequest(BaseModel):
    location_name: str
    manual_soil_type: str = None
    lat: float = None
    lon: float = None
    include_risk_analysis: bool = True  # NEW: Enable decision-grade analysis
    show_alternatives: bool = True      # NEW: Show why-not explanations
    # Custom NPK values from soil report
    custom_npk: dict = None  # Format: {"n": 150, "p": 50, "k": 200, "ph": 7.0}

class SoilImageRequest(BaseModel):
    image_base64: str  # Base64 encoded image

class SMSRequest(BaseModel):
    message: str
    sender: str = None

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "ml_engine", "version": "1.2.0"}

@app.post("/sms-webhook")
async def handle_sms(request: SMSRequest):
    """
    SMS webhook endpoint for Termux integration.
    Returns multi-part SMS responses for CROP-city, SUB, SCH commands.
    All responses in Telugu.
    """
    logger.info(f"SMS received from {request.sender}: {request.message}")
    
    try:
        bot = get_sms_bot()
        
        # Check if valid command
        if not bot.is_valid_command(request.message):
            logger.info(f"Ignoring invalid command: {request.message}")
            return {
                "success": True,
                "should_respond": False,
                "responses": [],
                "command": request.message.strip().upper()
            }
        
        # Get multi-part responses
        responses = bot.handle_command(request.message)
        
        logger.info(f"SMS response: {len(responses)} parts")
        
        return {
            "success": True,
            "should_respond": True,
            "responses": responses,  # List of SMS parts
            "response": responses[0] if responses else None,  # First part for backward compat
            "total_parts": len(responses),
            "command": request.message.strip().upper()
        }
    except Exception as e:
        logger.error(f"SMS processing error: {e}")
        return {
            "success": False,
            "should_respond": True,
            "responses": ["❌ లోపం. మళ్ళీ ప్రయత్నించండి."],
            "response": "❌ లోపం. మళ్ళీ ప్రయత్నించండి.",
            "error": str(e)
        }

@app.post("/classify-soil")
async def classify_soil_image(file: UploadFile = File(...)):
    """
    Classify soil type from an uploaded image.
    
    Accepts: multipart/form-data with 'file' field containing an image
    Returns: Soil classification with confidence, Telugu name, and soil parameters
    """
    logger.info(f"Received soil classification request: {file.filename}")
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Validate file type - check content type or file extension
        content_type = file.content_type or ""
        filename = file.filename or ""
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        is_valid_image = content_type.startswith("image/") or filename.lower().endswith(valid_extensions)
        
        if not is_valid_image and len(image_bytes) > 0:
            # Try to detect if it's an image by checking magic bytes
            is_valid_image = (
                image_bytes[:8] == b'\x89PNG\r\n\x1a\n' or  # PNG
                image_bytes[:2] == b'\xff\xd8' or  # JPEG
                image_bytes[:6] in (b'GIF87a', b'GIF89a')  # GIF
            )
        
        if not is_valid_image:
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Get classifier and predict
        classifier = get_classifier()
        result = classifier.classify(image_bytes)
        
        logger.info(f"Classification result: {result['soil_type']} ({result['confidence']:.2f})")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying soil image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify-soil-base64")
async def classify_soil_base64(request: SoilImageRequest):
    """
    Classify soil type from a base64 encoded image.
    
    Useful for direct API calls from frontend without multipart form.
    """
    logger.info("Received base64 soil classification request")
    
    try:
        # Get classifier and predict
        classifier = get_classifier()
        result = classifier.classify(request.image_base64)
        
        logger.info(f"Classification result: {result['soil_type']} ({result['confidence']:.2f})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error classifying soil image: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/recommend")
async def recommend_crops(request: LocationRequest):
    """
    Enhanced endpoint with:
    - Decision simulation (loss probabilities, risk breakdown)
    - Confidence scoring (data quality transparency)
    - Farmer-friendly explanations (Telugu/English)
    """
    logger.info(f"Recommendation request: {request.location_name}, Coords: {request.lat},{request.lon}, Manual: {request.manual_soil_type}")
    
    try:
        location = request.location_name
        
        # 1. Season
        season_info = season_service.get_current_season_details()
        current_season = season_info["season"]
        
        # 2. Parse location
        parts = location.split(',')
        if len(parts) > 1:
            mandal = parts[0].strip()
            district = parts[1].strip()
        else:
            mandal = None
            district = parts[0].strip()
        
        # 3. Soil: Try database first, then AI research if unknown
        soil_info = soil_service.get_soil_info(district, mandal)
        soil_source = "database"
        soil_classification_confidence = None
        
        # Auto-research if region is unknown
        if soil_info.get("zone") == "Unknown Region" and not request.manual_soil_type:
            logger.info(f"Unknown region '{district}' - triggering AI research...")
            try:
                from services.soil_research_agent import SoilResearchAgent
                agent = SoilResearchAgent()
                researched = agent.research_soil(
                    region=mandal or district,
                    district=district
                )
                if researched:
                    soil_info = researched
                    soil_source = "ai_researched"
                    logger.info(f"AI research found: {soil_info['soil']} (source: {soil_info.get('source', 'unknown')})")
            except Exception as e:
                logger.warning(f"Research failed: {e}")

        # Manual override
        if request.manual_soil_type:
            logger.info(f"Overriding to manual: {request.manual_soil_type}")
            soil_info["soil"] = request.manual_soil_type
            soil_source = "user_selected"
            
            # Soil-specific defaults
            soil_defaults = {
                "Red Sandy Loam": {"ph": 6.5, "n": 180, "p": 45, "k": 200},
                "Black Cotton": {"ph": 8.0, "n": 200, "p": 55, "k": 320},
                "Alluvial": {"ph": 7.2, "n": 240, "p": 65, "k": 280},
                "Clay": {"ph": 7.5, "n": 160, "p": 50, "k": 250},
                "Sandy": {"ph": 6.0, "n": 140, "p": 40, "k": 180},
                "Laterite": {"ph": 5.5, "n": 120, "p": 35, "k": 150},
                "Loamy": {"ph": 6.8, "n": 200, "p": 60, "k": 220},
            }
            if request.manual_soil_type in soil_defaults:
                soil_info.update(soil_defaults[request.manual_soil_type])
            
            soil_info["zone"] = "User Selected"
            if district:
                soil_service.update_soil_db(district, mandal, request.manual_soil_type)
        
        # Custom NPK from soil report (highest priority override)
        if request.custom_npk:
            logger.info(f"Using custom NPK from soil report: {request.custom_npk}")
            if 'n' in request.custom_npk:
                soil_info["n"] = float(request.custom_npk["n"])
            if 'p' in request.custom_npk:
                soil_info["p"] = float(request.custom_npk["p"])
            if 'k' in request.custom_npk:
                soil_info["k"] = float(request.custom_npk["k"])
            if 'ph' in request.custom_npk:
                soil_info["ph"] = float(request.custom_npk["ph"])
            soil_source = "soil_report"
        
        # 4. Weather: Current + Forecast
        lat = request.lat if request.lat else 17.3850
        lon = request.lon if request.lon else 78.4867
        
        weather = weather_service.get_current_weather(lat, lon) 
        forecast = weather_service.get_forecast(lat, lon)
        
        current_temp = weather.get('temp', 28)
        current_humidity = weather.get('humidity', 60)
        
        # Analyze forecast for summary
        forecast_analysis = recommendation_service._analyze_forecast(forecast)
        weather_summary = recommendation_service.get_weather_summary(forecast_analysis)

        # Smart Temp: Use forecast day temp if current temp is too low (night)
        effective_temp = current_temp
        if current_temp < 20 and forecast and 'daily' in forecast and len(forecast['daily']) > 0:
            effective_temp = forecast['daily'][0]['temp']
            logger.info(f"Night/Cold detected ({current_temp}C). Using forecast temp ({effective_temp}C) for ML.")

        # 5. Generate ML-Based Recommendations (with fallback to rule-based)
        recommendations = []
        try:
            recommendations = ml_recommendation_service.get_recommendations(
                soil_type=soil_info["soil"],
                season=current_season,
                temp=effective_temp,
                humidity=current_humidity,
                soil_ph=soil_info.get("ph", 7.0),
                soil_n=soil_info.get("n", 150),
                soil_p=soil_info.get("p", 50),
                soil_k=soil_info.get("k", 150),
                forecast=forecast_analysis,
                soil_source=soil_source
            )
            
            if not recommendations:
                logger.warning("ML model returned 0 crops. Falling back to rule-based.")
                raise ValueError("No ML recommendations")

            model_type = "ml_trained"
        except Exception as e:
            logger.warning(f"ML model failed (or empty), using rule-based: {e}")
            recommendations = recommendation_service.get_recommendations(
                soil_type=soil_info["soil"],
                season=current_season,
                temp=current_temp,
                humidity=current_humidity,
                soil_ph=soil_info.get("ph", 7.0),
                soil_n=soil_info.get("n", 150),
                soil_p=soil_info.get("p", 50),
                soil_k=soil_info.get("k", 150),
                forecast=forecast,
                soil_source=soil_source
            )
            model_type = "rule_based"

        # 6. HACKATHON ENHANCEMENT: Decision Simulation
        if request.include_risk_analysis and recommendations:
            try:
                # Add forecast data for risk calculation
                enhanced_forecast = {
                    **forecast_analysis,
                    'avg_temp': current_temp,
                    'avg_humidity': current_humidity
                }
                
                enhanced_recommendations = decision_simulator.simulate_decision(
                    recommendations=recommendations,
                    weather_forecast=enhanced_forecast,
                    soil_params={"ph": soil_info.get("ph", 7.0), 
                               "n": soil_info.get("n", 150),
                               "p": soil_info.get("p", 50),
                               "k": soil_info.get("k", 150)},
                    context={"season": current_season, "location": location}
                )
                recommendations = enhanced_recommendations
                logger.info("Decision simulation complete - risk analysis added")
            except Exception as e:
                logger.warning(f"Decision simulation failed: {e}, continuing without")

        # 7. HACKATHON ENHANCEMENT: Confidence Scoring
        soil_confidence = confidence_scorer.score_soil_data(
            soil_type=soil_info["soil"],
            source=soil_source,
            classification_confidence=soil_classification_confidence
        )
        
        weather_confidence = confidence_scorer.score_weather_data(
            source='openweather_forecast',
            forecast_hours=72
        )
        
        ml_confidence = confidence_scorer.score_ml_prediction(
            ml_confidence=recommendations[0].get('confidence', 70) if recommendations else 70,
            model_type=model_type,
            data_completeness=1.0
        )
        
        overall_confidence = confidence_scorer.aggregate_confidence(
            soil_conf=soil_confidence,
            weather_conf=weather_confidence,
            ml_conf=ml_confidence
        )

        # 8. HACKATHON ENHANCEMENT: Add explanations
        if request.show_alternatives and recommendations:
            for rec in recommendations:
                try:
                    # Add English explanation
                    explanation_en = explainability_service.explain_recommendation(
                        crop=rec['crop'],
                        recommendation=rec,
                        language='en'
                    )
                    rec['explanation_en'] = explanation_en
                    
                    # Add Telugu explanation
                    explanation_te = explainability_service.explain_recommendation(
                        crop=rec['crop'],
                        recommendation=rec,
                        language='te'
                    )
                    rec['explanation_te'] = explanation_te
                    
                    # Add "why not" explanation
                    rec['why_not'] = explainability_service.explain_why_not(
                        crop=rec['crop'],
                        rec=rec,
                        language='en'
                    )
                except Exception as e:
                    logger.warning(f"Explanation generation failed for {rec.get('crop')}: {e}")

        # ============== PARALLEL DATA ENHANCEMENT (Steps 9-11) ==============
        # Run Market Prices, Weather History, and NASA Forecast in parallel
        # This reduces response time by 50-70%
        
        market_prices_result = None
        weather_history = {}
        nasa_forecast = {}
        
        def fetch_market_prices():
            """Fetch live market prices from AGMARKNET"""
            try:
                market_service = get_market_price_service()
                return market_service.get_prices_for_recommendations(
                    recommendations.copy(),  # Copy to avoid threading issues
                    state="Andhra Pradesh",
                    district=district
                )
            except Exception as e:
                logger.warning(f"Market price fetch failed: {e}")
                return None
        
        def fetch_weather_history():
            """Fetch IMD weather history and crop water analysis"""
            try:
                weather_hist_service = get_weather_history_service()
                history = weather_hist_service.get_district_weather_summary(
                    state="Andhra Pradesh",
                    district=district
                )
                return {
                    'summary': history,
                    'service': weather_hist_service
                }
            except Exception as e:
                logger.warning(f"Weather history fetch failed: {e}")
                return None
        
        def fetch_nasa_forecast():
            """Fetch NASA Power 3-month growing season forecast"""
            try:
                lat_val = request.lat or 16.3067
                lon_val = request.lon or 80.4365
                
                current_month = datetime.now().month
                if current_season == "Kharif":
                    start_month = 6
                elif current_season == "Rabi":
                    start_month = 10
                else:
                    start_month = current_month
                
                nasa_service = get_nasa_power_service()
                return nasa_service.get_growing_season_forecast(
                    lat=lat_val,
                    lon=lon_val,
                    start_month=start_month,
                    duration_months=3
                )
            except Exception as e:
                logger.warning(f"NASA forecast fetch failed: {e}")
                return {}
        
        # Execute all data fetches in parallel
        logger.info("Starting parallel data enhancement...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(fetch_market_prices): 'market',
                executor.submit(fetch_weather_history): 'weather_history',
                executor.submit(fetch_nasa_forecast): 'nasa'
            }
            
            for future in as_completed(futures, timeout=30):
                task_name = futures[future]
                try:
                    result = future.result()
                    if task_name == 'market' and result:
                        market_prices_result = result
                        logger.info("Parallel: Market prices completed")
                    elif task_name == 'weather_history' and result:
                        weather_history = result.get('summary', {})
                        # Process water adequacy for each recommendation
                        wh_service = result.get('service')
                        if wh_service:
                            for rec in recommendations:
                                try:
                                    rec['water_adequacy'] = wh_service.assess_crop_water_adequacy(
                                        crop_name=rec['crop'],
                                        state="Andhra Pradesh",
                                        district=district,
                                        season=current_season
                                    )
                                    rec['historical_weather_risk'] = wh_service.calculate_weather_risk(
                                        crop_name=rec['crop'],
                                        state="Andhra Pradesh",
                                        district=district,
                                        season=current_season,
                                        current_forecast=forecast_analysis
                                    )
                                except:
                                    pass
                        logger.info("Parallel: Weather history completed")
                    elif task_name == 'nasa' and result:
                        nasa_forecast = result
                        logger.info("Parallel: NASA forecast completed")
                except Exception as e:
                    logger.warning(f"Parallel {task_name} failed: {e}")
        
        # Apply market prices to recommendations
        if market_prices_result:
            for i, rec in enumerate(recommendations):
                if i < len(market_prices_result):
                    rec['market_price'] = market_prices_result[i].get('market_price', {})
                    rec['market_price_live'] = market_prices_result[i].get('market_price_live', False)
        
        logger.info("Parallel data enhancement completed")

        return {
            "location": location,
            "model_type": model_type,
            "context": {
                "season": current_season,
                "season_desc": season_info["description"],
                "soil_type": soil_info["soil"],
                "soil_zone": soil_info.get("zone", ""),
                "soil_source": soil_source,
                "soil_params": {
                    "ph": soil_info.get("ph", 7.0),
                    "n": soil_info.get("n", 150),
                    "p": soil_info.get("p", 50),
                    "k": soil_info.get("k", 150)
                },
                "weather": {
                    "temp": current_temp,
                    "humidity": current_humidity,
                    "desc": weather.get('desc', 'Clear'),
                    "forecast_summary": weather_summary,
                    "rain_days": forecast_analysis.get("rain_days", 0),
                    "weather_risk": forecast_analysis.get("weather_risk", "Low")
                },
                # NEW: Weather history summary
                "weather_history": weather_history,
                # NEW: NASA Power 3-month growing season forecast
                "nasa_forecast": nasa_forecast,
                # NEW: Confidence metadata
                "confidence": {
                    "soil": soil_confidence,
                    "weather": weather_confidence,
                    "ml_prediction": ml_confidence,
                    "overall": overall_confidence
                }
            },
            "recommendations": recommendations
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



class SoilResearchRequest(BaseModel):
    district: str
    mandal: Optional[str] = None
    state: Optional[str] = None
    force: bool = False  # Force re-research even if data exists


@app.post("/soil/research")
async def research_soil_data(request: SoilResearchRequest):
    """
    Research soil data for a region using AI agent.
    The agent scrapes 15-20 web pages and extracts soil parameters.
    
    Args:
        district: District name
        mandal: Mandal name (optional)
        state: State name (optional, will be auto-detected)
        force: Force re-research even if data exists
    """
    logger.info(f"Soil research request: {request.district}, {request.mandal}, {request.state}, force={request.force}")
    
    try:
        if request.force:
            # Force research
            result = soil_service.force_research(request.district, request.mandal, request.state)
        else:
            # Intelligent lookup (research only if unknown)
            result = soil_service.get_soil_info_intelligent(request.district, request.mandal, request.state)
        
        if result:
            return {
                "success": True,
                "data": result,
                "source": result.get("source", "database"),
                "confidence": result.get("confidence"),
                "sources_count": result.get("sources_count")
            }
        else:
            return {
                "success": False,
                "error": "Research failed to find soil data",
                "data": soil_service.get_soil_info(request.district, request.mandal)
            }
            
    except Exception as e:
        logger.error(f"Soil research error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/soil/{district}")
async def get_soil_info(district: str, mandal: Optional[str] = None, intelligent: bool = False):
    """
    Get soil information for a district/mandal.
    
    Args:
        district: District name
        mandal: Mandal name (optional)
        intelligent: If true, use AI research for unknown regions
    """
    try:
        if intelligent:
            result = soil_service.get_soil_info_intelligent(district, mandal)
        else:
            result = soil_service.get_soil_info(district, mandal)
        
        return {
            "success": True,
            "district": district,
            "mandal": mandal,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Soil info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DECISION INTELLIGENCE ENDPOINTS (HACKATHON) ====================

class WhatIfScenarioRequest(BaseModel):
    crop: str
    current_recommendation: dict  # Full recommendation object
    scenario_type: str  # 'sowing_delay', 'rainfall_failure', 'fertilizer_reduction', 'pest_outbreak'
    # Scenario-specific parameters
    delay_days: Optional[int] = None
    failure_days: Optional[int] = None
    reduction_percent: Optional[int] = None
    outbreak_severity: Optional[str] = 'moderate'
    season: str = 'Kharif'


@app.post("/whatif-scenario")
async def simulate_whatif_scenario(request: WhatIfScenarioRequest):
    """
    HACKATHON INNOVATION: What-if scenario simulation.
    
    Prevents farming mistakes by showing consequences of decisions:
    - "What if I delay sowing by 15 days?"
    - "What if rainfall fails for 30 days?"
    - "What if I use 30% less fertilizer?"
    - "What if pest outbreak occurs?"
    """
    logger.info(f"What-if scenario: {request.scenario_type} for {request.crop}")
    
    try:
        if request.scenario_type == 'sowing_delay':
            if request.delay_days is None:
                raise HTTPException(status_code=400, detail="delay_days required for sowing_delay scenario")
            
            result = counterfactual_engine.simulate_sowing_delay(
                crop=request.crop,
                current_recommendation=request.current_recommendation,
                delay_days=request.delay_days,
                season=request.season
            )
        
        elif request.scenario_type == 'rainfall_failure':
            if request.failure_days is None:
                raise HTTPException(status_code=400, detail="failure_days required for rainfall_failure scenario")
            
            result = counterfactual_engine.simulate_rainfall_failure(
                crop=request.crop,
                current_recommendation=request.current_recommendation,
                failure_days=request.failure_days
            )
        
        elif request.scenario_type == 'fertilizer_reduction':
            if request.reduction_percent is None:
                raise HTTPException(status_code=400, detail="reduction_percent required for fertilizer_reduction scenario")
            
            result = counterfactual_engine.simulate_fertilizer_reduction(
                crop=request.crop,
                current_recommendation=request.current_recommendation,
                reduction_percent=request.reduction_percent
            )
        
        elif request.scenario_type == 'pest_outbreak':
            result = counterfactual_engine.simulate_pest_outbreak(
                crop=request.crop,
                current_recommendation=request.current_recommendation,
                outbreak_severity=request.outbreak_severity
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown scenario type: {request.scenario_type}")
        
        return {
            "success": True,
            "crop": request.crop,
            "scenario_type": request.scenario_type,
            "original": request.current_recommendation,
            "simulated": result,
            "recommendation": result.get('scenario', {}).get('recommendation', 'proceed')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"What-if scenario error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class CompareRisksRequest(BaseModel):
    crops: List[str]
    recommendations: List[dict]  # List of recommendation objects


@app.post("/compare-risks")
async def compare_crop_risks(request: CompareRisksRequest):
    """
    HACKATHON INNOVATION: Side-by-side risk comparison.
    
    Shows farmers the safest vs riskiest options with explanations.
    """
    logger.info(f"Risk comparison for {len(request.crops)} crops")
    
    try:
        if len(request.crops) != len(request.recommendations):
            raise HTTPException(status_code=400, detail="crops and recommendations must have same length")
        
        comparisons = []
        for i in range(len(request.crops)):
            crop = request.crops[i]
            rec = request.recommendations[i]
            
            # Get risk analysis
            loss_prob = rec.get('risk_analysis', {}).get('loss_probability', 50)
            risk_level = rec.get('risk_analysis', {}).get('risk_level', 'Medium')
            
            # Get explanation
            explanation_en = explainability_service.explain_recommendation(
                crop=crop,
                recommendation=rec,
                language='en'
            )
            
            explanation_te = explainability_service.explain_recommendation(
                crop=crop,
                recommendation=rec,
                language='te'
            )
            
            comparisons.append({
                "crop": crop,
                "loss_probability": loss_prob,
                "risk_level": risk_level,
                "suitability_score": rec.get('decision_grade', {}).get('suitability_score', 50),
                "explanation_en": explanation_en,
                "explanation_te": explanation_te
            })
        
        # Sort by suitability (best first)
        comparisons.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Add comparative insights
        if len(comparisons) >= 2:
            best = comparisons[0]
            worst = comparisons[-1]
            
            comparison_text_en = explainability_service.explain_risk_comparison(
                crop_a=best['crop'],
                crop_b=worst['crop'],
                rec_a=request.recommendations[request.crops.index(best['crop'])],
                rec_b=request.recommendations[request.crops.index(worst['crop'])],
                language='en'
            )
            
            comparison_text_te = explainability_service.explain_risk_comparison(
                crop_a=best['crop'],
                crop_b=worst['crop'],
                rec_a=request.recommendations[request.crops.index(best['crop'])],
                rec_b=request.recommendations[request.crops.index(worst['crop'])],
                language='te'
            )
        else:
            comparison_text_en = "Single option provided"
            comparison_text_te = "ఒక ఎంపిక మాత్రమే"
        
        return {
            "success": True,
            "comparisons": comparisons,
            "best_option": comparisons[0] if comparisons else None,
            "riskiest_option": comparisons[-1] if comparisons else None,
            "comparison_summary": {
                "en": comparison_text_en,
                "te": comparison_text_te
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DAILY ADVISORY ENDPOINTS ====================

class AdvisoryRequest(BaseModel):
    lat: float
    lon: float
    crop: str = None
    sowing_date: str = None  # Format: YYYY-MM-DD


@app.post("/daily-advisory")
async def get_daily_advisory(request: AdvisoryRequest):
    """
    Get comprehensive daily farming advisory.
    Combines weather alerts, pest warnings, crop calendar, and recommendations.
    """
    try:
        from datetime import datetime
        
        sowing_date = None
        if request.sowing_date:
            try:
                sowing_date = datetime.strptime(request.sowing_date, "%Y-%m-%d")
            except:
                pass
        
        advisory_service = get_daily_advisory_service()
        advisory = advisory_service.get_daily_advisory(
            request.lat, request.lon, request.crop, sowing_date
        )
        
        return {
            "success": True,
            "advisory": advisory
        }
        
    except Exception as e:
        logger.error(f"Advisory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather-alerts")
async def get_weather_alerts(lat: float, lon: float):
    """
    Get weather alerts for a location.
    """
    try:
        weather = weather_service.get_current_weather(lat, lon)
        forecast = weather_service.get_forecast(lat, lon)
        
        alert_service = get_alert_service()
        alerts = alert_service.generate_alerts(weather, forecast)
        
        return {
            "success": True,
            "weather": weather,
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Weather alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pest-warnings/{crop}")
async def get_pest_warnings(crop: str, temp: float = 30, humidity: float = 60):
    """
    Get pest warnings for a specific crop.
    """
    try:
        season = season_service.get_season()
        pest_service = get_pest_warning_service()
        warnings = pest_service.get_pest_warnings(crop, temp, humidity, season)
        
        return {
            "success": True,
            "crop": crop,
            "season": season,
            "conditions": {"temp": temp, "humidity": humidity},
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Pest warnings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crop-calendar/{crop}")
async def get_crop_calendar(crop: str, season: str = None):
    """
    Get crop calendar with sowing and harvest windows.
    """
    try:
        calendar_service = get_crop_calendar_service()
        
        window = calendar_service.get_optimal_sowing_window(crop, season)
        
        return {
            "success": True,
            "crop": crop,
            "calendar": window
        }
        
    except Exception as e:
        logger.error(f"Crop calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMPREHENSIVE CROP ADVISORY ====================

class CropAdvisoryRequest(BaseModel):
    crop: str
    lat: float
    lon: float
    sowing_date: str = None  # Format: YYYY-MM-DD, defaults to today
    language: str = "both"   # "en", "te", or "both"


@app.post("/crop-advisory")
async def get_crop_advisory(request: CropAdvisoryRequest):
    """
    Get comprehensive crop advisory based on 5-year historical weather patterns.
    
    Returns week-by-week farming guidance from sowing to harvest including:
    - Tasks for each growth stage (Telugu + English)
    - Weather predictions based on NASA POWER 5-year data
    - Irrigation schedules adjusted for expected rainfall
    - Pest and disease alerts
    """
    logger.info(f"Crop advisory request: {request.crop} at ({request.lat}, {request.lon})")
    
    try:
        from datetime import datetime
        from services.crop_advisory_service import get_crop_advisory_service
        
        sowing_date = None
        if request.sowing_date:
            try:
                sowing_date = datetime.strptime(request.sowing_date, "%Y-%m-%d")
            except:
                sowing_date = datetime.now()
        else:
            sowing_date = datetime.now()
        
        advisory_service = get_crop_advisory_service()
        advisory = advisory_service.generate_advisory(
            crop=request.crop,
            lat=request.lat,
            lon=request.lon,
            sowing_date=sowing_date,
            language=request.language
        )
        
        return {
            "success": True,
            "advisory": advisory
        }
        
    except Exception as e:
        logger.error(f"Crop advisory error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CHATBOT ENDPOINT ====================

class ChatRequest(BaseModel):
    message: str
    conversation_history: list = None

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Chat with KisanMitra AI assistant.
    Supports Telugu and English, integrates with all app features.
    """
    from services.chatbot_service import get_chatbot
    
    try:
        chatbot = get_chatbot()
        result = chatbot.generate_response(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        return {
            "success": True,
            "response": result["response"],
            "intent": result.get("intent"),
            "language": result.get("language"),
            "actions": result.get("actions", []),
            "fallback": result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        # Fast fallback
        return {
            "success": True,
            "response": "I'm here to help! Ask me about crops, weather, or market prices. / పంటలు, వాతావరణం, మార్కెట్ ధరల గురించి అడగండి!",
            "intent": "error",
            "language": "en",
            "actions": [],
            "fallback": True
        }


# ============ WHATSAPP WEBHOOK ============

from fastapi import Request, Form
from fastapi.responses import Response

@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    MediaUrl0: str = Form(None),
    Latitude: str = Form(None),
    Longitude: str = Form(None)
):
    """
    Webhook endpoint for Twilio WhatsApp messages.
    Configure this URL in Twilio Console: https://your-domain/whatsapp
    """
    try:
        from services.whatsapp_bot_service import get_whatsapp_bot
        from twilio.twiml.messaging_response import MessagingResponse
        
        bot = get_whatsapp_bot()
        
        # Parse location if provided
        lat = float(Latitude) if Latitude else None
        lon = float(Longitude) if Longitude else None
        
        # Handle the message
        result = bot.handle_incoming_message(
            from_number=From,
            message=Body,
            media_url=MediaUrl0,
            latitude=lat,
            longitude=lon
        )
        
        # Create Twilio response
        resp = MessagingResponse()
        resp.message(result.get("body", ""))
        
        logger.info(f"WhatsApp response to {From}: {result.get('type')}")
        
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        from twilio.twiml.messaging_response import MessagingResponse
        resp = MessagingResponse()
        resp.message("❌ లోపం. మళ్ళీ ప్రయత్నించండి.")
        return Response(content=str(resp), media_type="application/xml")


@app.get("/whatsapp/status")
async def whatsapp_status():
    """Check WhatsApp bot status."""
    try:
        from services.whatsapp_bot_service import get_whatsapp_bot
        bot = get_whatsapp_bot()
        return {
            "success": True,
            "enabled": bot.enabled,
            "whatsapp_number": bot.whatsapp_number if bot.enabled else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== CROP MONITORING ENDPOINTS ====================

class SubscribeCropRequest(BaseModel):
    farmerId: str
    farmerPhone: str
    crop: str
    sowingDate: str  # YYYY-MM-DD
    areaAcres: float = 1.0
    previousCrop: Optional[str] = None
    locationName: str
    lat: float
    lon: float
    district: Optional[str] = None
    soilType: Optional[str] = None
    irrigationType: str = "canal"
    notifyPhone: Optional[str] = None  # Phone for SMS updates
    enableSmsUpdates: bool = True


@app.post("/subscribe-crop")
async def subscribe_to_crop_monitoring(request: SubscribeCropRequest):
    """
    Subscribe to continuous crop monitoring.
    Returns subscription ID and initial monitoring data.
    """
    try:
        # Import database functions
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import create_crop_subscription
        
        # Create subscription
        subscription = create_crop_subscription({
            'farmerId': request.farmerId,
            'farmerPhone': request.farmerPhone,
            'crop': request.crop,
            'sowingDate': request.sowingDate,
            'areaAcres': request.areaAcres,
            'previousCrop': request.previousCrop,
            'locationName': request.locationName,
            'lat': request.lat,
            'lon': request.lon,
            'district': request.district,
            'soilType': request.soilType,
            'irrigationType': request.irrigationType
        })
        
        # Generate initial action plan
        monitoring_service = get_crop_monitoring_service()
        action_plan = monitoring_service.generate_daily_action_plan(subscription)
        
        # Send welcome SMS if phone provided
        welcome_sms_sent = False
        if request.notifyPhone and request.enableSmsUpdates:
            try:
                from services.sms_bot_service import get_sms_bot
                sms_bot = get_sms_bot()
                welcome_messages = sms_bot.format_welcome_sms(subscription)
                logger.info(f"Welcome SMS prepared for {request.notifyPhone}: {len(welcome_messages)} parts")
                # Store phone in subscription for future updates
                subscription['notifyPhone'] = request.notifyPhone
                welcome_sms_sent = True
            except Exception as sms_error:
                logger.error(f"Welcome SMS error: {sms_error}")
        
        logger.info(f"Created subscription {subscription['subscriptionId']} for {request.crop}")
        
        return {
            "success": True,
            "subscription": subscription,
            "initial_plan": action_plan,
            "welcome_sms_sent": welcome_sms_sent
        }
        
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/my-crops/{farmer_id}")
async def get_my_crops(farmer_id: str):
    """
    Get all subscribed crops for a farmer with current status.
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import get_farmer_subscriptions
        
        subscriptions = get_farmer_subscriptions(farmer_id)
        
        # Enrich with current status
        monitoring_service = get_crop_monitoring_service()
        enriched = []
        
        for sub in subscriptions:
            try:
                from datetime import datetime
                sowing_date = datetime.strptime(sub.get('sowingDate', '2025-01-01'), '%Y-%m-%d')
                stage_info = monitoring_service.calculate_crop_stage(sowing_date, sub.get('crop'))
                
                # Get quick alerts
                alerts = monitoring_service.generate_weather_alerts(
                    sub.get('location', {}).get('lat', 17.385),
                    sub.get('location', {}).get('lon', 78.487),
                    sub.get('crop'),
                    stage_info.get('current_stage')
                )
                
                enriched.append({
                    **sub,
                    'stage_info': stage_info,
                    'alert_count': len([a for a in alerts if a['severity'] == 'high']),
                    'has_urgent_alerts': any(a['severity'] == 'high' for a in alerts)
                })
            except Exception as e:
                logger.warning(f"Error enriching subscription: {e}")
                enriched.append(sub)
        
        return {
            "success": True,
            "farmer_id": farmer_id,
            "subscriptions": enriched,
            "count": len(enriched)
        }
        
    except Exception as e:
        logger.error(f"Get my crops error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/subscription/{subscription_id}")
async def delete_crop_subscription(subscription_id: str):
    """
    Delete a crop subscription.
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import delete_subscription, get_subscription_by_id
        
        # Verify subscription exists
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Delete it
        success = delete_subscription(subscription_id)
        
        if success:
            logger.info(f"Deleted subscription {subscription_id}")
            return {"success": True, "message": "Subscription deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crop-monitoring/{subscription_id}")
async def get_crop_monitoring_data(subscription_id: str):
    """
    Get full monitoring data for a subscription.
    Includes today's plan, alerts, forecast, and relevant FAQs.
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import get_subscription_by_id
        
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Generate full action plan
        monitoring_service = get_crop_monitoring_service()
        action_plan = monitoring_service.generate_daily_action_plan(subscription)
        
        # Get ALL FAQs for this crop (not filtered by stage)
        faq_service = get_crop_faq_service()
        crop = subscription.get('crop')
        crop_faqs = faq_service.faq_data.get('crops', {}).get(crop, {}).get('faqs', [])
        
        return {
            "success": True,
            "subscription": subscription,
            "action_plan": action_plan,
            "relevant_faqs": crop_faqs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Monitoring data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/daily-plan/{subscription_id}")
async def get_daily_action_plan(subscription_id: str):
    """Get today's action plan only (lightweight endpoint)."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import get_subscription_by_id
        
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        monitoring_service = get_crop_monitoring_service()
        action_plan = monitoring_service.generate_daily_action_plan(subscription)
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "plan": action_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weekly-plan/{subscription_id}")
async def get_weekly_action_plan(subscription_id: str):
    """
    Get comprehensive 7-day farmer action plan.
    Includes day-by-day tasks, weather forecasts, irrigation schedule,
    fertilizer reminders, pest alerts, and farmer-friendly advice.
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import get_subscription_by_id
        
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        monitoring_service = get_crop_monitoring_service()
        weekly_plan = monitoring_service.generate_weekly_plan(subscription)
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "weekly_plan": weekly_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weekly plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather-alerts-crop/{subscription_id}")
async def get_weather_alerts_for_crop(subscription_id: str):
    """Get current weather alerts for a subscribed crop."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import get_subscription_by_id
        
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        monitoring_service = get_crop_monitoring_service()
        from datetime import datetime
        sowing_date = datetime.strptime(subscription.get('sowingDate', '2025-01-01'), '%Y-%m-%d')
        stage_info = monitoring_service.calculate_crop_stage(sowing_date, subscription.get('crop'))
        
        alerts = monitoring_service.generate_weather_alerts(
            subscription.get('location', {}).get('lat', 17.385),
            subscription.get('location', {}).get('lon', 78.487),
            subscription.get('crop'),
            stage_info.get('current_stage')
        )
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "crop": subscription.get('crop'),
            "stage": stage_info.get('stage_name'),
            "alerts": alerts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weather alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crop-faqs/{crop}")
async def get_crop_faqs(crop: str, category: str = None, stage: str = None, limit: int = 20):
    """Get FAQs for a specific crop."""
    try:
        faq_service = get_crop_faq_service()
        
        if category:
            faqs = faq_service.get_faqs_by_category(crop, category)
        elif stage:
            faqs = faq_service.get_faqs_by_stage(crop, stage)
        else:
            # Get all FAQs for crop
            faqs = faq_service.search_faqs("", crop=crop, limit=limit)
        
        return {
            "success": True,
            "crop": crop,
            "category": category,
            "stage": stage,
            "faqs": faqs[:limit],
            "total": len(faqs)
        }
        
    except Exception as e:
        logger.error(f"Crop FAQs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search-faqs")
async def search_faqs(query: str, crop: str = None, category: str = None, limit: int = 10):
    """Search FAQs by symptom or question."""
    try:
        faq_service = get_crop_faq_service()
        results = faq_service.search_faqs(query, crop=crop, category=category, limit=limit)
        
        return {
            "success": True,
            "query": query,
            "crop": crop,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"FAQ search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/faq-categories")
async def get_faq_categories():
    """Get all FAQ categories with counts."""
    try:
        faq_service = get_crop_faq_service()
        categories = faq_service.get_all_categories()
        crops = faq_service.get_crop_list()
        
        return {
            "success": True,
            "categories": categories,
            "crops": crops
        }
        
    except Exception as e:
        logger.error(f"FAQ categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-subscription/{subscription_id}")
async def update_subscription(subscription_id: str, status: str = None, alerts_enabled: bool = None):
    """Update subscription status or settings."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from database import update_subscription_status, get_subscription_by_id
        
        additional_data = {}
        if alerts_enabled is not None:
            additional_data['alerts_enabled'] = alerts_enabled
        
        if status:
            success = update_subscription_status(subscription_id, status, additional_data)
        elif additional_data:
            success = update_subscription_status(subscription_id, None, additional_data)
        else:
            raise HTTPException(status_code=400, detail="No update parameters provided")
        
        if success:
            updated = get_subscription_by_id(subscription_id)
            return {"success": True, "subscription": updated}
        else:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
