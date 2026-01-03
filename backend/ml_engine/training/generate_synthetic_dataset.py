"""
Synthetic Soil Image Dataset Generator
Generates training data using color gradients and noise patterns for each soil type.
For production, use real soil image datasets from Kaggle or agricultural databases.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Soil type color profiles (RGB ranges)
SOIL_COLOR_PROFILES = {
    'alluvial': {
        'base_colors': [(180, 160, 130), (160, 140, 110), (170, 150, 120)],
        'variation': 25,
        'texture': 'smooth'
    },
    'black_cotton': {
        'base_colors': [(60, 50, 45), (70, 60, 55), (55, 45, 40)],
        'variation': 15,
        'texture': 'cracked'
    },
    'clay': {
        'base_colors': [(160, 130, 100), (150, 120, 90), (170, 140, 110)],
        'variation': 20,
        'texture': 'smooth'
    },
    'laterite': {
        'base_colors': [(180, 80, 50), (160, 70, 45), (190, 90, 55)],
        'variation': 25,
        'texture': 'rocky'
    },
    'loamy': {
        'base_colors': [(120, 90, 70), (130, 100, 80), (110, 85, 65)],
        'variation': 20,
        'texture': 'granular'
    },
    'red_sandy_loam': {
        'base_colors': [(180, 100, 70), (170, 90, 60), (190, 110, 80)],
        'variation': 25,
        'texture': 'sandy'
    },
    'saline': {
        'base_colors': [(200, 195, 185), (190, 185, 175), (210, 205, 195)],
        'variation': 15,
        'texture': 'crusty'
    },
    'sandy': {
        'base_colors': [(210, 190, 150), (200, 180, 140), (220, 200, 160)],
        'variation': 30,
        'texture': 'granular'
    }
}


def add_noise(img_array, intensity=0.1):
    """Add random noise to simulate natural variation."""
    noise = np.random.normal(0, intensity * 255, img_array.shape)
    noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return noisy


def add_texture_pattern(draw, width, height, texture_type, base_color):
    """Add texture patterns based on soil type."""
    
    if texture_type == 'cracked':
        # Draw crack lines for black cotton soil
        for _ in range(random.randint(3, 8)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-100, 100)
            crack_color = tuple(max(0, c - 30) for c in base_color)
            draw.line([(x1, y1), (x2, y2)], fill=crack_color, width=random.randint(1, 3))
    
    elif texture_type == 'granular':
        # Draw small particles for loamy/sandy soil
        for _ in range(random.randint(50, 150)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(1, 4)
            variation = random.randint(-20, 20)
            particle_color = tuple(min(255, max(0, c + variation)) for c in base_color)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=particle_color)
    
    elif texture_type == 'rocky':
        # Draw irregular shapes for laterite soil
        for _ in range(random.randint(10, 25)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(5, 20)
            points = []
            for i in range(5):
                angle = i * 72 + random.randint(-20, 20)
                px = x + int(size * np.cos(np.radians(angle)))
                py = y + int(size * np.sin(np.radians(angle)))
                points.append((px, py))
            variation = random.randint(-30, 30)
            rock_color = tuple(min(255, max(0, c + variation)) for c in base_color)
            draw.polygon(points, fill=rock_color)
    
    elif texture_type == 'crusty':
        # Draw salt crystal patterns for saline soil
        for _ in range(random.randint(20, 50)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(2, 8)
            white_var = random.randint(230, 255)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(white_var, white_var, white_var - 10))
    
    elif texture_type == 'sandy':
        # Fine grain pattern for sandy soils
        for _ in range(random.randint(100, 200)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(1, 2)
            variation = random.randint(-15, 25)
            grain_color = tuple(min(255, max(0, c + variation)) for c in base_color)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=grain_color)


def generate_soil_image(soil_type, size=224):
    """Generate a synthetic soil image for a given type."""
    
    profile = SOIL_COLOR_PROFILES.get(soil_type)
    if not profile:
        raise ValueError(f"Unknown soil type: {soil_type}")
    
    # Select random base color
    base_color = random.choice(profile['base_colors'])
    variation = profile['variation']
    
    # Create base image with gradient
    img = Image.new('RGB', (size, size))
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Create gradient with some randomness
    for y in range(size):
        for x in range(size):
            # Add spatial variation
            var_x = int((x / size - 0.5) * variation)
            var_y = int((y / size - 0.5) * variation)
            noise = random.randint(-variation//2, variation//2)
            
            r = min(255, max(0, base_color[0] + var_x + noise))
            g = min(255, max(0, base_color[1] + var_y + noise))
            b = min(255, max(0, base_color[2] + noise))
            
            pixels[y, x] = [r, g, b]
    
    # Add noise
    pixels = add_noise(pixels, intensity=0.05)
    
    img = Image.fromarray(pixels)
    
    # Add texture patterns
    draw = ImageDraw.Draw(img)
    add_texture_pattern(draw, size, size, profile['texture'], base_color)
    
    # Apply slight blur for realism
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Random brightness/contrast adjustment
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))
    
    return img


def generate_dataset(output_dir, images_per_class=500):
    """Generate complete synthetic dataset."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    for soil_type in SOIL_COLOR_PROFILES.keys():
        class_dir = os.path.join(output_dir, soil_type)
        os.makedirs(class_dir, exist_ok=True)
        
        logger.info(f"Generating {images_per_class} images for {soil_type}...")
        
        for i in range(images_per_class):
            img = generate_soil_image(soil_type)
            img.save(os.path.join(class_dir, f"{soil_type}_{i:04d}.jpg"), quality=90)
            
            if (i + 1) % 100 == 0:
                logger.info(f"  Generated {i + 1}/{images_per_class}")
    
    logger.info(f"Dataset generated in {output_dir}")
    logger.info(f"Total images: {len(SOIL_COLOR_PROFILES) * images_per_class}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Synthetic Soil Dataset')
    parser.add_argument('--output_dir', type=str, default='./data/soil_images',
                        help='Output directory for generated images')
    parser.add_argument('--images_per_class', type=int, default=500,
                        help='Number of images per soil class')
    
    args = parser.parse_args()
    
    generate_dataset(args.output_dir, args.images_per_class)
