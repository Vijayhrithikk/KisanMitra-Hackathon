"""
Test the updated crop recommendation model
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.ml_recommendation_service import MLRecommendationService

service = MLRecommendationService()

# Test Case 1: Summer vegetable growing (Zaid season)
print("=" * 60)
print("TEST 1: Summer Vegetable Growing (Zaid Season)")
print("=" * 60)
recommendations = service.get_recommendations(
    soil_type="Loamy",
    season="Zaid",
    temp=28,
    humidity=65,
    soil_ph=6.5,
    soil_n=150,
    soil_p=40,
    soil_k=120,
    forecast={"rain_days": 1}
)

print(f"Number of recommendations: {len(recommendations)}")
for i, rec in enumerate(recommendations[:5], 1):
    print(f"\n{i}. {rec['crop']} - Confidence: {rec['confidence']}%")
    print(f"   Yield: {rec['yield_potential']}, Risk: {rec['risk_factor']}, Water: {rec['water_needs']}")
    print(f"   Reason: {rec.get('reason', 'N/A')[:100]}...")

# Test Case 2: Winter fruit cultivation (Rabi season)
print("\n" + "=" * 60)
print("TEST 2: Winter Fruit Cultivation (Rabi Season)")
print("=" * 60)
recommendations = service.get_recommendations(
    soil_type="Sandy Loam",
    season="Rabi",
    temp=18,
    humidity=55,
    soil_ph=6.0,
    soil_n=100,
    soil_p=50,
    soil_k=150,
    forecast={"rain_days": 0}
)

print(f"Number of recommendations: {len(recommendations)}")
for i, rec in enumerate(recommendations[:5], 1):
    print(f"\n{i}. {rec['crop']} - Confidence: {rec['confidence']}%")
    print(f"   Yield: {rec['yield_potential']}, Risk: {rec['risk_factor']}, Water: {rec['water_needs']}")
    print(f"   Reason: {rec.get('reason', 'N/A')[:100]}...")

# Test Case 3: Monsoon crops (Kharif season)
print("\n" + "=" * 60)
print("TEST 3: Monsoon Crops (Kharif Season)")
print("=" * 60)
recommendations = service.get_recommendations(
    soil_type="Black Cotton",
    season="Kharif",
    temp=26,
    humidity=75,
    soil_ph=7.5,
    soil_n=200,
    soil_p=55,
    soil_k=320,
    forecast={"rain_days": 4}
)

print(f"Number of recommendations: {len(recommendations)}")
for i, rec in enumerate(recommendations[:5], 1):
    print(f"\n{i}. {rec['crop']} - Confidence: {rec['confidence']}%")
    print(f"   Yield: {rec['yield_potential']}, Risk: {rec['risk_factor']}, Water: {rec['water_needs']}")
    print(f"   Reason: {rec.get('reason', 'N/A')[:100]}...")

# Model info
print("\n" + "=" * 60)
print("MODEL INFORMATION")
print("=" * 60)
info = service.get_model_info()
print(f"Model Type: {info['type']}")
print(f"Loaded: {info['loaded']}")
if info['loaded']:
    print(f"Accuracy: {info['accuracy']:.2%}")
    print(f"Number of crops: {info['n_crops']}")
    print(f"Crops: {', '.join(info['crops'][:10])}... (showing first 10)")
