"""
Enhanced ML Crop Recommender Training with Agritech.csv Real Data
Uses real environmental data from Agritech.csv combined with crop profiles.
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
PROFILES_PATH = os.path.join(os.path.dirname(__file__), '../data/crop_profiles.json')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/crop_recommender_ml.joblib')
AGRITECH_PATH = os.path.join(os.path.dirname(__file__), '../../Agritech.csv')
# Also check root level
if not os.path.exists(AGRITECH_PATH):
    AGRITECH_PATH = os.path.join(os.path.dirname(__file__), '../../../Agritech.csv')

# Soil type mapping from Agritech to our system
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

# Standard soil types for encoding
SOIL_TYPES = [
    'Alluvial', 'Black Cotton', 'Black', 'Clay', 'Clayey', 'Laterite', 
    'Loamy', 'Red Soil', 'Red Sandy Loam', 'Sandy', 'Sandy Loam', 'Saline'
]

SEASONS = ['Kharif', 'Rabi', 'Zaid']

# Month to season mapping
MONTH_TO_SEASON = {
    'January': 'Rabi', 'February': 'Rabi', 'March': 'Zaid',
    'April': 'Zaid', 'May': 'Zaid', 'June': 'Kharif',
    'July': 'Kharif', 'August': 'Kharif', 'September': 'Kharif',
    'October': 'Rabi', 'November': 'Rabi', 'December': 'Rabi'
}


def load_profiles():
    with open(PROFILES_PATH, 'r') as f:
        return json.load(f)


def load_agritech_data():
    """Load real environmental data from Agritech.csv."""
    try:
        df = pd.read_csv(AGRITECH_PATH)
        logger.info(f"Loaded {len(df)} records from Agritech.csv")
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Map soil types to our standard
        if 'soil_type' in df.columns:
            df['mapped_soil_type'] = df['soil_type'].map(
                lambda x: SOIL_TYPE_MAPPING.get(x, 'Loamy')
            )
        
        # Map month to season
        if 'month' in df.columns:
            df['season'] = df['month'].map(MONTH_TO_SEASON)
        
        return df
    except Exception as e:
        logger.warning(f"Could not load Agritech.csv: {e}")
        return None


def generate_training_data_with_real_conditions(profiles, agritech_df, samples_per_crop=300):
    """
    Generate training data using REAL environmental conditions from Agritech.csv.
    For each crop profile, sample real environmental conditions and determine suitability.
    """
    data = []
    
    # If we have real data, use it
    if agritech_df is not None and len(agritech_df) > 0:
        logger.info("Using REAL environmental data from Agritech.csv")
        
        for crop_name, profile in profiles.items():
            suitable_soils = profile.get('soil_suitability', [])
            suitable_seasons = profile.get('season', [])
            min_temp = profile.get('min_temp', 15)
            max_temp = profile.get('max_temp', 35)
            ph_min = profile.get('ph_min', 5.5)
            ph_max = profile.get('ph_max', 8.0)
            
            # Sample from real data
            sampled = agritech_df.sample(n=min(samples_per_crop, len(agritech_df)), replace=True)
            
            for _, row in sampled.iterrows():
                # Get real environmental values
                soil_type = row.get('mapped_soil_type', row.get('soil_type', 'Loamy'))
                season = row.get('season', 'Rabi')
                temp = row.get('avg_temperature_c', 28)
                humidity = row.get('humidity_pct', 60)
                ph = row.get('soil_ph', 7.0)
                n = row.get('nitrogen_mgkg', 150)
                p = row.get('phosphorus_mgkg', 50)
                k = row.get('potassium_mgkg', 150)
                rainfall = row.get('rainfall_mm', 50)
                
                # Estimate rain days from rainfall
                rain_days = min(int(rainfall / 30), 7)
                
                # Determine suitability based on conditions matching crop profile
                suitability_score = 0
                
                # Soil match (most important - 40 points)
                if any(s.lower() in soil_type.lower() or soil_type.lower() in s.lower() 
                       for s in suitable_soils):
                    suitability_score += 40
                
                # Season match (30 points)
                if season in suitable_seasons:
                    suitability_score += 30
                
                # Temperature match (15 points)
                if min_temp <= temp <= max_temp:
                    suitability_score += 15
                elif abs(temp - min_temp) <= 5 or abs(temp - max_temp) <= 5:
                    suitability_score += 7
                
                # pH match (15 points)
                if ph_min <= ph <= ph_max:
                    suitability_score += 15
                elif abs(ph - ph_min) <= 0.5 or abs(ph - ph_max) <= 0.5:
                    suitability_score += 7
                
                # Suitable if score >= 60
                suitable = 1 if suitability_score >= 60 else 0
                
                data.append({
                    'soil_type': soil_type,
                    'season': season,
                    'temperature': float(temp),
                    'humidity': float(humidity),
                    'ph': float(ph),
                    'nitrogen': float(n),
                    'phosphorus': float(p),
                    'potassium': float(k),
                    'rain_days': rain_days,
                    'crop': crop_name,
                    'suitable': suitable,
                    'source': 'agritech_real'
                })
        
        logger.info(f"Generated {len(data)} samples from real environmental data")
    
    # Also add some synthetic ideal conditions for robustness
    logger.info("Adding synthetic ideal conditions for each crop...")
    
    for crop_name, profile in profiles.items():
        suitable_soils = profile.get('soil_suitability', [])
        suitable_seasons = profile.get('season', [])
        min_temp = profile.get('min_temp', 15)
        max_temp = profile.get('max_temp', 35)
        ph_min = profile.get('ph_min', 5.5)
        ph_max = profile.get('ph_max', 8.0)
        
        # Add 100 ideal positive samples per crop
        for _ in range(100):
            soil = np.random.choice(suitable_soils)
            season = np.random.choice(suitable_seasons)
            temp = np.random.uniform(min_temp, max_temp)
            humidity = np.random.uniform(40, 80)
            ph = np.random.uniform(ph_min, ph_max)
            n = np.random.uniform(100, 300)
            p = np.random.uniform(30, 80)
            k = np.random.uniform(100, 350)
            rain_days = np.random.randint(0, 5)
            
            data.append({
                'soil_type': soil,
                'season': season,
                'temperature': temp,
                'humidity': humidity,
                'ph': ph,
                'nitrogen': n,
                'phosphorus': p,
                'potassium': k,
                'rain_days': rain_days,
                'crop': crop_name,
                'suitable': 1,
                'source': 'synthetic_ideal'
            })
        
        # Add 50 negative samples (unsuitable conditions)
        for _ in range(50):
            # Pick unsuitable conditions
            all_soils = SOIL_TYPES.copy()
            unsuitable_soils = [s for s in all_soils if s not in suitable_soils]
            if not unsuitable_soils:
                unsuitable_soils = all_soils
            soil = np.random.choice(unsuitable_soils)
            
            all_seasons = SEASONS.copy()
            unsuitable_seasons = [s for s in all_seasons if s not in suitable_seasons]
            if not unsuitable_seasons:
                unsuitable_seasons = all_seasons
            season = np.random.choice(unsuitable_seasons)
            
            # Extreme conditions
            temp = np.random.choice([
                np.random.uniform(min_temp - 15, min_temp - 5),
                np.random.uniform(max_temp + 5, max_temp + 15)
            ])
            humidity = np.random.choice([np.random.uniform(10, 30), np.random.uniform(85, 100)])
            ph = np.random.choice([
                np.random.uniform(3, ph_min - 0.5),
                np.random.uniform(ph_max + 0.5, 10)
            ])
            n = np.random.uniform(50, 400)
            p = np.random.uniform(10, 100)
            k = np.random.uniform(50, 400)
            rain_days = np.random.randint(0, 7)
            
            data.append({
                'soil_type': soil,
                'season': season,
                'temperature': temp,
                'humidity': humidity,
                'ph': ph,
                'nitrogen': n,
                'phosphorus': p,
                'potassium': k,
                'rain_days': rain_days,
                'crop': crop_name,
                'suitable': 0,
                'source': 'synthetic_negative'
            })
    
    logger.info(f"Total training samples: {len(data)}")
    return pd.DataFrame(data)


def preprocess_data(df):
    """Encode categorical features and scale numerical features."""
    
    # Encode soil type
    soil_encoder = LabelEncoder()
    soil_encoder.fit(SOIL_TYPES)
    df['soil_encoded'] = df['soil_type'].apply(
        lambda x: soil_encoder.transform([x])[0] if x in SOIL_TYPES else 0
    )
    
    # Encode season
    season_encoder = LabelEncoder()
    season_encoder.fit(SEASONS)
    df['season_encoded'] = df['season'].apply(
        lambda x: season_encoder.transform([x])[0] if x in SEASONS else 0
    )
    
    # Encode crop
    crop_encoder = LabelEncoder()
    df['crop_encoded'] = crop_encoder.fit_transform(df['crop'])
    
    # Feature columns
    feature_cols = [
        'soil_encoded', 'season_encoded', 'temperature', 'humidity',
        'ph', 'nitrogen', 'phosphorus', 'potassium', 'rain_days', 'crop_encoded'
    ]
    
    X = df[feature_cols].values
    y = df['suitable'].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, soil_encoder, season_encoder, crop_encoder, scaler, feature_cols


def train_model(X, y):
    """Train a RandomForest classifier with cross-validation."""
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info("Training RandomForest classifier with real data...")
    
    model = RandomForestClassifier(
        n_estimators=150,  # More trees for real data
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    logger.info(f"Cross-validation scores: {cv_scores}")
    logger.info(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Final training
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Test Accuracy: {test_accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Unsuitable', 'Suitable']))
    
    return model, test_accuracy


def save_model(model, scaler, encoders, accuracy, feature_cols):
    """Save model and preprocessing objects."""
    
    model_data = {
        'model': model,
        'scaler': scaler,
        'soil_encoder': encoders[0],
        'season_encoder': encoders[1],
        'crop_encoder': encoders[2],
        'feature_cols': feature_cols,
        'accuracy': accuracy,
        'soil_types': SOIL_TYPES,
        'seasons': SEASONS,
        'crops': list(encoders[2].classes_),
        'trained_with': 'agritech_real_data'
    }
    
    joblib.dump(model_data, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")
    
    # Save accuracy report
    report_path = MODEL_PATH.replace('.joblib', '_report.json')
    with open(report_path, 'w') as f:
        json.dump({
            'accuracy': accuracy,
            'model_type': 'RandomForestClassifier',
            'n_estimators': 150,
            'features': feature_cols,
            'n_crops': len(encoders[2].classes_),
            'crops': list(encoders[2].classes_),
            'trained_with': 'Agritech.csv + crop_profiles.json'
        }, f, indent=2)
    
    return model_data


def main():
    print("=" * 60)
    print("🌾 Enhanced ML Crop Recommender Training")
    print("   Using REAL Agritech.csv Environmental Data")
    print("=" * 60)
    
    # Load crop profiles
    profiles = load_profiles()
    logger.info(f"Loaded {len(profiles)} crop profiles")
    
    # Load real environmental data
    agritech_df = load_agritech_data()
    
    # Generate training data
    logger.info("Generating training data with real conditions...")
    df = generate_training_data_with_real_conditions(profiles, agritech_df)
    
    # Show data distribution
    source_counts = df['source'].value_counts()
    logger.info(f"Data source distribution:\n{source_counts}")
    
    # Preprocess
    logger.info("Preprocessing data...")
    X, y, soil_enc, season_enc, crop_enc, scaler, feature_cols = preprocess_data(df)
    
    logger.info(f"Positive samples: {sum(y)}, Negative samples: {len(y) - sum(y)}")
    
    # Train
    model, accuracy = train_model(X, y)
    
    # Save
    save_model(model, scaler, (soil_enc, season_enc, crop_enc), accuracy, feature_cols)
    
    print("\n" + "=" * 60)
    print(f"✅ Training Complete!")
    print(f"   Model Accuracy: {accuracy:.2%}")
    print(f"   Trained with: Agritech.csv real data + synthetic")
    print("=" * 60)
    
    return accuracy


if __name__ == "__main__":
    main()
