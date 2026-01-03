import requests
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENWEATHER_KEY")
        self.base_url_current = "https://api.openweathermap.org/data/2.5/weather"
        self.base_url_forecast = "https://api.openweathermap.org/data/2.5/forecast"

    def get_current_weather(self, lat, lon):
        """
        Fetches current weather for ML input.
        Returns: {temp (C), humidity (%), moisture (mock), desc}
        """
        if not self.api_key:
            logger.warning("No OpenWeather API Key. Using mock weather.")
            return {"temp": 30.0, "humidity": 60.0, "moisture": 40.0, "desc": "Sunny (Mock)"}

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url_current, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "moisture": 45.0, # Soil moisture not available in standard API, mocking it
                "desc": data["weather"][0]["description"]
            }

        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return {"temp": 28.0, "humidity": 55.0, "moisture": 50.0, "desc": "Error Fallback"}

    def get_forecast(self, lat, lon):
        """
        Fetches 5-day forecast and generates 3-month seasonal projection.
        """
        if not self.api_key:
            return self._get_mock_forecast()

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url_forecast, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process 5-day forecast (taking one reading per day at noon)
            daily_forecast = []
            seen_dates = set()
            
            for item in data['list']:
                dt = datetime.fromtimestamp(item['dt'])
                date_str = dt.strftime('%Y-%m-%d')
                
                if date_str not in seen_dates and dt.hour >= 12:
                    seen_dates.add(date_str)
                    daily_forecast.append({
                        "date": date_str,
                        "temp": item['main']['temp'],
                        "humidity": item['main']['humidity'],
                        "desc": item['weather'][0]['description'],
                        "icon": item['weather'][0]['icon']
                    })
                    if len(daily_forecast) >= 5:
                        break
            
            seasonal_projection = self._generate_seasonal_projection()
            
            return {
                "daily": daily_forecast,
                "seasonal": seasonal_projection
            }

        except Exception as e:
            logger.error(f"Forecast fetch error: {e}")
            return self._get_mock_forecast()

    def _generate_seasonal_projection(self):
        """
        Generates a 3-month outlook based on the current month in India.
        """
        current_month = datetime.now().month
        
        # Logic for Indian Seasons
        if 6 <= current_month <= 9:
            season = "Monsoon (Kharif)"
            outlook = "High rainfall expected. Suitable for water-intensive crops like Paddy."
            trend = "Wet & Humid"
        elif 10 <= current_month <= 1:
            season = "Post-Monsoon (Rabi)"
            outlook = "Cooler temperatures, dry weather. Ideal for Wheat, Pulses."
            trend = "Cool & Dry"
        elif 2 <= current_month <= 5:
            season = "Summer (Zaid)"
            outlook = "High temperatures, low humidity. Irrigation crucial for Vegetables/Fruits."
            trend = "Hot & Dry"
        else:
            season = "Transition"
            outlook = "Variable conditions."
            trend = "Moderate"
            
        # Generate next 3 months
        months = []
        for i in range(1, 4):
            future_date = datetime.now() + timedelta(days=30*i)
            months.append(future_date.strftime("%B"))
            
        return {
            "season": season,
            "outlook": outlook,
            "trend": trend,
            "months": months
        }

    def _get_mock_forecast(self):
        return {
            "daily": [
                {"date": "2023-10-01", "temp": 30, "humidity": 60, "desc": "Sunny", "icon": "01d"},
                {"date": "2023-10-02", "temp": 29, "humidity": 65, "desc": "Cloudy", "icon": "03d"},
                {"date": "2023-10-03", "temp": 28, "humidity": 70, "desc": "Rain", "icon": "10d"},
                {"date": "2023-10-04", "temp": 29, "humidity": 60, "desc": "Sunny", "icon": "01d"},
                {"date": "2023-10-05", "temp": 30, "humidity": 55, "desc": "Sunny", "icon": "01d"}
            ],
            "seasonal": self._generate_seasonal_projection()
        }
