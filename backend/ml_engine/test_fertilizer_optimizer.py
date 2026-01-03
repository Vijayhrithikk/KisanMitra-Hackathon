"""
Test Fertilizer Optimizer Service
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.fertilizer_optimizer_service import fertilizer_optimizer

# Test 1: Rice with NPK deficit
print("=" * 60)
print("TEST 1: Rice with Nitrogen and Phosphorus deficit")
print("=" * 60)

result = fertilizer_optimizer.get_complete_recommendation(
    crop_name='rice',
    current_npk={'n': 80, 'p': 30, 'k': 200},  # Low N and P, excess K
    soil_type='Loamy',
    farming_type='balanced'
)

import json
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("TEST 2: Cotton with balanced soil")
print("=" * 60)

result2 = fertilizer_optimizer.get_complete_recommendation(
    crop_name='cotton',
    current_npk={'n': 140, 'p': 55, 'k': 55},
    soil_type='Black Cotton',
    farming_type='balanced'
)

print(json.dumps(result2, indent=2))

print("\n" + "=" * 60)
print("TEST 3: Wheat with organic preference")
print("=" * 60)

result3 = fertilizer_optimizer.get_complete_recommendation(
    crop_name='wheat',
    current_npk={'n': 60, 'p': 40, 'k': 25},
    soil_type='Alluvial',
    farming_type='organic'
)

print(json.dumps(result3, indent=2))

print("\n✅ All tests completed!")
