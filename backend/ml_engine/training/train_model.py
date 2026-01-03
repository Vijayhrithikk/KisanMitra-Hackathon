import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "data_core.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

def train():
    logger.info("Starting training pipeline...")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        logger.error(f"Data file not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    logger.info(f"Loaded {len(df)} records.")

    # 2. Preprocessing
    # Rename columns to standard format if needed (based on inspection)
    # Expected: Temparature,Humidity,Moisture,Soil Type,Crop Type,Nitrogen,Potassium,Phosphorous
    
    # Features (X) and Target (y)
    # We want to predict 'Crop Type' based on Soil & Weather metrics
    
    # Encoding 'Soil Type'
    le_soil = LabelEncoder()
    df['Soil_Code'] = le_soil.fit_transform(df['Soil Type'])
    
    # Encoding Target 'Crop Type'
    le_crop = LabelEncoder()
    df['Crop_Code'] = le_crop.fit_transform(df['Crop Type'])
    
    feature_cols = ['Temparature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous', 'Soil_Code']
    X = df[feature_cols]
    y = df['Crop_Code']
    
    logger.info(f"Features: {feature_cols}")
    logger.info(f"Target Classes: {le_crop.classes_}")

    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train Model
    logger.info("Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Model Accuracy: {acc:.4f}")
    logger.info("\n" + classification_report(y_test, y_pred, target_names=le_crop.classes_))
    
    # 6. Save Artifacts
    artifacts = {
        "model": rf,
        "le_soil": le_soil,
        "le_crop": le_crop,
        "feature_names": feature_cols
    }
    
    model_path = os.path.join(MODEL_DIR, "crop_recommender.pkl")
    joblib.dump(artifacts, model_path)
    logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
