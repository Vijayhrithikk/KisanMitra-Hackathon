"""
Soil Image Classification Service
Provides inference for soil type classification from images.
"""

import os
import json
import logging
import numpy as np
from PIL import Image
import io
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Soil class information with Telugu names and soil parameters
SOIL_CLASS_INFO = {
    'alluvial': {
        'en': 'Alluvial',
        'te': 'ఒండ్ర మట్టి',
        'params': {'ph': 7.2, 'n': 240, 'p': 65, 'k': 280},
        'description': 'River-deposited fertile soil, excellent for most crops'
    },
    'black_cotton': {
        'en': 'Black Cotton',
        'te': 'నల్ల పత్తి మట్టి',
        'params': {'ph': 8.0, 'n': 200, 'p': 55, 'k': 320},
        'description': 'High clay content, great water retention, ideal for cotton'
    },
    'clay': {
        'en': 'Clay',
        'te': 'బంక మట్టి',
        'params': {'ph': 7.5, 'n': 160, 'p': 50, 'k': 250},
        'description': 'Heavy soil, retains water and nutrients well'
    },
    'laterite': {
        'en': 'Laterite',
        'te': 'జల్లి మట్టి',
        'params': {'ph': 5.5, 'n': 120, 'p': 35, 'k': 150},
        'description': 'Iron-rich acidic soil, needs lime amendment'
    },
    'loamy': {
        'en': 'Loamy',
        'te': 'లోమీ మట్టి',
        'params': {'ph': 6.8, 'n': 200, 'p': 60, 'k': 220},
        'description': 'Balanced soil with good drainage and nutrients'
    },
    'red_sandy_loam': {
        'en': 'Red Sandy Loam',
        'te': 'ఎర్ర ఇసుక మట్టి',
        'params': {'ph': 6.5, 'n': 180, 'p': 45, 'k': 200},
        'description': 'Well-drained reddish soil, common in AP/Telangana'
    },
    'saline': {
        'en': 'Saline',
        'te': 'ఉప్పు మట్టి',
        'params': {'ph': 8.5, 'n': 100, 'p': 30, 'k': 180},
        'description': 'High salt content, needs special management'
    },
    'sandy': {
        'en': 'Sandy',
        'te': 'ఇసుక మట్టి',
        'params': {'ph': 6.0, 'n': 140, 'p': 40, 'k': 180},
        'description': 'Light soil, fast-draining, needs frequent watering'
    }
}

# Default class mapping (index to class name)
DEFAULT_CLASS_MAPPING = {
    0: 'alluvial',
    1: 'black_cotton',
    2: 'clay',
    3: 'laterite',
    4: 'loamy',
    5: 'red_sandy_loam',
    6: 'saline',
    7: 'sandy'
}


class SoilImageClassifier:
    """Soil type classification from images using trained CNN model."""
    
    def __init__(self, model_dir=None):
        """
        Initialize the classifier.
        
        Args:
            model_dir: Directory containing the trained model and mappings
        """
        self.model = None
        self.class_mapping = DEFAULT_CLASS_MAPPING
        self.model_loaded = False
        self.img_size = 224
        
        if model_dir is None:
            # Default model directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models', 'soil_classifier')
        
        self.model_dir = model_dir
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and class mappings."""
        try:
            # Try to import TensorFlow
            import tensorflow as tf
            
            model_path = os.path.join(self.model_dir, 'soil_classifier_final.keras')
            
            if os.path.exists(model_path):
                logger.info(f"Loading model from {model_path}")
                self.model = tf.keras.models.load_model(model_path)
                self.model_loaded = True
                
                # Load class mapping if available
                mapping_path = os.path.join(self.model_dir, 'class_mapping.json')
                if os.path.exists(mapping_path):
                    with open(mapping_path, 'r') as f:
                        # Convert string keys back to int
                        loaded_mapping = json.load(f)
                        self.class_mapping = {int(k): v for k, v in loaded_mapping.items()}
                
                logger.info("Model loaded successfully")
            else:
                logger.warning(f"Model not found at {model_path}. Using fallback mode.")
                self.model_loaded = False
                
        except ImportError:
            logger.warning("TensorFlow not installed. Using fallback mode.")
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model_loaded = False
    
    def preprocess_image(self, image):
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Preprocessed numpy array ready for model
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Resize to model input size
        image = image.resize((self.img_size, self.img_size))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def classify(self, image):
        """
        Classify soil type from image.
        
        Args:
            image: PIL Image, numpy array, base64 string, or file path
            
        Returns:
            dict with classification results
        """
        # Handle different input types
        if isinstance(image, str):
            if os.path.exists(image):
                # File path
                image = Image.open(image)
            elif image.startswith('data:image'):
                # Base64 data URL
                image_data = image.split(',')[1]
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            else:
                # Raw base64
                try:
                    image = Image.open(io.BytesIO(base64.b64decode(image)))
                except:
                    raise ValueError("Invalid image input")
        elif isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        
        if self.model_loaded and self.model is not None:
            return self._model_predict(image)
        else:
            return self._fallback_predict(image)
    
    def _model_predict(self, image):
        """Make prediction using trained model."""
        # Preprocess
        img_array = self.preprocess_image(image)
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)[0]
        
        # Get top 3 predictions
        top_indices = np.argsort(predictions)[::-1][:3]
        
        top_class_idx = top_indices[0]
        top_class_name = self.class_mapping.get(top_class_idx, 'unknown')
        confidence = float(predictions[top_class_idx])
        
        # Build response
        result = {
            'success': True,
            'soil_type': SOIL_CLASS_INFO.get(top_class_name, {}).get('en', top_class_name),
            'soil_type_key': top_class_name,
            'soil_type_te': SOIL_CLASS_INFO.get(top_class_name, {}).get('te', ''),
            'confidence': round(confidence, 3),
            'description': SOIL_CLASS_INFO.get(top_class_name, {}).get('description', ''),
            'soil_params': SOIL_CLASS_INFO.get(top_class_name, {}).get('params', {}),
            'top_3': []
        }
        
        for idx in top_indices:
            class_name = self.class_mapping.get(idx, 'unknown')
            result['top_3'].append({
                'type': SOIL_CLASS_INFO.get(class_name, {}).get('en', class_name),
                'type_key': class_name,
                'confidence': round(float(predictions[idx]), 3)
            })
        
        return result
    
    def _fallback_predict(self, image):
        """
        Fallback prediction based on dominant colors when model is not available.
        This is a simple heuristic for demo purposes.
        """
        # Resize for analysis
        image = image.resize((100, 100))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get average color
        pixels = np.array(image)
        avg_color = pixels.mean(axis=(0, 1))
        r, g, b = avg_color
        
        # Simple color-based heuristics
        if r < 80 and g < 70 and b < 60:
            soil_type = 'black_cotton'
            confidence = 0.75
        elif r > 170 and g > 170 and b > 160:
            soil_type = 'saline'
            confidence = 0.70
        elif r > 160 and g < 100 and b < 80:
            soil_type = 'laterite'
            confidence = 0.72
        elif r > 170 and g < 120 and b < 90:
            soil_type = 'red_sandy_loam'
            confidence = 0.73
        elif r > 190 and g > 170 and b > 130:
            soil_type = 'sandy'
            confidence = 0.71
        elif r > 150 and g > 130 and b > 100:
            soil_type = 'alluvial'
            confidence = 0.68
        elif abs(r - g) < 30 and abs(g - b) < 30:
            soil_type = 'clay'
            confidence = 0.65
        else:
            soil_type = 'loamy'
            confidence = 0.60
        
        result = {
            'success': True,
            'soil_type': SOIL_CLASS_INFO.get(soil_type, {}).get('en', soil_type),
            'soil_type_key': soil_type,
            'soil_type_te': SOIL_CLASS_INFO.get(soil_type, {}).get('te', ''),
            'confidence': confidence,
            'description': SOIL_CLASS_INFO.get(soil_type, {}).get('description', ''),
            'soil_params': SOIL_CLASS_INFO.get(soil_type, {}).get('params', {}),
            'top_3': [
                {
                    'type': SOIL_CLASS_INFO.get(soil_type, {}).get('en', soil_type),
                    'type_key': soil_type,
                    'confidence': confidence
                }
            ],
            'fallback_mode': True,
            'note': 'Using color-based heuristics. Train the model for accurate predictions.'
        }
        
        return result


# Singleton instance
_classifier_instance = None


def get_classifier():
    """Get or create the global classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SoilImageClassifier()
    return _classifier_instance
