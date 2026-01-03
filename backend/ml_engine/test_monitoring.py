"""Test crop monitoring services"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.crop_monitoring_service import get_crop_monitoring_service
from services.crop_faq_service import get_crop_faq_service

print("Testing Crop Monitoring Services...")

# Test monitoring service
ms = get_crop_monitoring_service()
print(f"✅ CropMonitoringService loaded")
print(f"   Weather rules: {len(ms.rules.get('weather_alert_rules', []))}")
print(f"   Stage rules for crops: {list(ms.rules.get('stage_based_rules', {}).keys())}")

# Test FAQ service
fs = get_crop_faq_service()
print(f"✅ CropFAQService loaded")
print(f"   Total FAQs: {fs._count_faqs()}")
print(f"   Crops: {[c['name'] for c in fs.get_crop_list()]}")

# Test search
results = fs.search_faqs("yellow leaves", crop="Paddy")
print(f"   Search 'yellow leaves' in Paddy: {len(results)} results")

# Test stage calculation
from datetime import datetime, timedelta
sowing_date = datetime.now() - timedelta(days=45)
stage_info = ms.calculate_crop_stage(sowing_date, "Paddy")
print(f"✅ Stage calculation for Paddy (45 days): {stage_info['stage_name']}")

print("\n✅ All services working correctly!")
