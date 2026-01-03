"""
Crop FAQ Service
Provides intelligent search and retrieval of crop-specific FAQs
for farmer troubleshooting.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Load FAQ data
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
FAQ_PATH = os.path.join(DATA_DIR, 'crop_faqs_complete.json')


class CropFAQService:
    """
    Intelligent FAQ service for crop-specific troubleshooting.
    Features:
    - Keyword-based search with fuzzy matching
    - Category filtering (pest, disease, fertilizer, growth, weather, harvest)
    - Stage-relevant FAQ suggestions
    - Bilingual support (English/Telugu)
    """
    
    def __init__(self):
        self.faq_data = self._load_faqs()
        self.keywords_cache = {}
        self._build_keywords_index()
        logger.info(f"CropFAQService initialized with {self._count_faqs()} FAQs")
    
    def _load_faqs(self) -> Dict:
        """Load FAQ database"""
        try:
            with open(FAQ_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load FAQs: {e}")
            return {'crops': {}, 'general_faqs': []}
    
    def _count_faqs(self) -> int:
        """Count total FAQs in database"""
        count = len(self.faq_data.get('general_faqs', []))
        for crop_data in self.faq_data.get('crops', {}).values():
            count += len(crop_data.get('faqs', []))
        return count
    
    def _build_keywords_index(self):
        """Build keyword index for faster searching"""
        # Common symptom keywords mapped to FAQ IDs
        self.symptom_keywords = {
            # Leaf symptoms
            'yellow': ['dis', 'fert', 'nutrient'],
            'yellowing': ['dis', 'fert', 'nutrient'],
            'brown': ['dis', 'pest'],
            'spots': ['dis', 'pest'],
            'curling': ['pest', 'dis', 'virus'],
            'curled': ['pest', 'dis', 'virus'],
            'wilting': ['dis', 'water'],
            'wilt': ['dis', 'water'],
            'holes': ['pest'],
            'white': ['pest', 'dis'],
            'black': ['dis', 'pest'],
            'drying': ['pest', 'dis', 'water'],
            'pale': ['fert', 'nutrient'],
            
            # Growth symptoms
            'stunted': ['fert', 'growth'],
            'not growing': ['fert', 'growth'],
            'slow': ['fert', 'growth'],
            'tall': ['fert', 'growth'],
            'no flowers': ['fert', 'growth'],
            'dropping': ['fert', 'weather'],
            'falling': ['weather', 'pest'],
            
            # Pest-related
            'insects': ['pest'],
            'caterpillar': ['pest'],
            'worm': ['pest'],
            'borer': ['pest'],
            'aphid': ['pest'],
            'mite': ['pest'],
            'hopper': ['pest'],
            'bug': ['pest'],
            
            # Weather-related
            'rain': ['weather'],
            'heat': ['weather'],
            'cold': ['weather'],
            'waterlog': ['weather'],
            'flood': ['weather'],
            'drought': ['weather'],
            
            # Fertilizer-related
            'urea': ['fert', 'fertilizer'],
            'fertilizer': ['fert', 'fertilizer'],
            'npk': ['fert', 'fertilizer'],
            'nutrient': ['fert', 'fertilizer'],
            'deficiency': ['fert', 'fertilizer'],
            
            # Telugu keywords
            'పసుపు': ['dis', 'fert'],  # yellow
            'మచ్చలు': ['dis', 'pest'],  # spots
            'పురుగు': ['pest'],  # pest
            'వాడి': ['dis', 'water'],  # wilting
            'ఎరువు': ['fert'],  # fertilizer
            'వర్షం': ['weather'],  # rain
        }
    
    def search_faqs(self, query: str, crop: str = None, category: str = None, 
                    limit: int = 10) -> List[Dict]:
        """
        Search FAQs using keyword matching and fuzzy search
        
        Args:
            query: Search query (symptom or question)
            crop: Optional crop filter
            category: Optional category filter (pest, disease, fertilizer, etc.)
            limit: Maximum results to return
        
        Returns:
            List of matching FAQs sorted by relevance
        """
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Get FAQs to search
        faqs_to_search = []
        
        if crop and crop in self.faq_data.get('crops', {}):
            # Search specific crop
            faqs_to_search = self.faq_data['crops'][crop].get('faqs', [])
        else:
            # Search all crops
            for crop_name, crop_data in self.faq_data.get('crops', {}).items():
                for faq in crop_data.get('faqs', []):
                    faq_copy = faq.copy()
                    faq_copy['crop'] = crop_name
                    faqs_to_search.append(faq_copy)
        
        # Add general FAQs
        for faq in self.faq_data.get('general_faqs', []):
            faq_copy = faq.copy()
            faq_copy['crop'] = 'General'
            faqs_to_search.append(faq_copy)
        
        # Filter by category if specified
        if category:
            faqs_to_search = [f for f in faqs_to_search if f.get('category') == category]
        
        # Score each FAQ
        for faq in faqs_to_search:
            score = self._calculate_relevance_score(query_lower, faq)
            if score > 0.2:  # Minimum relevance threshold
                results.append({
                    **faq,
                    'relevance_score': round(score, 2)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:limit]
    
    def _calculate_relevance_score(self, query: str, faq: Dict) -> float:
        """Calculate relevance score for a FAQ based on query"""
        score = 0.0
        
        # Check question text similarity
        question_en = faq.get('question_en', '').lower()
        question_te = faq.get('question_te', '').lower()
        
        # Direct substring match
        if query in question_en or query in question_te:
            score += 0.5
        
        # Fuzzy matching on question
        en_ratio = SequenceMatcher(None, query, question_en).ratio()
        te_ratio = SequenceMatcher(None, query, question_te).ratio()
        score += max(en_ratio, te_ratio) * 0.3
        
        # Keyword matching
        for keyword, categories in self.symptom_keywords.items():
            if keyword in query:
                if faq.get('category') in categories:
                    score += 0.2
                if keyword in question_en or keyword in question_te:
                    score += 0.1
        
        # Answer relevance boost
        answer = faq.get('answer_en', '').lower()
        if any(word in answer for word in query.split()):
            score += 0.1
        
        return min(1.0, score)
    
    def get_faqs_by_category(self, crop: str, category: str) -> List[Dict]:
        """Get all FAQs in a specific category for a crop"""
        crop_data = self.faq_data.get('crops', {}).get(crop, {})
        faqs = crop_data.get('faqs', [])
        
        filtered = [f for f in faqs if f.get('category') == category]
        
        # Add general FAQs of same category
        for faq in self.faq_data.get('general_faqs', []):
            if faq.get('category') == category:
                faq_copy = faq.copy()
                faq_copy['crop'] = 'General'
                filtered.append(faq_copy)
        
        return filtered
    
    def get_faqs_by_stage(self, crop: str, stage: str) -> List[Dict]:
        """Get FAQs relevant to a specific growth stage"""
        crop_data = self.faq_data.get('crops', {}).get(crop, {})
        faqs = crop_data.get('faqs', [])
        
        relevant = []
        for faq in faqs:
            stages = faq.get('stage', [])
            if not stages or stage in stages or 'all' in stages:
                relevant.append(faq)
        
        return relevant
    
    def get_urgent_faqs(self, crop: str, weather_conditions: Dict = None) -> List[Dict]:
        """Get urgent FAQs based on current conditions"""
        crop_data = self.faq_data.get('crops', {}).get(crop, {})
        faqs = crop_data.get('faqs', [])
        
        urgent = [f for f in faqs if f.get('urgency') == 'high']
        
        # If weather conditions provided, add relevant weather FAQs
        if weather_conditions:
            if weather_conditions.get('rainfall_mm', 0) > 20:
                weather_faqs = self.search_faqs('heavy rain', crop, 'weather')
                urgent.extend(weather_faqs)
            
            if weather_conditions.get('temp_max', 30) > 38:
                heat_faqs = self.search_faqs('heat', crop, 'weather')
                urgent.extend(heat_faqs)
        
        # Remove duplicates
        seen_ids = set()
        unique = []
        for faq in urgent:
            if faq.get('id') not in seen_ids:
                seen_ids.add(faq.get('id'))
                unique.append(faq)
        
        return unique
    
    def get_all_categories(self) -> List[Dict]:
        """Get all FAQ categories with counts"""
        categories = {
            'pest': {'name_en': 'Pest Issues', 'name_te': 'తెగుళ్ళ సమస్యలు', 'icon': '🐛', 'count': 0},
            'disease': {'name_en': 'Disease Symptoms', 'name_te': 'వ్యాధి లక్షణాలు', 'icon': '🦠', 'count': 0},
            'fertilizer': {'name_en': 'Fertilizer & Nutrients', 'name_te': 'ఎరువులు & పోషకాలు', 'icon': '🧪', 'count': 0},
            'growth': {'name_en': 'Growth Problems', 'name_te': 'పెరుగుదల సమస్యలు', 'icon': '🌱', 'count': 0},
            'weather': {'name_en': 'Weather Issues', 'name_te': 'వాతావరణ సమస్యలు', 'icon': '🌧️', 'count': 0},
            'harvest': {'name_en': 'Harvest & Storage', 'name_te': 'కోత & నిల్వ', 'icon': '🌾', 'count': 0}
        }
        
        # Count FAQs per category
        for crop_data in self.faq_data.get('crops', {}).values():
            for faq in crop_data.get('faqs', []):
                cat = faq.get('category')
                if cat in categories:
                    categories[cat]['count'] += 1
        
        return [{'id': k, **v} for k, v in categories.items()]
    
    def get_crop_list(self) -> List[Dict]:
        """Get list of crops with FAQ counts"""
        crops = []
        for crop_name, crop_data in self.faq_data.get('crops', {}).items():
            crops.append({
                'name': crop_name,
                'name_te': crop_data.get('crop_te', crop_name),
                'faq_count': len(crop_data.get('faqs', []))
            })
        return crops


# Singleton instance
_faq_service = None

def get_crop_faq_service() -> CropFAQService:
    """Get singleton instance of CropFAQService"""
    global _faq_service
    if _faq_service is None:
        _faq_service = CropFAQService()
    return _faq_service
