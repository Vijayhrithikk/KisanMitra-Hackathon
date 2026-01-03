import requests
import json

url = "http://localhost:8001/daily-advisory"
data = {
    "lat": 17.385,
    "lon": 78.487,
    "crop": "Rice",
    "sowing_date": "2025-11-01"
}

try:
    print(f"Sending POST to {url} with data: {data}")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("\n✅ Success! Response:")
        # Print pretty JSON
        print(json.dumps(response.json(), indent=2))
        
        # Check specific fields
        adv = response.json().get('advisory', {})
        print(f"\n--- Analysis ---")
        print(f"Tasks Count: {len(adv.get('daily_tasks', []))}")
        print(f"Alerts Count: {len(adv.get('alerts', []))}")
        print(f"Priority Action: {adv.get('priority_action')}")
    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")
