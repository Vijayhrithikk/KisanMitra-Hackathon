"""
ML-Based Crop Recommendation Training Script
Generates synthetic training data and trains a RandomForest classifier.
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load crop profiles
PROFILES_PATH = os.path.join(os.path.dirname(__file__), '../data/crop_profiles.json')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/crop_recommender_ml.joblib')

# Encoding mappings
SOIL_TYPES = [
    'Alluvial', 'Black Cotton', 'Black', 'Clay', 'Clayey', 'Laterite', 
    'Loamy', 'Red Soil', 'Red Sandy Loam', 'Sandy', 'Sandy Loam', 'Saline'
]

SEASONS = ['Kharif', 'Rabi', 'Zaid']

WATER_NEEDS = {'Low': 0, 'Medium': 1, 'High': 2}
RISK_LEVELS = {'Low': 0, 'Medium': 1, 'High': 2}
YIELD_LEVELS = {'Low': 0, 'Medium': 1, 'High': 2}


def load_profiles():
    with open(PROFILES_PATH, 'r') as f:
        return json.load(f)


def generate_synthetic_data(profiles, n_samples_per_crop=500):
    """
    Generate synthetic training data based on crop profiles.
    For each crop, generate samples with appropriate soil, season, weather conditions.
    """
    data = []
    
    for crop_name, profile in profiles.items():
        # Get profile parameters
        suitable_soils = profile['soil_suitability']
        suitable_seasons = profile['season']
        min_temp = profile['min_temp']
        max_temp = profile['max_temp']
        ph_min = profile['ph_min']
        ph_max = profile['ph_max']
        
        n_positive = int(n_samples_per_crop * 0.7)  # 70% positive samples
        n_negative = n_samples_per_crop - n_positive
        
        # Generate POSITIVE samples (ideal conditions)
        for _ in range(n_positive):
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
                'suitable': 1
            })
        
        # Generate NEGATIVE samples (unsuitable conditions)
        for _ in range(n_negative):
            # Pick unsuitable soil/season
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
                'suitable': 0
            })
    
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
    
    logger.info("Training RandomForest classifier...")
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
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
        'crops': list(encoders[2].classes_)
    }
    
    joblib.dump(model_data, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")
    
    # Save accuracy report
    report_path = MODEL_PATH.replace('.joblib', '_report.json')
    with open(report_path, 'w') as f:
        json.dump({
            'accuracy': accuracy,
            'model_type': 'RandomForestClassifier',
            'n_estimators': 100,
            'features': feature_cols,
            'n_crops': len(encoders[2].classes_),
            'crops': list(encoders[2].classes_)
        }, f, indent=2)
    
    return model_data


def main():
    print("=" * 60)
    print("🌾 ML Crop Recommender Training")
    print("=" * 60)
    
    # Load profiles
    profiles = load_profiles()
    logger.info(f"Loaded {len(profiles)} crop profiles")
    
    # Generate data
    logger.info("Generating synthetic training data...")
    df = generate_synthetic_data(profiles, n_samples_per_crop=1000)
    logger.info(f"Generated {len(df)} training samples")
    
    # Preprocess
    logger.info("Preprocessing data...")
    X, y, soil_enc, season_enc, crop_enc, scaler, feature_cols = preprocess_data(df)
    
    # Train
    model, accuracy = train_model(X, y)
    
    # Save
    save_model(model, scaler, (soil_enc, season_enc, crop_enc), accuracy, feature_cols)
    
    print("\n" + "=" * 60)
    print(f"✅ Training Complete! Accuracy: {accuracy:.2%}")
    print("=" * 60)
    
    return accuracy


if __name__ == "__main__":
    main()
