"""
Crop Monitoring Service
Provides intelligent daily action plans based on real-time weather monitoring
and crop growth stage analysis.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

# Load data files
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
RULES_PATH = os.path.join(DATA_DIR, 'daily_action_rules.json')
PROFILES_PATH = os.path.join(DATA_DIR, 'crop_profiles.json')
STAGES_PATH = os.path.join(DATA_DIR, 'crop_stages.json')  # Use comprehensive stages
WEATHER_IMPACTS_PATH = os.path.join(DATA_DIR, 'weather_crop_impacts.json')  # Weather scenarios
PEST_DISEASE_PATH = os.path.join(DATA_DIR, 'pest_disease_db.json')  # Pest & disease database
FAQS_PATH = os.path.join(DATA_DIR, 'crop_faqs_complete.json')  # Comprehensive FAQs

# OpenWeather API
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'dd587855fbdac207034b854ea3e03c00')


class CropMonitoringService:
    """
    Intelligent crop monitoring service that provides:
    - Real-time weather alerts with actionable recommendations
    - Daily action plans based on crop stage
    - 5-day forecast with day-by-day actions
    - Dynamic adjustment based on weather patterns
    """
    
    def __init__(self):
        self.rules = self._load_json(RULES_PATH)
        self.profiles = self._load_json(PROFILES_PATH)
        self.stages = self._load_json(STAGES_PATH)
        self.weather_impacts = self._load_json(WEATHER_IMPACTS_PATH)
        self.pest_disease_db = self._load_json(PEST_DISEASE_PATH)
        self.faqs = self._load_json(FAQS_PATH)
        self._weather_cache = {}
        self._cache_timeout = 10800  # 3 hours
        logger.info("CropMonitoringService initialized with comprehensive data")
    
    def _load_json(self, path: str) -> Dict:
        """Load JSON data file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}
    
    def _get_weather_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch current weather and 5-day forecast from OpenWeather API
        Implements caching to reduce API calls
        """
        cache_key = f"{lat:.2f}_{lon:.2f}"
        now = datetime.now()
        
        # Check cache
        if cache_key in self._weather_cache:
            cached = self._weather_cache[cache_key]
            if (now - cached['timestamp']).seconds < self._cache_timeout:
                return cached['data']
        
        try:
            # Current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            current_res = requests.get(current_url, timeout=10)
            current_data = current_res.json()
            
            # 5-day forecast (3-hour intervals)
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            forecast_res = requests.get(forecast_url, timeout=10)
            forecast_data = forecast_res.json()
            
            # Process forecast into daily summaries
            daily_forecast = self._process_forecast(forecast_data)
            
            weather = {
                'current': {
                    'temp': current_data.get('main', {}).get('temp', 25),
                    'temp_min': current_data.get('main', {}).get('temp_min', 20),
                    'temp_max': current_data.get('main', {}).get('temp_max', 30),
                    'humidity': current_data.get('main', {}).get('humidity', 60),
                    'wind_speed': current_data.get('wind', {}).get('speed', 5) * 3.6,  # Convert m/s to km/h
                    'description': current_data.get('weather', [{}])[0].get('description', 'clear'),
                    'icon': current_data.get('weather', [{}])[0].get('icon', '01d'),
                    'rainfall_1h': current_data.get('rain', {}).get('1h', 0),
                    'rainfall_3h': current_data.get('rain', {}).get('3h', 0),
                    'visibility': current_data.get('visibility', 10000)
                },
                'forecast': daily_forecast,
                'next_6h_rain': self._calculate_next_hours_rain(forecast_data, 6),
                'next_24h_rain': self._calculate_next_hours_rain(forecast_data, 24)
            }
            
            # Cache the result
            self._weather_cache[cache_key] = {
                'timestamp': now,
                'data': weather
            }
            
            return weather
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._get_default_weather()
    
    def _process_forecast(self, forecast_data: Dict) -> List[Dict]:
        """Process 3-hourly forecast into daily summaries"""
        daily = {}
        
        for item in forecast_data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.strftime('%Y-%m-%d')
            
            if date_key not in daily:
                daily[date_key] = {
                    'date': date_key,
                    'day_name': dt.strftime('%A'),
                    'temps': [],
                    'humidity': [],
                    'rainfall': 0,
                    'wind_speeds': [],
                    'descriptions': []
                }
            
            daily[date_key]['temps'].append(item['main']['temp'])
            daily[date_key]['humidity'].append(item['main']['humidity'])
            daily[date_key]['rainfall'] += item.get('rain', {}).get('3h', 0)
            daily[date_key]['wind_speeds'].append(item['wind']['speed'] * 3.6)
            daily[date_key]['descriptions'].append(item['weather'][0]['main'])
        
        # Convert to final format
        result = []
        for date_key in sorted(daily.keys())[:5]:
            d = daily[date_key]
            result.append({
                'date': d['date'],
                'day_name': d['day_name'],
                'temp_min': min(d['temps']),
                'temp_max': max(d['temps']),
                'temp_avg': sum(d['temps']) / len(d['temps']),
                'humidity_avg': sum(d['humidity']) / len(d['humidity']),
                'rainfall_mm': round(d['rainfall'], 1),
                'wind_speed_max': max(d['wind_speeds']),
                'condition': max(set(d['descriptions']), key=d['descriptions'].count)
            })
        
        return result
    
    def _calculate_next_hours_rain(self, forecast_data: Dict, hours: int) -> float:
        """Calculate expected rainfall in next N hours"""
        total_rain = 0
        target_time = datetime.now() + timedelta(hours=hours)
        
        for item in forecast_data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            if dt <= target_time:
                total_rain += item.get('rain', {}).get('3h', 0)
        
        return round(total_rain, 1)
    
    def _get_default_weather(self) -> Dict:
        """Default weather when API fails"""
        return {
            'current': {'temp': 28, 'humidity': 65, 'wind_speed': 10, 'rainfall_1h': 0},
            'forecast': [],
            'next_6h_rain': 0,
            'next_24h_rain': 0
        }
    
    def calculate_crop_stage(self, sowing_date: datetime, crop: str) -> Dict:
        """
        Calculate current crop growth stage based on sowing date
        Uses comprehensive stages data with detailed activities
        """
        days_after_sowing = (datetime.now() - sowing_date).days
        
        # Get crop stages from comprehensive data
        crop_data = self.stages.get('crops', {}).get(crop, {})
        stages_list = crop_data.get('stages', [])
        total_duration = crop_data.get('duration_days', crop_data.get('total_duration_days', 120))
        
        current_stage = None
        stage_name = "Unknown"
        stage_name_te = "తెలియదు"
        stage_day_start = 0
        stage_day_end = 0
        current_activities = []
        pest_focus = []
        disease_focus = []
        
        # Handle pre-sowing (future sowing date)
        if days_after_sowing < 0:
            days_until_sowing = abs(days_after_sowing)
            current_stage = "pre_sowing"
            stage_name = "Pre-Sowing"
            stage_name_te = "విత్తనానికి ముందు"
            stage_day_start = days_after_sowing
            stage_day_end = 0
            # Get first stage activities as preparation
            first_stage = stages_list[0] if stages_list else {}
            current_activities = [
                {'task': f'Prepare field - {days_until_sowing} days to sowing', 'priority': 'high', 'day': 0},
                {'task': 'Arrange quality seeds', 'priority': 'high', 'day': 0},
                {'task': 'Soil testing and land preparation', 'priority': 'medium', 'day': 0}
            ]
            pest_focus = []
            disease_focus = []
        else:
            for stage in stages_list:
                # Convert weeks to days (our data uses week_start/week_end)
                week_start = stage.get('week_start', 1)
                week_end = stage.get('week_end', 1)
                start_day = (week_start - 1) * 7  # Week 1 = Day 0-6
                end_day = week_end * 7 - 1  # Week 2 = Day 7-13
                
                # Also support start_day/end_day if present (backwards compat)
                start_day = stage.get('start_day', start_day)
                end_day = stage.get('end_day', end_day)
                
                if start_day <= days_after_sowing <= end_day:
                    current_stage = stage.get('name', stage.get('name_en', '')).lower().replace(' ', '_')
                    stage_name = stage.get('name', stage.get('name_en', 'Unknown'))
                    stage_name_te = stage.get('name_te', stage_name)
                    stage_day_start = start_day
                    stage_day_end = end_day
                    
                    # Get activities - support multiple field names
                    tasks_en = stage.get('tasks_en', [])
                    activities = stage.get('critical_activities', [])
                    if tasks_en and not activities:
                        # Convert tasks_en to activities format
                        current_activities = [{'task': t, 'priority': 'normal'} for t in tasks_en]
                    else:
                        current_activities = activities
                    
                    pest_focus = stage.get('pest_focus', [])
                    disease_focus = stage.get('disease_focus', [])
                    break
            
            # If no stage matched, use the closest or last stage
            if not current_stage and stages_list:
                # Find closest stage
                for stage in stages_list:
                    week_start = stage.get('week_start', 1)
                    week_end = stage.get('week_end', 1)
                    start_day = stage.get('start_day', (week_start - 1) * 7)
                    end_day = stage.get('end_day', week_end * 7 - 1)
                    
                    if days_after_sowing < start_day:
                        # Use this stage as current (closest upcoming)
                        current_stage = stage.get('name', stage.get('name_en', '')).lower().replace(' ', '_')
                        stage_name = stage.get('name', stage.get('name_en', 'Unknown'))
                        stage_name_te = stage.get('name_te', stage_name)
                        stage_day_start = start_day
                        stage_day_end = end_day
                        tasks_en = stage.get('tasks_en', [])
                        activities = stage.get('critical_activities', [])
                        if tasks_en and not activities:
                            current_activities = [{'task': t, 'priority': 'normal'} for t in tasks_en]
                        else:
                            current_activities = activities
                        pest_focus = stage.get('pest_focus', [])
                        disease_focus = stage.get('disease_focus', [])
                        break
                
                # If still not found, use last stage (post-harvest)
                if not current_stage:
                    last_stage = stages_list[-1]
                    current_stage = "post_harvest"
                    stage_name = "Harvest Complete"
                    stage_name_te = "కోత పూర్తి"
                    stage_day_start = days_after_sowing
                    stage_day_end = days_after_sowing + 7
                    current_activities = [{'task': 'Post-harvest activities and storage', 'priority': 'normal'}]
                    pest_focus = []
                    disease_focus = []
        
        # Calculate progress
        progress_percent = min(100, round((days_after_sowing / total_duration) * 100))
        
        return {
            'crop': crop,
            'crop_name_te': crop_data.get('name_te', crop),
            'sowing_date': sowing_date.strftime('%Y-%m-%d'),
            'days_after_sowing': days_after_sowing,
            'current_stage': current_stage,
            'stage_name': stage_name,
            'stage_name_te': stage_name_te,
            'stage_day_range': [stage_day_start, stage_day_end],
            'days_in_stage': days_after_sowing - stage_day_start,
            'total_duration_days': total_duration,
            'progress_percent': progress_percent,
            'harvest_expected': (sowing_date + timedelta(days=total_duration)).strftime('%Y-%m-%d'),
            'current_activities': current_activities[:5],  # Top 5 activities for today
            'pest_focus': pest_focus,
            'disease_focus': disease_focus
        }
    
    def generate_weather_alerts(self, lat: float, lon: float, crop: str, stage: str = None) -> List[Dict]:
        """
        Generate real-time weather alerts based on current conditions and forecast
        Returns prioritized list of actionable alerts
        """
        weather = self._get_weather_data(lat, lon)
        alerts = []
        
        current = weather.get('current', {})
        forecast = weather.get('forecast', [])
        
        # Check each alert rule
        for rule in self.rules.get('weather_alert_rules', []):
            triggered = False
            condition = rule.get('condition', {})
            
            # Check current conditions
            if 'rainfall_mm' in condition:
                rain_check = weather.get('next_6h_rain', 0)
                op = condition['rainfall_mm'].get('operator', '>=')
                val = condition['rainfall_mm'].get('value', 0)
                if op == '>=' and rain_check >= val:
                    triggered = True
                elif op == '>' and rain_check > val:
                    triggered = True
            
            if 'temp_max' in condition:
                op = condition['temp_max'].get('operator', '>=')
                val = condition['temp_max'].get('value', 40)
                temp_check = current.get('temp_max') or current.get('temp', 25)
                # Also check forecast
                for fc in forecast[:2]:
                    if fc.get('temp_max', 0) >= val:
                        triggered = True
                        break
                if op == '>=' and temp_check >= val:
                    triggered = True
            
            if 'temp_min' in condition:
                op = condition['temp_min'].get('operator', '<=')
                val = condition['temp_min'].get('value', 10)
                temp_check = current.get('temp_min') or current.get('temp', 25)
                if op == '<=' and temp_check <= val:
                    triggered = True
            
            if 'humidity' in condition:
                op = condition['humidity'].get('operator', '>=')
                val = condition['humidity'].get('value', 85)
                if op == '>=' and current.get('humidity', 60) >= val:
                    triggered = True
            
            if 'wind_speed' in condition:
                op = condition['wind_speed'].get('operator', '>=')
                val = condition['wind_speed'].get('value', 40)
                if op == '>=' and current.get('wind_speed', 0) >= val:
                    triggered = True
            
            # If triggered and crop is affected
            if triggered:
                crops_at_risk = rule.get('crops_affected', [])
                if not crops_at_risk or crop in crops_at_risk:
                    alerts.append({
                        'id': rule.get('id'),
                        'severity': rule.get('severity', 'medium'),
                        'icon': rule.get('icon', '⚠️'),
                        'title_en': rule.get('title_en'),
                        'title_te': rule.get('title_te'),
                        'risks_en': rule.get('risks_en', []),
                        'risks_te': rule.get('risks_te', []),
                        'actions_en': rule.get('actions_en', []),
                        'actions_te': rule.get('actions_te', []),
                        'forecast_hours': rule.get('forecast_hours', 24),
                        'weather_data': {
                            'temp': current.get('temp'),
                            'humidity': current.get('humidity'),
                            'rainfall_expected': weather.get('next_6h_rain', 0),
                            'wind_speed': current.get('wind_speed')
                        }
                    })
        
        # Add intelligent weather impact alerts using comprehensive data
        alerts.extend(self._generate_weather_impact_alerts(weather, crop, stage))
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 2))
        
        return alerts
    
    def _generate_weather_impact_alerts(self, weather: Dict, crop: str, stage: str) -> List[Dict]:
        """Generate alerts based on weather_crop_impacts.json data"""
        alerts = []
        current = weather.get('current', {})
        forecast = weather.get('forecast', [])
        
        scenarios = self.weather_impacts.get('weather_scenarios', {})
        
        # Check heat wave
        if current.get('temp', 25) >= 38 or any(f.get('temp_max', 30) >= 40 for f in forecast[:3]):
            heat_wave = scenarios.get('heat_wave', {}).get('crop_impacts', {}).get(crop, {})
            if stage and stage in heat_wave:
                impact = heat_wave[stage]
                alerts.append({
                    'id': 'heat_wave_impact',
                    'severity': impact.get('risk', 'high'),
                    'icon': '🔥',
                    'title_en': f"Heat Wave Warning - {impact.get('effect', 'High temperature stress')}",
                    'title_te': f"వేడి గాలి హెచ్చరిక - {impact.get('effect', '')}",
                    'risks_en': [f"Potential yield loss: {impact.get('yield_loss_percent', 'Unknown')}%"],
                    'risks_te': [f"దిగుబడి నష్టం: {impact.get('yield_loss_percent', 'Unknown')}%"],
                    'actions_en': impact.get('actions_en', ['Irrigate in evening']),
                    'actions_te': impact.get('actions_te', ['సాయంత్రం నీరు'])
                })
        
        # Check high humidity (pest/disease risk)
        if current.get('humidity', 60) >= 85:
            humidity_scenario = scenarios.get('high_humidity', {}).get('crop_impacts', {}).get(crop, {})
            if stage and stage in humidity_scenario:
                impact = humidity_scenario[stage]
                alerts.append({
                    'id': 'humidity_impact',
                    'severity': impact.get('risk', 'medium'),
                    'icon': '💧',
                    'title_en': f"High Humidity Alert - {impact.get('effect', 'Disease risk')}",
                    'title_te': f"అధిక తేమ హెచ్చరిక",
                    'risks_en': [impact.get('effect', 'Increased pest/disease pressure')],
                    'risks_te': [impact.get('effect', '')],
                    'actions_en': impact.get('actions_en', ['Monitor for pests']),
                    'actions_te': impact.get('actions_te', ['పురుగుల కోసం చూడండి'])
                })
        
        # Check heavy rain expected
        rain_24h = weather.get('next_24h_rain', 0)
        if rain_24h >= 50:
            rain_scenario = scenarios.get('continuous_rain', {}).get('crop_impacts', {}).get(crop, {})
            if rain_scenario:
                # Check any stage impact
                for s, impact in rain_scenario.items():
                    if stage and s in stage or s == 'all':
                        alerts.append({
                            'id': 'rain_impact',
                            'severity': impact.get('risk', 'medium'),
                            'icon': '🌧️',
                            'title_en': f"Heavy Rain Alert ({rain_24h}mm expected)",
                            'title_te': f"భారీ వర్షం హెచ్చరిక ({rain_24h}mm)",
                            'risks_en': [impact.get('effect', 'Water logging risk')],
                            'risks_te': [impact.get('effect', '')],
                            'actions_en': impact.get('actions_en', ['Ensure drainage']),
                            'actions_te': impact.get('actions_te', ['డ్రైనేజ్ నిర్ధారించండి'])
                        })
                        break
        
        # Check strong wind
        if current.get('wind_speed', 10) >= 35:
            wind_scenario = scenarios.get('strong_wind', {}).get('crop_impacts', {}).get(crop, {})
            if stage and stage in wind_scenario:
                impact = wind_scenario[stage]
                alerts.append({
                    'id': 'wind_impact',
                    'severity': impact.get('risk', 'medium'),
                    'icon': '💨',
                    'title_en': f"Strong Wind Alert - {impact.get('effect', 'Lodging risk')}",
                    'title_te': f"గాలి హెచ్చరిక",
                    'actions_en': impact.get('actions_en', ['Take protective measures']),
                    'actions_te': impact.get('actions_te', ['రక్షణ చర్యలు తీసుకోండి'])
                })
        
        return alerts
    
    def get_today_tasks(self, crop: str, stage: str, weather: Dict = None, stage_info: Dict = None) -> List[Dict]:
        """
        Get today's actionable tasks based on crop stage and weather
        Uses comprehensive stages data with detailed activities
        """
        tasks = []
        
        # Get activities from stage_info (from comprehensive stages)
        activities = stage_info.get('current_activities', []) if stage_info else []
        pest_focus = stage_info.get('pest_focus', []) if stage_info else []
        disease_focus = stage_info.get('disease_focus', []) if stage_info else []
        
        # Add critical activities
        for i, activity in enumerate(activities[:5]):  # Top 5 activities
            task_text = activity.get('task', activity) if isinstance(activity, dict) else str(activity)
            priority_level = activity.get('priority', 'normal') if isinstance(activity, dict) else 'normal'
            
            tasks.append({
                'id': f"task_{i+1}",
                'type': 'activity',
                'task_en': task_text,
                'task_te': task_text,  # Could add Telugu translations
                'completed': False,
                'priority': priority_level
            })
        
        # Add pest scouting task if pest focus exists
        if pest_focus:
            tasks.append({
                'id': 'pest_task',
                'type': 'pest_scouting',
                'task_en': f"🔍 Scout for: {', '.join(pest_focus)}",
                'task_te': f"🔍 పురుగుల కోసం చూడండి: {', '.join(pest_focus)}",
                'completed': False,
                'priority': 'high'
            })
        
        # Add disease monitoring if disease focus exists
        if disease_focus:
            tasks.append({
                'id': 'disease_task',
                'type': 'disease_monitoring',
                'task_en': f"🦠 Watch for: {', '.join(disease_focus)}",
                'task_te': f"🦠 వ్యాధుల కోసం చూడండి: {', '.join(disease_focus)}",
                'completed': False,
                'priority': 'high'
            })
        
        # Weather-based adjustments
        if weather:
            current = weather.get('current', {})
            rain_expected = weather.get('next_6h_rain', 0)
            
            if rain_expected > 20:
                tasks.insert(0, {
                    'id': 'weather_rain',
                    'type': 'weather_adjustment',
                    'task_en': f"⚠️ Rain Alert: {rain_expected}mm expected in 6 hours. Avoid spraying/fertilizer.",
                    'task_te': f"⚠️ వర్షం హెచ్చరిక: 6 గంటలలో {rain_expected}mm. పిచికారీ/ఎరువులు వేయకండి.",
                    'completed': False,
                    'priority': 'urgent'
                })
            
            if current.get('temp', 25) > 38:
                tasks.insert(0, {
                    'id': 'weather_heat',
                    'type': 'weather_adjustment',
                    'task_en': f"🔥 Heat Alert: {current.get('temp')}°C. Irrigate in evening only.",
                    'task_te': f"🔥 వేడి హెచ్చరిక: {current.get('temp')}°C. సాయంత్రం మాత్రమే నీరు పెట్టండి.",
                    'completed': False,
                    'priority': 'urgent'
                })
        
        return tasks
    
    def generate_daily_action_plan(self, subscription: Dict) -> Dict:
        """
        Generate comprehensive daily action plan for a subscribed crop
        
        Args:
            subscription: Dict containing crop details, location, sowing date
        
        Returns:
            Complete daily action plan with alerts, tasks, and forecast actions
        """
        crop = subscription.get('crop')
        lat = subscription.get('location', {}).get('lat', 17.385)
        lon = subscription.get('location', {}).get('lon', 78.487)
        sowing_date = datetime.strptime(subscription.get('sowingDate', '2025-01-01'), '%Y-%m-%d')
        area_acres = subscription.get('areaAcres', 1)
        
        # Calculate crop stage
        stage_info = self.calculate_crop_stage(sowing_date, crop)
        current_stage = stage_info.get('current_stage')
        
        # Get weather data
        weather = self._get_weather_data(lat, lon)
        
        # Generate weather alerts
        alerts = self.generate_weather_alerts(lat, lon, crop, current_stage)
        
        # Get today's tasks (with comprehensive stage activities)
        today_tasks = self.get_today_tasks(crop, current_stage, weather, stage_info)
        
        # Generate 5-day forecast with actions
        forecast_actions = []
        for day in weather.get('forecast', []):
            day_actions = []
            
            # Rain day actions
            if day.get('rainfall_mm', 0) > 20:
                day_actions.append({
                    'action_en': "Skip irrigation - rain expected",
                    'action_te': "నీరు వేయకండి - వర్షం వస్తుంది",
                    'icon': '🌧️'
                })
                day_actions.append({
                    'action_en': "Avoid fertilizer application",
                    'action_te': "ఎరువులు వేయకండి",
                    'icon': '⚠️'
                })
            
            # Hot day actions
            if day.get('temp_max', 30) > 38:
                day_actions.append({
                    'action_en': "Irrigate in evening only",
                    'action_te': "సాయంత్రం మాత్రమే నీరు వేయండి",
                    'icon': '🔥'
                })
            
            # Good weather actions
            if day.get('rainfall_mm', 0) == 0 and 25 <= day.get('temp_max', 30) <= 35:
                day_actions.append({
                    'action_en': "Good day for spraying/fertilizer",
                    'action_te': "పిచికారి/ఎరువులకు మంచి రోజు",
                    'icon': '✅'
                })
            
            forecast_actions.append({
                'date': day.get('date'),
                'day_name': day.get('day_name'),
                'weather': {
                    'temp_min': day.get('temp_min'),
                    'temp_max': day.get('temp_max'),
                    'rainfall_mm': day.get('rainfall_mm'),
                    'condition': day.get('condition')
                },
                'actions': day_actions if day_actions else [{
                    'action_en': "Normal operations",
                    'action_te': "సాధారణ పనులు",
                    'icon': '📋'
                }]
            })
        
        # Calculate irrigation advice
        irrigation_advice = self._get_irrigation_advice(crop, current_stage, weather)
        
        return {
            'subscription_id': subscription.get('subscriptionId'),
            'generated_at': datetime.now().isoformat(),
            'crop': crop,
            'area_acres': area_acres,
            'stage_info': stage_info,
            'current_weather': weather.get('current', {}),
            'alerts': alerts,
            'today_tasks': today_tasks,
            'forecast_actions': forecast_actions,
            'irrigation_advice': irrigation_advice,
            'summary_en': self._generate_summary_en(stage_info, alerts, weather),
            'summary_te': self._generate_summary_te(stage_info, alerts, weather)
        }
    
    def _get_irrigation_advice(self, crop: str, stage: str, weather: Dict) -> Dict:
        """Get irrigation recommendation based on crop, stage, and weather"""
        base_frequency = self.rules.get('irrigation_rules', {}).get('default_frequency_days', 7)
        adjustments = self.rules.get('irrigation_rules', {}).get('adjustments', {})
        
        frequency = base_frequency
        skip_days = 0
        reason = ""
        
        # Check recent/expected rainfall
        rain_expected = weather.get('next_24h_rain', 0)
        if rain_expected >= 50:
            skip_days = adjustments.get('after_rain_50mm', {}).get('skip_days', 4)
            reason = "Heavy rain expected, skip irrigation"
        elif rain_expected >= 25:
            skip_days = adjustments.get('after_rain_25mm', {}).get('skip_days', 2)
            reason = "Rain expected, reduce irrigation"
        
        # Temperature adjustment
        current_temp = weather.get('current', {}).get('temp', 28)
        if current_temp >= 38:
            frequency -= adjustments.get('temp_above_38', {}).get('reduce_frequency_by', 2)
            reason = "High temperature, increase irrigation frequency"
        
        return {
            'recommended_frequency_days': max(2, frequency),
            'skip_days': skip_days,
            'reason_en': reason or "Normal irrigation schedule",
            'reason_te': reason or "సాధారణ నీటిపారుదల షెడ్యూల్",
            'next_irrigation': (datetime.now() + timedelta(days=skip_days if skip_days else frequency)).strftime('%Y-%m-%d')
        }
    
    def _generate_summary_en(self, stage_info: Dict, alerts: List, weather: Dict) -> str:
        """Generate English summary of today's plan"""
        crop = stage_info.get('crop')
        stage = stage_info.get('stage_name')
        days = stage_info.get('days_after_sowing')
        temp = weather.get('current', {}).get('temp', 28)
        
        alert_count = len([a for a in alerts if a['severity'] == 'high'])
        
        if alert_count > 0:
            return f"⚠️ {crop} at {stage} stage (Day {days}). {alert_count} weather alert(s) require attention. Current temp: {temp}°C"
        else:
            return f"✅ {crop} at {stage} stage (Day {days}). No critical alerts. Current temp: {temp}°C. Check today's tasks below."
    
    def _generate_summary_te(self, stage_info: Dict, alerts: List, weather: Dict) -> str:
        """Generate Telugu summary of today's plan"""
        crop = stage_info.get('crop')
        stage = stage_info.get('stage_name')
        days = stage_info.get('days_after_sowing')
        temp = weather.get('current', {}).get('temp', 28)
        
        alert_count = len([a for a in alerts if a['severity'] == 'high'])
        
        if alert_count > 0:
            return f"⚠️ {crop} {stage} దశలో (రోజు {days}). {alert_count} వాతావరణ హెచ్చరిక(లు). ప్రస్తుత ఉష్ణోగ్రత: {temp}°C"
        else:
            return f"✅ {crop} {stage} దశలో (రోజు {days}). తీవ్ర హెచ్చరికలు లేవు. ప్రస్తుత ఉష్ణోగ్రత: {temp}°C"
    
    def generate_weekly_plan(self, subscription: Dict) -> Dict:
        """
        Generate comprehensive 7-day farmer action plan
        Acts as a 'farmer friend' with day-by-day guidance
        """
        crop = subscription.get('crop')
        lat = subscription.get('location', {}).get('lat', 17.385)
        lon = subscription.get('location', {}).get('lon', 78.487)
        sowing_date = datetime.strptime(subscription.get('sowingDate', '2025-01-01'), '%Y-%m-%d')
        area_acres = subscription.get('areaAcres', 1)
        
        # Get weather data (includes 5-day forecast)
        weather = self._get_weather_data(lat, lon)
        forecast_days = weather.get('forecast', [])
        
        # Calculate current crop stage
        stage_info = self.calculate_crop_stage(sowing_date, crop)
        current_stage = stage_info.get('current_stage')
        days_after_sowing = stage_info.get('days_after_sowing', 0)
        
        # Get crop stage data
        crop_data = self.stages.get('crops', {}).get(crop, {})
        stages_list = crop_data.get('stages', [])
        
        # Find current and upcoming stages
        current_stage_data = None
        next_stage_data = None
        for i, stage in enumerate(stages_list):
            if stage.get('start_day', 0) <= days_after_sowing <= stage.get('end_day', 0):
                current_stage_data = stage
                if i + 1 < len(stages_list):
                    next_stage_data = stages_list[i + 1]
                break
        
        # Generate 7-day plan
        days_plan = []
        today = datetime.now()
        
        DAY_LABELS = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        DAY_LABELS_TE = ["ఈ రోజు", "రేపు", "3వ రోజు", "4వ రోజు", "5వ రోజు", "6వ రోజు", "7వ రోజు"]
        
        for day_offset in range(7):
            target_date = today + timedelta(days=day_offset)
            das_on_day = days_after_sowing + day_offset  # Days After Sowing on that day
            
            # Get weather for this day (if available)
            day_weather = {}
            if day_offset < len(forecast_days):
                day_weather = forecast_days[day_offset]
            else:
                # Estimate based on current
                day_weather = {
                    'temp_max': weather.get('current', {}).get('temp', 28) + 2,
                    'temp_min': weather.get('current', {}).get('temp', 28) - 5,
                    'humidity_avg': weather.get('current', {}).get('humidity', 60),
                    'rainfall_mm': 0,
                    'condition': 'Clear'
                }
            
            # Determine priority level for the day
            priority = self._calculate_day_priority(day_weather, current_stage_data, das_on_day, crop)
            
            # Get tasks for this day
            tasks = self._get_tasks_for_day(
                crop, current_stage_data, das_on_day, day_offset, 
                day_weather, stage_info, area_acres
            )
            
            # Get irrigation advice for this day
            irrigation = self._get_irrigation_for_day(crop, current_stage, day_weather, day_offset, das_on_day)
            
            # Get fertilizer schedule
            fertilizer = self._get_fertilizer_for_day(crop, current_stage_data, das_on_day, area_acres)
            
            # Get pest/disease alert for this day
            pest_alert = self._get_pest_alert_for_day(crop, current_stage_data, day_weather)
            
            # Weather warning
            weather_warning = self._get_weather_warning(day_weather, crop, current_stage)
            
            # Generate friendly advice
            advice = self._generate_daily_advice(
                crop, current_stage_data, das_on_day, day_weather, day_offset
            )
            
            days_plan.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day_label_en': DAY_LABELS[day_offset],
                'day_label_te': DAY_LABELS_TE[day_offset],
                'day_name': target_date.strftime('%A'),
                'das': das_on_day,  # Days After Sowing
                'priority': priority,
                'weather': {
                    'temp_max': round(day_weather.get('temp_max', 30), 1),
                    'temp_min': round(day_weather.get('temp_min', 20), 1),
                    'humidity': round(day_weather.get('humidity_avg', 60)),
                    'rainfall_mm': round(day_weather.get('rainfall_mm', 0), 1),
                    'condition': day_weather.get('condition', 'Clear'),
                    'icon': self._get_weather_icon(day_weather)
                },
                'tasks': tasks,
                'irrigation': irrigation,
                'fertilizer': fertilizer,
                'pest_alert': pest_alert,
                'weather_warning': weather_warning,
                'advice_en': advice['en'],
                'advice_te': advice['te']
            })
        
        # Week summary
        week_summary = self._generate_week_summary(crop, stage_info, days_plan, weather)
        
        return {
            'subscription_id': subscription.get('subscriptionId'),
            'generated_at': datetime.now().isoformat(),
            'crop': crop,
            'crop_name_te': crop_data.get('name_te', crop),
            'area_acres': area_acres,
            'stage_info': stage_info,
            'current_weather': weather.get('current', {}),
            'week_summary_en': week_summary['en'],
            'week_summary_te': week_summary['te'],
            'days': days_plan,
            'next_stage': {
                'name': next_stage_data.get('name') if next_stage_data else None,
                'starts_in_days': next_stage_data.get('start_day', 0) - days_after_sowing if next_stage_data else None
            } if next_stage_data else None
        }
    
    def _calculate_day_priority(self, weather: Dict, stage_data: Dict, das: int, crop: str) -> str:
        """Calculate priority level for a day"""
        # High priority conditions
        if weather.get('rainfall_mm', 0) > 30:
            return 'high'
        if weather.get('temp_max', 30) > 40:
            return 'high'
        if stage_data:
            # Check if critical activity due
            for activity in stage_data.get('critical_activities', []):
                if isinstance(activity, dict) and activity.get('day') == das:
                    if activity.get('priority') in ['high', 'critical']:
                        return 'high'
        return 'normal'
    
    def _get_tasks_for_day(self, crop: str, stage_data: Dict, das: int, day_offset: int, 
                          weather: Dict, stage_info: Dict, area_acres: float) -> List[Dict]:
        """Get specific tasks for a given day"""
        tasks = []
        
        if not stage_data:
            return [{'task_en': 'No specific tasks', 'task_te': 'ప్రత్యేక పనులు లేవు', 'type': 'info'}]
        
        # Get activities from stage data that match this DAS
        for activity in stage_data.get('critical_activities', []):
            if isinstance(activity, dict):
                activity_day = activity.get('day', 0)
                # Show activities due within 2 days
                if das - 1 <= activity_day <= das + 1:
                    task_text = activity.get('task', '')
                    tasks.append({
                        'task_en': task_text,
                        'task_te': task_text,  # Add Telugu translation
                        'type': 'critical' if activity.get('priority') == 'critical' else 'important',
                        'priority': activity.get('priority', 'normal')
                    })
        
        # Add weather-based tasks
        if weather.get('rainfall_mm', 0) > 20:
            tasks.insert(0, {
                'task_en': f"⚠️ Rain expected ({weather.get('rainfall_mm')}mm) - Postpone spraying/fertilizer",
                'task_te': f"⚠️ వర్షం ({weather.get('rainfall_mm')}mm) - పిచికారీ/ఎరువులు వాయిదా",
                'type': 'weather',
                'priority': 'high'
            })
        
        if weather.get('temp_max', 30) > 38:
            tasks.insert(0, {
                'task_en': f"🔥 High temperature ({weather.get('temp_max')}°C) - Irrigate in evening only",
                'task_te': f"🔥 అధిక ఉష్ణోగ్రత ({weather.get('temp_max')}°C) - సాయంత్రం మాత్రమే నీరు",
                'type': 'weather',
                'priority': 'high'
            })
        
        # Add pest scouting task if applicable
        if day_offset == 0:  # Today only
            pest_focus = stage_data.get('pest_focus', [])
            if pest_focus:
                tasks.append({
                    'task_en': f"🔍 Scout for: {', '.join(pest_focus)}",
                    'task_te': f"🔍 పురుగుల కోసం చూడండి: {', '.join(pest_focus)}",
                    'type': 'scouting',
                    'priority': 'medium'
                })
        
        # Add good weather opportunity
        if weather.get('rainfall_mm', 0) == 0 and 25 <= weather.get('temp_max', 30) <= 35:
            if day_offset > 0:  # Not today
                tasks.append({
                    'task_en': "✅ Good day for spraying/fertilizer application",
                    'task_te': "✅ పిచికారీ/ఎరువులకు మంచి రోజు",
                    'type': 'opportunity',
                    'priority': 'normal'
                })
        
        if not tasks:
            tasks.append({
                'task_en': "📋 Normal operations - monitor crop health",
                'task_te': "📋 సాధారణ పనులు - పంట ఆరోగ్యం పరిశీలించండి",
                'type': 'routine',
                'priority': 'normal'
            })
        
        return tasks
    
    def _get_irrigation_for_day(self, crop: str, stage: str, weather: Dict, day_offset: int, das: int) -> Dict:
        """Get irrigation advice for a specific day"""
        rain_expected = weather.get('rainfall_mm', 0)
        
        if rain_expected > 20:
            return {
                'needed': False,
                'reason_en': f"Skip irrigation - {rain_expected}mm rain expected",
                'reason_te': f"నీరు వద్దు - {rain_expected}mm వర్షం",
                'icon': '🌧️'
            }
        
        if weather.get('temp_max', 30) > 38:
            return {
                'needed': True,
                'reason_en': "Irrigate in evening due to high temperature",
                'reason_te': "అధిక ఉష్ణోగ్రత వల్ల సాయంత్రం నీరు పెట్టండి",
                'time': 'evening',
                'icon': '💧'
            }
        
        # Default based on typical irrigation frequency
        irrigation_days = {
            'Paddy': [0, 3, 7],  # Every 3-4 days
            'Cotton': [0, 7],
            'Maize': [0, 5],
            'Wheat': [0, 7],
            'Sugarcane': [0, 7],
            'Tomato': [0, 2, 4, 6],
            'Onion': [0, 3, 6],
            'Chilli': [0, 3, 6]
        }
        
        crop_schedule = irrigation_days.get(crop, [0, 7])
        if day_offset in crop_schedule:
            return {
                'needed': True,
                'reason_en': "Scheduled irrigation day",
                'reason_te': "షెడ్యూల్డ్ నీటిపారుదల రోజు",
                'icon': '💧'
            }
        
        return {
            'needed': False,
            'reason_en': "No irrigation needed",
            'reason_te': "నీటిపారుదల అవసరం లేదు",
            'icon': '✓'
        }
    
    def _get_fertilizer_for_day(self, crop: str, stage_data: Dict, das: int, area_acres: float) -> Dict:
        """Check if fertilizer is due on this day"""
        if not stage_data:
            return None
        
        # Check fertilizer schedule in stage data
        fert_schedule = stage_data.get('fertilizer_schedule', [])
        for fert in fert_schedule:
            if isinstance(fert, dict):
                fert_day = fert.get('day', 0)
                if das - 1 <= fert_day <= das + 1:
                    return {
                        'due': True,
                        'product': fert.get('product', 'NPK'),
                        'qty_per_acre': fert.get('qty_per_acre', 'As recommended'),
                        'total_qty': f"{float(fert.get('qty_per_acre', '0').split()[0]) * area_acres:.1f} kg" if 'kg' in str(fert.get('qty_per_acre', '')) else fert.get('qty_per_acre'),
                        'message_en': f"Apply {fert.get('product')} - {fert.get('qty_per_acre')} per acre",
                        'message_te': f"{fert.get('product')} వేయండి - ఎకరాకు {fert.get('qty_per_acre')}"
                    }
        
        return None
    
    def _get_pest_alert_for_day(self, crop: str, stage_data: Dict, weather: Dict) -> Dict:
        """Get pest/disease alert based on conditions"""
        if not stage_data:
            return None
        
        pest_focus = stage_data.get('pest_focus', [])
        disease_focus = stage_data.get('disease_focus', [])
        
        alerts = []
        
        # High humidity = disease risk
        if weather.get('humidity_avg', 60) > 80:
            if disease_focus:
                alerts.append(f"🦠 High humidity! Watch for: {', '.join(disease_focus)}")
        
        # Pest alerts
        if pest_focus:
            alerts.append(f"🔍 Scout for: {', '.join(pest_focus)}")
        
        if alerts:
            return {
                'has_alert': True,
                'alerts': alerts,
                'message_en': '; '.join(alerts),
                'message_te': f"పురుగులు/వ్యాధుల కోసం చూడండి"
            }
        
        return None
    
    def _get_weather_warning(self, weather: Dict, crop: str, stage: str) -> Dict:
        """Get weather warning if conditions are extreme"""
        warnings = []
        
        if weather.get('temp_max', 30) > 40:
            warnings.append({
                'type': 'heat',
                'icon': '🔥',
                'message_en': f"Extreme heat warning: {weather.get('temp_max')}°C expected",
                'message_te': f"తీవ్ర వేడి హెచ్చరిక: {weather.get('temp_max')}°C"
            })
        
        if weather.get('rainfall_mm', 0) > 50:
            warnings.append({
                'type': 'rain',
                'icon': '🌧️',
                'message_en': f"Heavy rain warning: {weather.get('rainfall_mm')}mm expected",
                'message_te': f"భారీ వర్షం హెచ్చరిక: {weather.get('rainfall_mm')}mm"
            })
        
        return warnings[0] if warnings else None
    
    def _get_weather_icon(self, weather: Dict) -> str:
        """Get emoji icon for weather condition"""
        rain = weather.get('rainfall_mm', 0)
        temp = weather.get('temp_max', 30)
        
        if rain > 20:
            return '🌧️'
        elif rain > 0:
            return '🌦️'
        elif temp > 38:
            return '🔥'
        elif temp > 32:
            return '☀️'
        else:
            return '⛅'
    
    def _generate_daily_advice(self, crop: str, stage_data: Dict, das: int, 
                               weather: Dict, day_offset: int) -> Dict:
        """Generate friendly daily advice"""
        stage_name = stage_data.get('name', 'Unknown') if stage_data else 'Unknown'
        
        # Context-aware advice
        if weather.get('rainfall_mm', 0) > 30:
            return {
                'en': f"🌧️ Rainy day ahead! Focus on drainage and avoid field operations. Good time to plan next week's activities.",
                'te': f"🌧️ వర్షం వస్తుంది! డ్రైనేజ్ పై దృష్టి పెట్టండి, పొలం పనులు వాయిదా వేయండి."
            }
        
        if weather.get('temp_max', 30) > 38:
            return {
                'en': f"🔥 Hot day! Irrigate only in evening. Avoid spraying 11am-4pm. Workers should take breaks.",
                'te': f"🔥 వేడి రోజు! సాయంత్రం మాత్రమే నీరు. 11am-4pm పిచికారీ వద్దు."
            }
        
        if day_offset == 0:  # Today
            return {
                'en': f"📅 Your {crop} is at {stage_name} stage (Day {das}). Check today's priority tasks above.",
                'te': f"📅 మీ {crop} {stage_name} దశలో ఉంది (రోజు {das}). పై పనులు చూడండి."
            }
        
        if weather.get('rainfall_mm', 0) == 0 and 25 <= weather.get('temp_max', 30) <= 35:
            return {
                'en': f"✅ Good weather expected! Ideal for spraying, fertilizer application, or field operations.",
                'te': f"✅ మంచి వాతావరణం! పిచికారీ, ఎరువులు, పొలం పనులకు అనువైన రోజు."
            }
        
        return {
            'en': f"📋 Day {das} of your {crop} crop. Continue regular monitoring.",
            'te': f"📋 మీ {crop} పంట రోజు {das}. సాధారణ పరిశీలన కొనసాగించండి."
        }
    
    def _generate_week_summary(self, crop: str, stage_info: Dict, days_plan: List, weather: Dict) -> Dict:
        """Generate summary for the entire week"""
        rain_days = sum(1 for d in days_plan if d['weather']['rainfall_mm'] > 5)
        hot_days = sum(1 for d in days_plan if d['weather']['temp_max'] > 38)
        high_priority_days = sum(1 for d in days_plan if d['priority'] == 'high')
        
        stage = stage_info.get('stage_name', 'Unknown')
        das = stage_info.get('days_after_sowing', 0)
        
        summary_en = f"📊 Week Overview: {crop} at {stage} stage (Day {das}-{das+6}). "
        summary_te = f"📊 వారం: {crop} {stage} దశ (రోజు {das}-{das+6}). "
        
        if rain_days > 0:
            summary_en += f"🌧️ {rain_days} rainy day(s) expected. "
            summary_te += f"🌧️ {rain_days} వర్షపు రోజులు. "
        
        if hot_days > 0:
            summary_en += f"🔥 {hot_days} hot day(s). "
            summary_te += f"🔥 {hot_days} వేడి రోజులు. "
        
        if high_priority_days > 0:
            summary_en += f"⚠️ {high_priority_days} day(s) need attention. "
            summary_te += f"⚠️ {high_priority_days} రోజులు శ్రద్ధ అవసరం. "
        
        return {'en': summary_en, 'te': summary_te}


# Singleton instance
_monitoring_service = None

def get_crop_monitoring_service() -> CropMonitoringService:
    """Get singleton instance of CropMonitoringService"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = CropMonitoringService()
    return _monitoring_service
