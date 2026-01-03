import requests
import json
import time

URL = "http://localhost:8001/recommend"
PAYLOAD = {
    "location_name": "Guntur, Andhra Pradesh",
    "lat": 16.3067,
    "lon": 80.4365,
    "manual_soil_type": "Black Cotton",
    "include_risk_analysis": True,
    "show_alternatives": True
}

def test_recommendation_speed():
    print(f"Testing {URL}...")
    start_time = time.time()
    
    try:
        response = requests.post(URL, json=PAYLOAD, timeout=30)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            recs = data.get("recommendations", [])
            print(f"Received {len(recs)} recommendations")
            
            if recs:
                first_rec = recs[0]
                print(f"Top Recommendation: {first_rec.get('crop')}")
                
                # Check for enhanced data
                has_market = 'market_price' in first_rec
                has_weather_hist = 'weather_history' in data.get('context', {})
                has_nasa = 'nasa_forecast' in data.get('context', {})
                
                print(f"Market Price Data: {'✅ Present' if has_market else '❌ Missing'}")
                print(f"Weather History: {'✅ Present' if has_weather_hist else '❌ Missing'}")
                print(f"NASA Forecast: {'✅ Present' if has_nasa else '❌ Missing'}")
                
                if duration < 5.0:
                    print("✅ SPEED TEST PASSED (< 5s)")
                else:
                    print("⚠️ SPEED TEST WARNING (> 5s)")
            else:
                print("❌ No recommendations returned")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_recommendation_speed()
