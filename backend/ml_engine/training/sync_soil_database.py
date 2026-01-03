"""
Sync Soil Database with Agritech.csv Data
Updates regions_soil_db.json with real soil data from Agritech.csv
"""

import os
import json
import pandas as pd
from collections import Counter

# Paths
AGRITECH_PATH = os.path.join(os.path.dirname(__file__), '../../Agritech.csv')
if not os.path.exists(AGRITECH_PATH):
    AGRITECH_PATH = os.path.join(os.path.dirname(__file__), '../../../Agritech.csv')
    
SOIL_DB_PATH = os.path.join(os.path.dirname(__file__), '../data/regions_soil_db.json')

# Soil type mapping from Agritech to our standard
SOIL_TYPE_MAPPING = {
    'Black': 'Black Cotton',
    'Alluvial': 'Alluvial',
    'Red': 'Red Soil',
    'Laterite': 'Laterite',
    'Peaty': 'Loamy',
    'Desert': 'Sandy',
    'Forest': 'Loamy',
    'Clay': 'Clay',
    'Sandy': 'Sandy',
    'Loamy': 'Loamy'
}


def load_agritech_data():
    """Load and process Agritech.csv"""
    df = pd.read_csv(AGRITECH_PATH)
    print(f"Loaded {len(df)} records from Agritech.csv")
    return df


def aggregate_by_district(df):
    """Aggregate soil data by state and district, taking most common values."""
    
    district_data = {}
    
    for state in df['state'].unique():
        state_df = df[df['state'] == state]
        
        for district in state_df['district'].unique():
            district_df = state_df[state_df['district'] == district]
            
            # Get most common soil type
            soil_counts = Counter(district_df['soil_type'])
            most_common_soil = soil_counts.most_common(1)[0][0]
            
            # Get averages for other values
            avg_ph = district_df['soil_pH'].mean()
            avg_n = district_df['nitrogen_mgkg'].mean()
            avg_p = district_df['phosphorus_mgkg'].mean()
            avg_k = district_df['potassium_mgkg'].mean()
            avg_lat = district_df['latitude'].mean()
            avg_lon = district_df['longitude'].mean()
            
            # Map soil type to our standard
            mapped_soil = SOIL_TYPE_MAPPING.get(most_common_soil, most_common_soil)
            
            key = f"{state}_{district}".lower().replace(" ", "_")
            
            district_data[key] = {
                "state": state,
                "district": district,
                "soil": mapped_soil,
                "original_soil": most_common_soil,
                "ph": round(avg_ph, 2),
                "n": round(avg_n, 0),
                "p": round(avg_p, 0),
                "k": round(avg_k, 0),
                "lat": round(avg_lat, 4),
                "lon": round(avg_lon, 4),
                "zone": f"{state} Region",
                "source": "Agritech.csv"
            }
            
            print(f"  {state}/{district}: {most_common_soil} → {mapped_soil}, pH={avg_ph:.2f}, N={avg_n:.0f}, P={avg_p:.0f}, K={avg_k:.0f}")
    
    return district_data


def update_soil_db(new_data):
    """Update regions_soil_db.json with Agritech data."""
    
    # Load existing database
    try:
        with open(SOIL_DB_PATH, 'r', encoding='utf-8') as f:
            existing_db = json.load(f)
        print(f"\nLoaded existing soil DB with {len(existing_db.get('districts', {}))} districts")
    except:
        existing_db = {"districts": {}, "mandals": {}}
    
    # Add/update districts from Agritech data
    if 'districts' not in existing_db:
        existing_db['districts'] = {}
    
    updated_count = 0
    added_count = 0
    
    for key, data in new_data.items():
        district_name = data['district'].lower()
        
        if district_name in existing_db['districts']:
            # Update existing entry with Agritech data
            existing_db['districts'][district_name].update({
                'soil': data['soil'],
                'ph': data['ph'],
                'n': data['n'],
                'p': data['p'],
                'k': data['k'],
                'lat': data['lat'],
                'lon': data['lon'],
                'source': 'Agritech.csv'
            })
            updated_count += 1
        else:
            # Add new district
            existing_db['districts'][district_name] = {
                'zone': data['zone'],
                'soil': data['soil'],
                'ph': data['ph'],
                'n': data['n'],
                'p': data['p'],
                'k': data['k'],
                'lat': data['lat'],
                'lon': data['lon'],
                'source': 'Agritech.csv'
            }
            added_count += 1
    
    # Save updated database
    with open(SOIL_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing_db, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Soil database updated!")
    print(f"   Updated: {updated_count} districts")
    print(f"   Added: {added_count} new districts")
    print(f"   Total: {len(existing_db.get('districts', {}))} districts")
    
    return existing_db


def main():
    print("=" * 60)
    print("🌱 Syncing Soil Database with Agritech.csv")
    print("=" * 60)
    
    # Load Agritech data
    df = load_agritech_data()
    
    # Get unique states
    print(f"\nStates in Agritech.csv: {df['state'].nunique()}")
    print(f"Districts in Agritech.csv: {df['district'].nunique()}")
    
    # Aggregate by district
    print("\nAggregating soil data by district:")
    district_data = aggregate_by_district(df)
    
    # Update soil database
    update_soil_db(district_data)
    
    print("\n" + "=" * 60)
    print("✅ Sync Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
