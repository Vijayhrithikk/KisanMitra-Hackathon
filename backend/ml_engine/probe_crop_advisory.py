import requests
import json
import time

url = "http://localhost:8001/crop-advisory"
data = {
    "crop": "Rice",
    "lat": 17.385,
    "lon": 78.487,
    "sowing_date": "2025-11-01",
    "language": "en"
}

try:
    print(f"Sending POST to {url}...")
    start = time.time()
    response = requests.post(url, json=data)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"\n✅ Success! ({elapsed:.2f}s)")
        result = response.json()
        adv = result.get('advisory', {})
        
        # Check fertilizer plan
        fp = adv.get('fertilizer_plan')
        print(f"\n🌱 Fertilizer Plan Present: {'YES' if fp else 'NO'}")
        if fp:
            print(f"   Items: {len(fp.get('fertilizer_recommendations', []))}")
            print(f"   Cost: {fp.get('cost_benefit_analysis', {}).get('total_cost')}")
        
        # Check weekly advisory
        weeks = adv.get('weekly_advisory', [])
        print(f"\n📅 Weekly Advisory Weeks: {len(weeks)}")
        if weeks:
            print(f"   First Week: {weeks[0].get('date_range')}")
            print(f"   First Week Tasks: {len(weeks[0].get('tasks', []))}")
            print(f"   First Week Weather: {weeks[0].get('weather')}")
            
        # Check alerts
        alerts = adv.get('alerts', [])
        print(f"\n⚠️ Alerts: {len(alerts)}")
        for a in alerts:
            print(f"   - {a.get('name_en')}: {a.get('message_en')}")

    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")
