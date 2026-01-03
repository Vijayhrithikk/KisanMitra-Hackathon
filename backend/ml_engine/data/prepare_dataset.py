"""
Soil Dataset Preparation Script
Downloads and organizes soil images for training the classification model.

This script helps acquire soil images from multiple sources:
1. Kaggle datasets (requires Kaggle API)
2. RoboFlow datasets
3. Web scraping (requires verification)

Target: ~1000 images per soil type (8000 total)
"""

import os
import shutil
import json
from pathlib import Path

# Soil types we need
SOIL_TYPES = [
    'alluvial',
    'black_cotton',
    'clay',
    'laterite', 
    'loamy',
    'red_sandy_loam',
    'saline',
    'sandy'
]

def setup_directory_structure(base_dir='./data/soil_images'):
    """Create directory structure for training data."""
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    for soil_type in SOIL_TYPES:
        soil_dir = base_path / soil_type
        soil_dir.mkdir(exist_ok=True)
        print(f"Created directory: {soil_dir}")
    
    print(f"\n✅ Directory structure created at {base_path}")
    return base_path

def download_from_kaggle(dataset_name, download_path):
    """
    Download dataset from Kaggle using Kaggle API.
    
    Prerequisites:
    1. Install kaggle: pip install kaggle
    2. Setup API credentials: https://www.kaggle.com/docs/api
    3. Place kaggle.json in ~/.kaggle/
    """
    try:
        import kaggle
        print(f"Downloading {dataset_name} from Kaggle...")
        kaggle.api.dataset_download_files(
            dataset_name,
            path=download_path,
            unzip=True
        )
        print(f"✅ Downloaded to {download_path}")
        return True
    except ImportError:
        print("❌ Kaggle API not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Kaggle: {e}")
        return False

def count_images(base_dir):
    """Count images in each soil type directory."""
    base_path = Path(base_dir)
    counts = {}
    total = 0
    
    for soil_type in SOIL_TYPES:
        soil_dir = base_path / soil_type
        if soil_dir.exists():
            images = list(soil_dir.glob('*.jpg')) + list(soil_dir.glob('*.png')) + list(soil_dir.glob('*.jpeg'))
            count = len(images)
            counts[soil_type] = count
            total += count
        else:
            counts[soil_type] = 0
    
    return counts, total

def generate_report(base_dir):
    """Generate a report of current dataset status."""
    counts, total = count_images(base_dir)
    
    print("\n" + "="*60)
    print("SOIL DATASET REPORT")
    print("="*60)
    
    for soil_type in SOIL_TYPES:
        count = counts[soil_type]
        progress = (count / 1000) * 100 if count > 0 else 0
        status = "✅" if count >= 1000 else "⚠️" if count > 0 else "❌"
        print(f"{status} {soil_type:20s}: {count:4d}/1000 images ({progress:3.0f}%)")
    
    print("-"*60)
    print(f"Total Images: {total}/8000 ({(total/8000)*100:.1f}%)")
    print("="*60)
    
    # Save report
    report_path = Path(base_dir) / 'dataset_report.json'
    with open(report_path, 'w') as f:
        json.dump({
            'total_images': total,
            'target': 8000,
            'counts': counts,
            'progress_percent': (total/8000)*100
        }, f, indent=2)
    
    print(f"\n📊 Report saved to {report_path}")

def main():
    print("🌱 Soil Dataset Preparation Tool")
    print("="*60)
    
    # Setup directories
    base_dir = input("Enter base directory (default: ./data/soil_images): ").strip() or './data/soil_images'
    setup_directory_structure(base_dir)
    
    # Generate initial report
    generate_report(base_dir)
    
    print("\n📌 NEXT STEPS:")
    print("1. Download soil images and place them in respective directories")
    print("2. Recommended sources:")
    print("   - Kaggle: Search for 'soil classification' datasets")
    print("   - RoboFlow: https://universe.roboflow.com/")
    print("   - Google Dataset Search")
    print("3. Run this script again to check progress")
    print("4. Once you have ~8000 images, run the training script:")
    print("   python train_soil_classifier.py --data_dir", base_dir)

if __name__ == "__main__":
    main()
