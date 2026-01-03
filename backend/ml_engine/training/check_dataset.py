"""
Quick helper script to check soil image dataset status
and prepare for training.
"""

import os
import sys

# Expected soil classes
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

DATA_DIR = './data/soil_images'

def check_dataset():
    """Check the current state of the soil image dataset."""
    
    if not os.path.exists(DATA_DIR):
        print(f"❌ Dataset directory not found: {DATA_DIR}")
        print("\n📁 Creating directory structure...")
        os.makedirs(DATA_DIR, exist_ok=True)
        for soil_class in SOIL_CLASSES:
            os.makedirs(os.path.join(DATA_DIR, soil_class), exist_ok=True)
        print("✅ Created directories for all 8 soil classes")
        print(f"\n📝 Next: Add images to {DATA_DIR}/<class_name>/")
        return False
    
    print("📊 Soil Image Dataset Status\n")
    print("=" * 60)
    
    total_images = 0
    ready_for_training = True
    min_images_per_class = 50
    
    for soil_class in SOIL_CLASSES:
        class_dir = os.path.join(DATA_DIR, soil_class)
        
        if not os.path.exists(class_dir):
            os.makedirs(class_dir, exist_ok=True)
            count = 0
        else:
            files = [f for f in os.listdir(class_dir) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            count = len(files)
        
        total_images += count
        
        # Status indicator
        if count >= 200:
            status = "✅ EXCELLENT"
        elif count >= min_images_per_class:
            status = "✓  Ready"
        else:
            status = f"❌ Need {min_images_per_class - count} more"
            ready_for_training = False
        
        print(f"{soil_class:20} {count:4} images   {status}")
    
    print("=" * 60)
    print(f"Total: {total_images} images across {len(SOIL_CLASSES)} classes")
    
    if ready_for_training:
        print("\n🎉 Dataset ready for training!")
        print("Run: python train_soil_classifier.py")
    else:
        print(f"\n⚠️  Add more images (minimum {min_images_per_class} per class)")
        print("💡 TIP: Run generate_synthetic_dataset.py to augment existing images")
    
    return ready_for_training

def create_sample_structure():
    """Create example dataset structure with instructions."""
    
    readme_content = """# Soil Image Dataset

## How to Add Images

1. Download soil images for each class from:
   - Kaggle datasets (search "soil classification")
   - Google Images (with proper licensing)
   - Your own field photos

2. Organize images into class folders:
   - Each image should be a clear photo of the soil type
   - Supported formats: JPG, PNG
   - Minimum 50 images per class (200+ recommended)

3. Run the checker:
   ```
   python check_dataset.py
   ```

4. When ready, train the model:
   ```
   python train_soil_classifier.py
   ```

## Soil Classes

- alluvial: River-deposited soil, fertile
- black_cotton: Black regur soil, common in Deccan
- clay: Heavy clay soil, good water retention
- laterite: Reddish laterite, iron-rich
- loamy: Balanced texture, ideal for crops
- red_sandy_loam: Common in AP/Telangana
- saline: Salt-affected soil
- sandy: Light sandy soil, poor retention

## Image Quality Tips

✅ Clear, well-lit photos
✅ Focus on soil texture and color
✅ Include dry and moist samples
✅ Use natural outdoor lighting
✅ Capture from 6-12 inches above soil

❌ Avoid blurry images
❌ Don't include too much plant debris
❌ Avoid extreme shadows
❌ Don't use heavily filtered photos
"""
    
    readme_path = os.path.join(DATA_DIR, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created: {readme_path}")

if __name__ == "__main__":
    print("🌾 KisanMitra Soil Classifier Dataset Checker\n")
    
    is_ready = check_dataset()
    
    # Create README if it doesn't exist
    readme_path = os.path.join(DATA_DIR, 'README.md')
    if os.path.exists(DATA_DIR) and not os.path.exists(readme_path):
        create_sample_structure()
    
    print("\n" + "=" * 60)
    
    if is_ready:
        print("\n🚀 Ready to train! Run:")
        print("   python train_soil_classifier.py\n")
    else:
        print("\n📝 Next steps:")
        print(f"1. Add images to {DATA_DIR}/<class_name>/")
        print("2. Run this script again to check progress")
        print("3. When ready, run: python train_soil_classifier.py\n")
