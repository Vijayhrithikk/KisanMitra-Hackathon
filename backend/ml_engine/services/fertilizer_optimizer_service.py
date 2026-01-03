"""
Fertilizer Usage Optimizer Service
Analyzes soil NPK data and provides sustainable, crop-specific fertilizer recommendations
"""

import json
import os
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Paths
FERTILIZER_DB_PATH = os.path.join(os.path.dirname(__file__), '../data/fertilizer_database.json')
CROP_NPK_PATH = os.path.join(os.path.dirname(__file__), '../data/crop_npk_requirements.json')


class FertilizerOptimizerService:
    def __init__(self):
        self.fertilizer_db = self._load_json(FERTILIZER_DB_PATH)
        self.crop_npk = self._load_json(CROP_NPK_PATH)
    
    def _load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}
    
    def get_crop_requirements(self, crop_name: str, unit='acre') -> Optional[Dict]:
        """
        Get NPK requirements for a crop.
        
        Args:
            crop_name: Crop name (e.g., 'rice', 'wheat', 'Bengal Gram')
            unit: 'acre' or 'hectare'
        
        Returns:
            Dict with n, p, k values or None if crop not found
        """
        # Convert to lowercase for case-insensitive matching
        crop_key = crop_name.lower().strip()
        crop_data = self.crop_npk.get('crops', {}).get(crop_key)
        
        if not crop_data:
            logger.warning(f"Crop {crop_name} (as '{crop_key}') not found in NPK database")
            return None
        
        npk_key = f'npk_per_{unit}'
        if npk_key in crop_data:
            return crop_data[npk_key]
        else:
            # Default to acre if hectare not available
            return crop_data.get('npk_per_acre')
    
    def calculate_npk_deficit(self, current_npk: Dict, required_npk: Dict) -> Dict:
        """
        Calculate NPK deficit.
        Positive = need to add, Negative = excess
        
        Args:
            current_npk: {'n': 180, 'p': 35, 'k': 220}
            required_npk: {'n': 120, 'p': 60, 'k': 40}
        
        Returns:
            {'n': -60, 'p': 25, 'k': -180} (negative means excess)
        """
        deficit = {}
        for nutrient in ['n', 'p', 'k']:
            required = required_npk.get(nutrient, 0)
            current = current_npk.get(nutrient, 0)
            deficit[nutrient] = required - current
        
        return deficit
    
    def recommend_fertilizers(
        self, 
        deficit: Dict, 
        soil_type: str = 'Loamy',
        farming_type: str = 'balanced'  # 'organic', 'balanced', 'conventional'
    ) -> List[Dict]:
        """
        Recommend fertilizers to meet NPK deficit.
        
        Args:
            deficit: {'n': 120, 'p': 60, 'k': 40}
            soil_type: Soil type for adjustments
            farming_type: Farming preference
        
        Returns:
            List of fertilizer recommendations with quantities
        """
        recommendations = []
        products = self.fertilizer_db.get('products', {})
        
        # Adjust for soil type
        deficit = self._adjust_for_soil_type(deficit, soil_type)
        
        # Nitrogen handling
        n_need = max(0, deficit.get('n', 0))
        if n_need > 0:
            if farming_type == 'organic':
                # Use organic sources
                fym = products.get('fym', {})
                fym_qty = n_need / (fym['composition']['n'] / 100) if fym else 0
                recommendations.append({
                    'product': fym.get('name', 'FYM'),
                    'quantity_kg_per_acre': round(fym_qty),
                    'application_time': 'Basal (2 weeks before sowing)',
                    'cost_estimate': round(fym_qty * fym.get('price_per_kg', 2)),
                    'npk_contribution': {
                        'n': round(fym_qty * fym['composition']['n'] / 100, 1),
                        'p': round(fym_qty * fym['composition']['p'] / 100, 1),
                        'k': round(fym_qty * fym['composition']['k'] / 100, 1)
                    },
                    'type': 'organic'
                })
                # Adjust deficit after FYM
                n_need -= fym_qty * fym['composition']['n'] / 100
                deficit['p'] -= fym_qty * fym['composition']['p'] / 100
                deficit['k'] -= fym_qty * fym['composition']['k'] / 100
            
            if n_need > 0:  # Still need nitrogen
                urea = products.get('urea', {})
                urea_qty = n_need / (urea['composition']['n'] / 100) if urea else 0
                recommendations.append({
                    'product': urea.get('name', 'Urea'),
                    'quantity_kg_per_acre': round(urea_qty),
                    'application_time': 'Split application (see schedule)',
                    'cost_estimate': round(urea_qty * urea.get('price_per_kg', 6.5)),
                    'npk_contribution': {
                        'n': round(urea_qty * urea['composition']['n'] / 100, 1),
                        'p': 0,
                        'k': 0
                    },
                    'type': 'synthetic'
                })
        
        # Phosphorus handling
        p_need = max(0, deficit.get('p', 0))
        if p_need > 0:
            dap = products.get('dap', {})
            dap_qty = p_need / (dap['composition']['p'] / 100) if dap else 0
            recommendations.append({
                'product': dap.get('name', 'DAP'),
                'quantity_kg_per_acre': round(dap_qty),
                'application_time': 'Basal (at sowing)',
                'cost_estimate': round(dap_qty * dap.get('price_per_kg', 27)),
                'npk_contribution': {
                    'n': round(dap_qty * dap['composition']['n'] / 100, 1),
                    'p': round(dap_qty * dap['composition']['p'] / 100, 1),
                    'k': 0
                },
                'type': 'synthetic'
            })
            # DAP also provides nitrogen
            deficit['n'] -= dap_qty * dap['composition']['n'] / 100
        
        # Potassium handling
        k_need = max(0, deficit.get('k', 0))
        if k_need > 0:
            mop = products.get('mop', {})
            mop_qty = k_need / (mop['composition']['k'] / 100) if mop else 0
            recommendations.append({
                'product': mop.get('name', 'MOP'),
                'quantity_kg_per_acre': round(mop_qty),
                'application_time': 'Split: 50% basal, 50% mid-season',
                'cost_estimate': round(mop_qty * mop.get('price_per_kg', 12)),
                'npk_contribution': {
                    'n': 0,
                    'p': 0,
                    'k': round(mop_qty * mop['composition']['k'] / 100, 1)
                },
                'type': 'synthetic'
            })
        
        return recommendations
    
    def _adjust_for_soil_type(self, deficit: Dict, soil_type: str) -> Dict:
        """Adjust NPK requirements based on soil type"""
        adjustments = self.fertilizer_db.get('application_guidelines', {}).get('soil_type_adjustments', {})
        soil_adj = adjustments.get(soil_type, {})
        
        adjusted = deficit.copy()
        
        # Apply percentage adjustments
        if 'n_increase_percent' in soil_adj:
            adjusted['n'] *= (1 + soil_adj['n_increase_percent'] / 100)
        if 'n_decrease_percent' in soil_adj:
            adjusted['n'] *= (1 - soil_adj['n_decrease_percent'] / 100)
        
        if 'p_increase_percent' in soil_adj:
            adjusted['p'] *= (1 + soil_adj['p_increase_percent'] / 100)
        if 'p_decrease_percent' in soil_adj:
            adjusted['p'] *= (1 - soil_adj['p_decrease_percent'] / 100)
        
        if 'k_increase_percent' in soil_adj:
            adjusted['k'] *= (1 + soil_adj['k_increase_percent'] / 100)
        if 'k_decrease_percent' in soil_adj:
            adjusted['k'] *= (1 - soil_adj['k_decrease_percent'] / 100)
        
        return adjusted
    
    def generate_application_schedule(
        self, 
        crop_name: str, 
        fertilizers: List[Dict]
    ) -> List[Dict]:
        """
        Generate split application schedule based on crop growth stages.
        
        Args:
            crop_name: Name of crop
            fertilizers: List of recommended fertilizers
        
        Returns:
            List of scheduled applications with day and activity
        """
        schedule = []
        split_guide = self.fertilizer_db.get('application_guidelines', {}).get('split_application', {})
        crop_schedule = split_guide.get(crop_name.lower(), split_guide.get('default', []))
        
        if not crop_schedule:
            return schedule
        
        # Find nitrogen and potassium fertilizers
        n_fertilizer = None
        p_fertilizer = None
        k_fertilizer = None
        
        for fert in fertilizers:
            npk = fert.get('npk_contribution', {})
            if npk.get('n', 0) > 0 and fert.get('product', '').upper() in ['UREA', 'FYM', 'VERMICOMPOST']:
                n_fertilizer = fert
            if npk.get('p', 0) > 0:
                p_fertilizer = fert
            if npk.get('k', 0) > 0:
                k_fertilizer = fert
        
        # Generate schedule based on crop stages
        for stage in crop_schedule:
            day = int(stage.get('stage', '0 days').split('(')[1].split(' ')[0]) if '(' in stage.get('stage', '') else 0
            
            applications = []
            cost = 0
            
            # Phosphorus - usually 100% at basal
            if stage.get('p_percent', 0) > 0 and p_fertilizer:
                qty = p_fertilizer['quantity_kg_per_acre'] * stage['p_percent'] / 100
                applications.append(f"{p_fertilizer['product']} {round(qty)}kg")
                cost += p_fertilizer['cost_estimate'] * stage['p_percent'] / 100
            
            # Nitrogen - split application
            if stage.get('n_percent', 0) > 0 and n_fertilizer:
                qty = n_fertilizer['quantity_kg_per_acre'] * stage['n_percent'] / 100
                applications.append(f"{n_fertilizer['product']} {round(qty)}kg")
                cost += n_fertilizer['cost_estimate'] * stage['n_percent'] / 100
            
            # Potassium - split application
            if stage.get('k_percent', 0) > 0 and k_fertilizer:
                qty = k_fertilizer['quantity_kg_per_acre'] * stage['k_percent'] / 100
                applications.append(f"{k_fertilizer['product']} {round(qty)}kg")
                cost += k_fertilizer['cost_estimate'] * stage['k_percent'] / 100
            
            if applications:
                schedule.append({
                    'day': day,
                    'stage': stage.get('stage', 'Application'),
                    'activity': 'Apply ' + ' + '.join(applications),
                    'cost': round(cost)
                })
        
        return schedule
    
    def calculate_cost_benefit(
        self, 
        fertilizers: List[Dict], 
        crop_name: str,
        current_yield_tons_per_acre: float = None
    ) -> Dict:
        """
        Calculate cost-benefit analysis.
        
        Returns:
            Dict with total_cost, expected_yield_increase, roi, sustainability_score
        """
        total_cost = sum(f.get('cost_estimate', 0) for f in fertilizers)
        
        # Get crop data (case-insensitive)
        crop_data = self.crop_npk.get('crops', {}).get(crop_name.lower(), {})
        target_yield = crop_data.get('target_yield_tons_per_acre', 2.0)
        
        # Estimate yield improvement (10-20% with optimal fertilization)
        if current_yield_tons_per_acre:
            potential_increase = min(target_yield - current_yield_tons_per_acre, target_yield * 0.20)
            expected_yield_increase_percent = (potential_increase / current_yield_tons_per_acre) * 100
        else:
            expected_yield_increase_percent = 15  # Default estimate
        
        # Calculate sustainability score (0-10)
        sustainability_score = 10.0
        organic_count = sum(1 for f in fertilizers if f.get('type') == 'organic')
        synthetic_count = len(fertilizers) - organic_count
        
        # Deduct points for heavy synthetic use
        if synthetic_count > 2:
            sustainability_score -= 2
        if organic_count == 0:
            sustainability_score -= 1
        
        # Check total NPK - penalize over-application
        total_npk = sum(
            f.get('npk_contribution', {}).get('n', 0) + 
            f.get('npk_contribution', {}).get('p', 0) + 
            f.get('npk_contribution', {}).get('k', 0) 
            for f in fertilizers
        )
        
        crop_req = self.get_crop_requirements(crop_name) or {'n': 100, 'p': 50, 'k': 50}
        required_total = crop_req['n'] + crop_req['p'] + crop_req['k']
        
        if total_npk > required_total * 1.2:  # More than 20% excess
            sustainability_score -= 2
        
        sustainability_score = max(0, min(10, sustainability_score))
        
        # Estimate ROI (assuming market price benefits)
        # For Indian context: ₹10,000-30,000 per ton (crop dependent)
        avg_price_per_ton = 15000  # Conservative estimate
        potential_revenue_increase = (expected_yield_increase_percent / 100) * avg_price_per_ton
        roi = (potential_revenue_increase / total_cost) if total_cost > 0 else 0
        
        return {
            'total_cost': round(total_cost),
            'expected_yield_increase_percent': round(expected_yield_increase_percent, 1),
            'expected_revenue_increase': round(potential_revenue_increase),
            'roi': round(roi, 2),
            'sustainability_score': round(sustainability_score, 1),
            'sustainable': sustainability_score >= 7.0
        }
    
    def get_complete_recommendation(
        self,
        crop_name: str,
        current_npk: Dict,
        soil_type: str = 'Loamy',
        farming_type: str = 'balanced',
        current_yield: float = None
    ) -> Dict:
        """
        Get complete fertilizer recommendation with all details.
        
        Args:
            crop_name: Name of crop (e.g., 'rice', 'wheat')
            current_npk: Current soil NPK {'n': 180, 'p': 35, 'k': 220}
            soil_type: Soil type
            farming_type: 'organic', 'balanced', or 'conventional'
            current_yield: Current yield in tons/acre (optional)
        
        Returns:
            Complete recommendation with deficit, products, schedule, cost-benefit
        """
        # Get crop requirements (case-insensitive)
        required_npk = self.get_crop_requirements(crop_name)
        if not required_npk:
            return {
                'error': f'Crop {crop_name} not found in database',
                'available_crops': list(self.crop_npk.get('crops', {}).keys())
            }
        
        # Calculate deficit
        deficit = self.calculate_npk_deficit(current_npk, required_npk)
        
        # Get fertilizer recommendations
        fertilizers = self.recommend_fertilizers(deficit, soil_type, farming_type)
        
        # Generate application schedule
        schedule = self.generate_application_schedule(crop_name, fertilizers)
        
        # Calculate cost-benefit
        cost_benefit = self.calculate_cost_benefit(fertilizers, crop_name, current_yield)
        
        return {
            'crop': crop_name.title(),
            'soil_type': soil_type,
            'farming_type': farming_type,
            'npk_analysis': {
                'current': current_npk,
                'required': required_npk,
                'deficit': deficit,
                'status': {
                    'n': 'Excess' if deficit['n'] < 0 else 'Deficit' if deficit['n'] > 0 else 'Adequate',
                    'p': 'Excess' if deficit['p'] < 0 else 'Deficit' if deficit['p'] > 0 else 'Adequate',
                    'k': 'Excess' if deficit['k'] < 0 else 'Deficit' if deficit['k'] > 0 else 'Adequate'
                }
            },
            'fertilizer_recommendations': fertilizers,
            'application_schedule': schedule,
            'cost_benefit_analysis': cost_benefit,
            'sustainability_advice': self._get_sustainability_advice(cost_benefit['sustainability_score'], farming_type)
        }
    
    def _get_sustainability_advice(self, score: float, farming_type: str) -> List[str]:
        """Get sustainability improvement advice"""
        advice = []
        
        if score < 7:
            advice.append("Consider incorporating organic fertilizers (FYM/vermicompost) for better soil health")
        
        if farming_type != 'organic':
            advice.append("Use neem-coated urea to reduce nitrogen loss and improve efficiency")
        
        advice.append("Always conduct soil test every 2-3 years for accurate recommendations")
        advice.append("Apply fertilizers in split doses to maximize nutrient use efficiency")
        advice.append("Use drip fertigation where possible to reduce wastage")
        
        return advice


# Create singleton instance
fertilizer_optimizer = FertilizerOptimizerService()
