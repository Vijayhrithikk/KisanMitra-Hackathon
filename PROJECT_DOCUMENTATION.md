# KisanMitra-AI v2 - Complete Project Documentation

## 🌾 Project Overview

**KisanMitra-AI** is an intelligent agricultural advisory platform designed for Indian farmers. It provides AI-powered crop recommendations, fertilizer optimization, weather forecasting, and market price analysis. The application is built as a **mobile-first PWA (Progressive Web App)** locked to 414px viewport.

---

## 🏗️ Architecture

### Frontend (React + Vite)
```
src/
├── pages/
│   ├── CropRecommendation.jsx    # Main recommendation page
│   ├── FarmerDashboard.jsx       # Dashboard with stats
│   ├── Login.jsx                 # Phone + OTP authentication
│   ├── Home.jsx                  # Landing page
│   └── AIAssistant.jsx           # Telugu/English chatbot
├── components/
│   ├── Navbar.jsx                # Mobile navigation
│   ├── Footer.jsx                # App footer
│   └── ...
├── styles/
│   └── design-tokens.css         # Global CSS variables (ONLY global import allowed)
```

### Backend (FastAPI + Python)
```
backend/ml_engine/
├── app.py                        # Main FastAPI application
├── services/
│   ├── ml_recommendation_service.py   # RandomForest ML model
│   ├── market_price_service.py        # AGMARKNET price scraping (4 parallel workers)
│   ├── weather_history_service.py     # IMD rainfall normals
│   ├── nasa_power_service.py          # NASA satellite 5-year historical weather
│   ├── soil_research_agent.py         # Multi-source soil data (5 parallel workers)
│   ├── fertilizer_optimizer_service.py # NPK deficit & fertilizer planning
│   ├── decision_simulator_service.py   # Risk analysis engine
│   ├── confidence_scoring_service.py   # Confidence metrics
│   ├── season_service.py              # Kharif/Rabi/Summer detection
│   ├── soil_service.py                # Soil database lookup
│   └── web_scraper.py                 # General web scraping utility
├── data/
│   ├── crop_profiles.json           # Detailed crop requirements
│   ├── regions_soil_db.json         # State/District/Mandal soil data
│   ├── fertilizer_database.json     # Fertilizer products & costs
│   └── price_cache/                 # Cached market prices
├── training/
│   └── train_model.py               # ML model training script
└── models/
    └── crop_model.pkl               # Trained RandomForest model
```

---

## 🔌 API Endpoints

### Main Endpoint: `/recommend` (POST)
**Request:**
```json
{
  "location_name": "Guntur",
  "manual_soil_type": null,
  "lat": 16.3067,
  "lon": 80.4365,
  "include_risk_analysis": true,
  "show_alternatives": true,
  "custom_npk": {
    "N": 180,
    "P": 45,
    "K": 220,
    "ph": 7.2
  }
}
```

**Response:**
```json
{
  "location": "Guntur",
  "model_type": "ml",
  "context": {
    "season": "Rabi",
    "season_desc": "Winter crop season...",
    "soil_type": "Black Cotton",
    "soil_zone": "Guntur agricultural zone",
    "soil_source": "database",
    "soil_params": {"ph": 7.8, "n": 200, "p": 50, "k": 280},
    "weather": {
      "temp": 28,
      "humidity": 60,
      "desc": "Clear",
      "rain_days": 2,
      "weather_risk": "Low"
    },
    "weather_history": {
      "district": "Guntur",
      "annual_rainfall_mm": 850,
      "rainfall_zone": "Medium Rainfall",
      "irrigation_dependency": "High"
    },
    "nasa_forecast": {
      "source": "NASA_POWER_5YR_HISTORICAL",
      "growing_season": {"start_month": 10, "duration_months": 3},
      "weekly_forecast": [
        {
          "week": 1,
          "month": "December",
          "temp_max": 28.6,
          "temp_min": 18.7,
          "rainfall_mm": 11.2,
          "humidity": 81.7,
          "solar_radiation": 14.1,
          "risks": []
        }
      ]
    },
    "confidence": {
      "soil": 90,
      "weather": 85,
      "ml_prediction": 78,
      "overall": 84
    }
  },
  "recommendations": [
    {
      "crop": "Paddy",
      "confidence": 92,
      "yield_potential": "High",
      "risk_factor": "Low",
      "water_needs": "High",
      "market_price": {
        "price": 2300,
        "min_price": 2070,
        "max_price": 2530,
        "unit": "₹/quintal",
        "trend": "stable",
        "source": "MSP 2024-25",
        "live": false,
        "msp": true
      },
      "water_adequacy": {
        "adequacy": "Inadequate",
        "irrigation_advice": "Supplement with 2-3 irrigations"
      },
      "risk_analysis": {
        "loss_probability": 25,
        "risk_level": "Low"
      },
      "decision_grade": {
        "grade": "A",
        "label": "Highly Recommended"
      },
      "fertilizer_plan": {
        "npk_deficit": {"n": -20, "p": 10, "k": -40},
        "recommendations": [],
        "schedule": [],
        "total_cost": 2400
      }
    }
  ]
}
```

---

## 🛠️ Key Services

### 1. ML Recommendation Service
- **Model**: RandomForest Classifier (100% accuracy on training data)
- **Features**: soil_type, season, temp, humidity, pH, N, P, K, rain_days
- **Output**: Top 5 crop recommendations with confidence scores
- **Fallback**: Rule-based recommendations if ML fails

### 2. Market Price Service (4 Parallel Workers)
- DataGovWorker (data.gov.in API - most reliable)
- AgmarknetWorker (AGMARKNET web scraping)
- ENAMWorker (eNAM National Market)
- APAgrisnetWorker (State-specific AP data)
- **MSP Validation**: Rejects prices outside 0.3x-5x of expected MSP
- **Caching**: 3-hour TTL

### 3. Soil Research Agent (5 Parallel Workers)
- DataGovSoilWorker (Government data)
- SoilHealthCardWorker (Portal scraping)
- WikipediaWorker (Encyclopedia)
- NBSSWorker (National Soil Survey)
- WebSearchWorker (DuckDuckGo search)
- **Auto-research**: Researches unknown regions automatically

### 4. NASA Power Service
- **API**: NASA POWER satellite data (5-year historical)
- **Output**: 12-week growing season forecast
- **Risk Alerts**: Heat stress, cold stress, drought, flood, fungal disease

### 5. Weather History Service
- **Data**: IMD (India Meteorological Department) normals
- **Coverage**: AP, Telangana, Karnataka, TN, Maharashtra
- Seasonal rainfall breakdown (Kharif, Rabi, Summer)
- Crop-specific water requirements (16 crops)

### 6. Fertilizer Optimizer Service
- NPK deficit calculation
- Product recommendations from 50+ fertilizer database
- Week-by-week application schedule
- Cost-benefit analysis

---

## ⚡ Performance Optimizations

### Parallel Execution (ThreadPoolExecutor)
Steps 9-11 run concurrently (50-70% faster):
- Market Prices
- Weather History
- NASA Forecast

### Response Times
| Scenario | Time |
|----------|------|
| Cold Start | ~10s |
| Warm Cache | ~6s |

---

## 📱 Frontend Features

### CropRecommendation.jsx
- Location search with geocoding
- Soil image classification (AI)
- Custom NPK input from soil reports
- Recommendation cards with market price, water adequacy, risk analysis

### AI Assistant
- Telugu + English support
- Intent recognition for navigation
- Voice input support

### Design System
- **Mobile-first**: Locked to 414px viewport
- **CSS**: Component-specific CSS (no global styles except design-tokens.css)

---

## 🔐 Environment Variables

```env
# backend/.env
OWM_API_KEY=your_openweathermap_api_key
```

---

## 🚀 Running the Application

### Frontend
```bash
npm install
npm run dev    # http://localhost:5173
```

### Backend
```bash
cd backend/ml_engine
pip install -r requirements.txt
python app.py  # http://localhost:8001
```

---

## 📊 Data Sources

| Source | Type | Used For |
|--------|------|----------|
| OpenWeatherMap | API | Live weather + 5-day forecast |
| NASA POWER | API | 5-year historical satellite data |
| AGMARKNET | Web Scraping | Live mandi prices |
| data.gov.in | API | Agricultural market data |
| IMD Normals | Static | Historical rainfall patterns |

---

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main FastAPI server with /recommend endpoint |
| `ml_recommendation_service.py` | ML model inference |
| `market_price_service.py` | 4-worker parallel price fetching |
| `soil_research_agent.py` | 5-worker parallel soil research |
| `nasa_power_service.py` | 3-month weather forecast |
| `CropRecommendation.jsx` | Main UI for recommendations |
| `design-tokens.css` | Global CSS variables |
| `regions_soil_db.json` | Soil database by region |
| `crop_profiles.json` | Crop requirements database |

---

## 📌 Important Notes

1. **Mobile-Only**: UI locked to 414px - no desktop layouts
2. **CSS Rules**: Only import design-tokens.css globally
3. **API Validation**: Prices validated against MSP ranges
4. **Parallel Execution**: Steps 9-11 run in parallel
5. **Caching**: Price (3h), NASA (24h), Soil (30 days)
6. **Fallbacks**: Every service has graceful fallback

---

*Generated for KisanMitra-AI v2 - December 2024*
