"""
Soil Image Classification Model Training Script
Uses MobileNetV2 transfer learning for 8 Indian soil types.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Soil Classes
SOIL_CLASSES = [
    'alluvial',
    'black_cotton',
    'clay',
    'laterite',
    'loamy',
    'red_sandy_loam',
    'saline',
    'sandy'
]

SOIL_CLASS_INFO = {
    'alluvial': {
        'en': 'Alluvial',
        'te': 'ఒండ్ర మట్టి',
        'params': {'ph': 7.2, 'n': 240, 'p': 65, 'k': 280}
    },
    'black_cotton': {
        'en': 'Black Cotton',
        'te': 'నల్ల పత్తి మట్టి',
        'params': {'ph': 8.0, 'n': 200, 'p': 55, 'k': 320}
    },
    'clay': {
        'en': 'Clay',
        'te': 'బంక మట్టి',
        'params': {'ph': 7.5, 'n': 160, 'p': 50, 'k': 250}
    },
    'laterite': {
        'en': 'Laterite',
        'te': 'జల్లి మట్టి',
        'params': {'ph': 5.5, 'n': 120, 'p': 35, 'k': 150}
    },
    'loamy': {
        'en': 'Loamy',
        'te': 'లోమీ మట్టి',
        'params': {'ph': 6.8, 'n': 200, 'p': 60, 'k': 220}
    },
    'red_sandy_loam': {
        'en': 'Red Sandy Loam',
        'te': 'ఎర్ర ఇసుక మట్టి',
        'params': {'ph': 6.5, 'n': 180, 'p': 45, 'k': 200}
    },
    'saline': {
        'en': 'Saline',
        'te': 'ఉప్పు మట్టి',
        'params': {'ph': 8.5, 'n': 100, 'p': 30, 'k': 180}
    },
    'sandy': {
        'en': 'Sandy',
        'te': 'ఇసుక మట్టి',
        'params': {'ph': 6.0, 'n': 140, 'p': 40, 'k': 180}
    }
}

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_PHASE1 = 10  # Feature extraction
EPOCHS_PHASE2 = 20  # Fine-tuning


def create_model(num_classes=8):
    """Create MobileNetV2-based classification model."""
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model initially
    base_model.trainable = False
    
    # Build classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model, base_model


def create_data_generators(data_dir):
    """Create training and validation data generators with augmentation."""
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    return train_generator, val_generator


def train_model(data_dir, output_dir):
    """Train the soil classification model in two phases."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create data generators
    logger.info("Creating data generators...")
    train_gen, val_gen = create_data_generators(data_dir)
    
    # Verify class indices match our expected classes
    logger.info(f"Class indices: {train_gen.class_indices}")
    
    # Create model
    logger.info("Creating model...")
    model, base_model = create_model(num_classes=len(train_gen.class_indices))
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True
        ),
        ModelCheckpoint(
            os.path.join(output_dir, 'soil_classifier_best.keras'),
            monitor='val_accuracy',
            save_best_only=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7
        )
    ]
    
    # ========== PHASE 1: Feature Extraction ==========
    logger.info("Phase 1: Training classification head...")
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history1 = model.fit(
        train_gen,
        epochs=EPOCHS_PHASE1,
        validation_data=val_gen,
        callbacks=callbacks
    )
    
    # ========== PHASE 2: Fine-tuning ==========
    logger.info("Phase 2: Fine-tuning base model...")
    
    # Unfreeze last 30 layers
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history2 = model.fit(
        train_gen,
        epochs=EPOCHS_PHASE2,
        validation_data=val_gen,
        callbacks=callbacks
    )
    
    # Save final model
    model.save(os.path.join(output_dir, 'soil_classifier_final.keras'))
    
    # Save class mapping
    class_mapping = {v: k for k, v in train_gen.class_indices.items()}
    with open(os.path.join(output_dir, 'class_mapping.json'), 'w', encoding='utf-8') as f:
        json.dump(class_mapping, f, indent=2)
    
    # Save soil class info
    with open(os.path.join(output_dir, 'soil_class_info.json'), 'w', encoding='utf-8') as f:
        json.dump(SOIL_CLASS_INFO, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Model and mappings saved to {output_dir}")
    
    return model, history1, history2


def evaluate_model(model, test_dir):
    """Evaluate model on test set."""
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    results = model.evaluate(test_generator)
    logger.info(f"Test Loss: {results[0]:.4f}")
    logger.info(f"Test Accuracy: {results[1]:.4f}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Soil Classification Model')
    parser.add_argument('--data_dir', type=str, default='./data/soil_images',
                        help='Directory containing soil images organized by class')
    parser.add_argument('--output_dir', type=str, default='../models/soil_classifier',
                        help='Directory to save trained model')
    
    args = parser.parse_args()
    
    if os.path.exists(args.data_dir):
        train_model(args.data_dir, args.output_dir)
    else:
        logger.error(f"Data directory not found: {args.data_dir}")
        logger.info("Please run generate_synthetic_dataset.py first or provide a valid dataset path")
