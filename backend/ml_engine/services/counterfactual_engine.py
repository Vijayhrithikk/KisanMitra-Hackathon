"""
Counterfactual Engine - Mistake Prevention AI
Answers "What if...?" questions to prevent farming errors.

This is what separates recommendation systems from decision systems.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(__name__)


class CounterfactualEngine:
    """
    Core Innovation: Simulate alternative scenarios before farmers commit.
    
    Examples:
    - "What if I delay sowing by 15 days?"
    - "What if rainfall fails in next 30 days?"
    - "What if I use 30% less fertilizer?"
    
    This prevents costly mistakes by showing consequences upfront.
    """
    
    def __init__(self):
        # Timing impact factors
        self.sowing_delay_impact = {
            'Kharif': {  # Monsoon crops
                10: {'yield_loss': 5, 'risk_increase': 10},   # 10 days delay
                15: {'yield_loss': 12, 'risk_increase': 20},
                20: {'yield_loss': 20, 'risk_increase': 35},
                30: {'yield_loss': 35, 'risk_increase': 50}
            },
            'Rabi': {  # Winter crops
                10: {'yield_loss': 3, 'risk_increase': 8},
                15: {'yield_loss': 8, 'risk_increase': 15},
                20: {'yield_loss': 15, 'risk_increase': 25},
                30: {'yield_loss': 28, 'risk_increase': 40}
            }
        }
    
    def simulate_sowing_delay(self, crop: str, current_recommendation: Dict,
                             delay_days: int, season: str = 'Kharif') -> Dict:
        """
        Simulate impact of delayed sowing.
        
        Critical for farmers who may want to wait for better prices or conditions.
        
        Args:
            crop: Crop name
            current_recommendation: Current recommendation data
            delay_days: Number of days to delay sowing
            season: Kharif or Rabi
        
        Returns:
            Modified recommendation showing impact of delay
        """
        # Get delay impact
        delay_ranges = self.sowing_delay_impact.get(season, self.sowing_delay_impact['Kharif'])
        
        # Find closest delay range
        closest_delay = min(delay_ranges.keys(), key=lambda x: abs(x - delay_days))
        impact = delay_ranges[closest_delay]
        
        # Scale impact proportionally
        scale_factor = delay_days / closest_delay
        yield_loss = int(impact['yield_loss'] * scale_factor)
        risk_increase = int(impact['risk_increase'] * scale_factor)
        
        # Create modified recommendation
        modified = copy.deepcopy(current_recommendation)
        
        # Adjust yield expectation
        original_yield_potential = modified.get('yield_potential', 'Medium')
        if yield_loss > 25:
            modified['yield_potential'] = 'Low'
        elif yield_loss > 15 and original_yield_potential == 'High':
            modified['yield_potential'] = 'Medium'
        
        # Increase risk
        if 'risk_analysis' in modified:
            original_loss_prob = modified['risk_analysis']['loss_probability']
            modified['risk_analysis']['loss_probability'] = min(95, original_loss_prob + risk_increase)
            modified['risk_analysis']['loss_probability_category'] = self._categorize_loss_prob(
                modified['risk_analysis']['loss_probability']
            )
        
        # Add scenario explanation
        modified['scenario'] = {
            'type': 'sowing_delay',
            'delay_days': delay_days,
            'yield_loss_percent': yield_loss,
            'risk_increase_percent': risk_increase,
            'explanation_en': self._get_delay_explanation_en(crop, delay_days, yield_loss, risk_increase),
            'explanation_te': self._get_delay_explanation_te(crop, delay_days, yield_loss, risk_increase),
            'recommendation': 'proceed' if yield_loss < 15 else 'reconsider'
        }
        
        return modified
    
    def simulate_rainfall_failure(self, crop: str, current_recommendation: Dict,
                                  failure_days: int, total_season_days: int = 120) -> Dict:
        """
        Simulate impact of rainfall failure.
        
        Critical for rain-dependent crops.
        
        Args:
            crop: Crop name
            current_recommendation: Current recommendation
            failure_days: Consecutive days without rain
            total_season_days: Total crop duration
        
        Returns:
            Modified recommendation showing drought impact
        """
        water_needs = current_recommendation.get('water_needs', 'Medium')
        
        # Calculate drought severity
        failure_percent = (failure_days / total_season_days) * 100
        
        # Water needs impact multiplier
        needs_multiplier = {
            'Low': 0.5,
            'Medium': 1.0,
            'High': 1.5
        }.get(water_needs, 1.0)
        
        # Calculate yield loss
        base_yield_loss = failure_percent * 0.6  # 60% conversion rate
        yield_loss = int(base_yield_loss * needs_multiplier)
        
        # Calculate risk increase
        risk_increase = int(failure_percent * 0.8 * needs_multiplier)
        
        # Create modified recommendation
        modified = copy.deepcopy(current_recommendation)
        
        # Catastrophic failure check
        if water_needs == 'High' and failure_days > 30:
            modified['yield_potential'] = 'Low'
            if 'risk_analysis' in modified:
                modified['risk_analysis']['loss_probability'] = 85
                modified['risk_analysis']['loss_probability_category'] = 'Very High'
        else:
            # Gradual degradation
            if 'risk_analysis' in modified:
                original_loss_prob = modified['risk_analysis']['loss_probability']
                modified['risk_analysis']['loss_probability'] = min(95, original_loss_prob + risk_increase)
                modified['risk_analysis']['loss_probability_category'] = self._categorize_loss_prob(
                    modified['risk_analysis']['loss_probability']
                )
        
        # Add scenario explanation
        modified['scenario'] = {
            'type': 'rainfall_failure',
            'failure_days': failure_days,
            'water_needs': water_needs,
            'yield_loss_percent': min(yield_loss, 90),
            'risk_increase_percent': min(risk_increase, 70),
            'explanation_en': self._get_rainfall_explanation_en(crop, failure_days, water_needs, yield_loss),
            'explanation_te': self._get_rainfall_explanation_te(crop, failure_days, water_needs, yield_loss),
            'recommendation': 'high_risk' if yield_loss > 40 else 'manageable'
        }
        
        return modified
    
    def simulate_fertilizer_reduction(self, crop: str, current_recommendation: Dict,
                                     reduction_percent: int) -> Dict:
        """
        Simulate impact of using less fertilizer.
        
        Useful for farmers trying to cut costs.
        
        Args:
            crop: Crop name
            current_recommendation: Current recommendation
            reduction_percent: Fertilizer reduction (0-100%)
        
        Returns:
            Modified recommendation showing fertilizer impact
        """
        # Get fertilizer plan if available
        fert_plan = current_recommendation.get('fertilizer_plan', {})
        
        # Estimate yield impact
        # Rule: First 30% reduction has minimal impact, beyond that it's linear
        if reduction_percent <= 30:
            yield_loss = int(reduction_percent * 0.3)
        else:
            yield_loss = 9 + int((reduction_percent - 30) * 0.7)
        
        # Quality degradation risk
        quality_risk = reduction_percent > 40
        
        # Create modified recommendation
        modified = copy.deepcopy(current_recommendation)
        
        # Adjust yield
        if yield_loss > 20:
            original_yield = modified.get('yield_potential', 'Medium')
            if original_yield == 'High':
                modified['yield_potential'] = 'Medium'
            elif original_yield == 'Medium':
                modified['yield_potential'] = 'Low'
        
        # Add scenario explanation
        cost_savings = 0
        if fert_plan and 'cost_benefit_analysis' in fert_plan:
            original_cost = fert_plan['cost_benefit_analysis'].get('total_cost', 0)
            cost_savings = int(original_cost * (reduction_percent / 100))
        
        modified['scenario'] = {
            'type': 'fertilizer_reduction',
            'reduction_percent': reduction_percent,
            'yield_loss_percent': yield_loss,
            'cost_savings': cost_savings,
            'quality_risk': quality_risk,
            'explanation_en': self._get_fertilizer_explanation_en(crop, reduction_percent, yield_loss, cost_savings, quality_risk),
            'explanation_te': self._get_fertilizer_explanation_te(crop, reduction_percent, yield_loss, cost_savings, quality_risk),
            'recommendation': 'acceptable' if reduction_percent <= 20 else 'not_recommended'
        }
        
        return modified
    
    def simulate_pest_outbreak(self, crop: str, current_recommendation: Dict,
                              outbreak_severity: str = 'moderate') -> Dict:
        """
        Simulate impact of pest outbreak.
        
        Helps farmers understand risk exposure.
        
        Args:
            crop: Crop name
            current_recommendation: Current recommendation
            outbreak_severity: 'mild', 'moderate', 'severe'
        
        Returns:
            Modified recommendation with pest outbreak impact
        """
        # Severity impact
        severity_impact = {
            'mild': {'yield_loss': 10, 'cost_increase': 15},
            'moderate': {'yield_loss': 25, 'cost_increase': 30},
            'severe': {'yield_loss': 50, 'cost_increase': 50}
        }
        
        impact = severity_impact.get(outbreak_severity, severity_impact['moderate'])
        
        # Crop-specific vulnerability
        high_risk_crops = ['Cotton', 'Tomato', 'Chilli', 'Rice']
        if crop in high_risk_crops:
            impact['yield_loss'] = int(impact['yield_loss'] * 1.2)
        
        # Create modified recommendation
        modified = copy.deepcopy(current_recommendation)
        
        # Adjust yield
        if impact['yield_loss'] > 30:
            modified['yield_potential'] = 'Low'
        
        # Add scenario explanation
        modified['scenario'] = {
            'type': 'pest_outbreak',
            'severity': outbreak_severity,
            'yield_loss_percent': impact['yield_loss'],
            'pest_control_cost_increase': impact['cost_increase'],
            'explanation_en': self._get_pest_explanation_en(crop, outbreak_severity, impact['yield_loss']),
            'explanation_te': self._get_pest_explanation_te(crop, outbreak_severity, impact['yield_loss']),
            'recommendation': 'high_monitoring' if crop in high_risk_crops else 'standard_care'
        }
        
        return modified
    
    def compare_scenarios(self, base_recommendation: Dict,
                         scenarios: List[Dict]) -> Dict:
        """
        Compare base case vs multiple what-if scenarios.
        
        Returns comparative analysis showing best/worst cases.
        """
        all_options = [base_recommendation] + scenarios
        
        # Extract loss probabilities
        loss_probs = []
        for opt in all_options:
            if 'risk_analysis' in opt:
                loss_probs.append(opt['risk_analysis']['loss_probability'])
            else:
                loss_probs.append(50)  # Default
        
        best_case_idx = loss_probs.index(min(loss_probs))
        worst_case_idx = loss_probs.index(max(loss_probs))
        
        return {
            'base_case': base_recommendation,
            'scenarios': scenarios,
            'best_case': all_options[best_case_idx],
            'worst_case': all_options[worst_case_idx],
            'risk_range': {
                'min': min(loss_probs),
                'max': max(loss_probs),
                'spread': max(loss_probs) - min(loss_probs)
            },
            'recommendation': self._get_scenario_recommendation(
                all_options[best_case_idx],
                all_options[worst_case_idx]
            )
        }
    
    # Helper methods for explanations
    
    def _categorize_loss_prob(self, prob: int) -> str:
        if prob < 25:
            return "Very Low"
        elif prob < 40:
            return "Low"
        elif prob < 60:
            return "Moderate"
        elif prob < 75:
            return "High"
        else:
            return "Very High"
    
    def _get_delay_explanation_en(self, crop: str, delay: int, yield_loss: int, risk_inc: int) -> str:
        return f"Delaying {crop} sowing by {delay} days may reduce yield by {yield_loss}% and increase failure risk by {risk_inc}%"
    
    def _get_delay_explanation_te(self, crop: str, delay: int, yield_loss: int, risk_inc: int) -> str:
        return f"{delay} రోజులు ఆలస్యం చేస్తే దిగుబడి {yield_loss}% తగ్గుతుంది, రిస్క్ {risk_inc}% పెరుగుతుంది"
    
    def _get_rainfall_explanation_en(self, crop: str, days: int, water_needs: str, yield_loss: int) -> str:
        if water_needs == 'High':
            return f"{crop} needs high water. {days} days without rain could reduce yield by {yield_loss}%"
        return f"{days} days without rain may reduce yield by {yield_loss}%"
    
    def _get_rainfall_explanation_te(self, crop: str, days: int, water_needs: str, yield_loss: int) -> str:
        if water_needs == 'High':
            return f"{days} రోజులు వర్షం లేకపోతే దిగుబడి {yield_loss}% తగ్గవచ్చు. ఎక్కువ నీరు కావాలి"
        return f"{days} రోజులు వర్షం లేకపోతే {yield_loss}% నష్టం"
    
    def _get_fertilizer_explanation_en(self, crop: str, reduction: int, yield_loss: int, savings: int, quality_risk: bool) -> str:
        msg = f"Reducing fertilizer by {reduction}% saves ₹{savings} but may reduce yield by {yield_loss}%"
        if quality_risk:
            msg += ". Quality may also suffer"
        return msg
    
    def _get_fertilizer_explanation_te(self, crop: str, reduction: int, yield_loss: int, savings: int, quality_risk: bool) -> str:
        msg = f"ఎరువులు {reduction}% తగ్గిస్తే ₹{savings} ఆదా, కానీ దిగుబడి {yield_loss}% తగ్గుతుంది"
        if quality_risk:
            msg += ". నాణ్యత కూడా తగ్గవచ్చు"
        return msg
    
    def _get_pest_explanation_en(self, crop: str, severity: str, yield_loss: int) -> str:
        return f"{severity.capitalize()} pest outbreak in {crop} could cause {yield_loss}% yield loss. Regular monitoring essential"
    
    def _get_pest_explanation_te(self, crop: str, severity: str, yield_loss: int) -> str:
        sev_map = {'mild': 'తక్కువ', 'moderate': 'మధ్యస్థ', 'severe': 'తీవ్రమైన'}
        return f"{sev_map.get(severity, 'మధ్యస్థ')} తెగులు వస్తే {yield_loss}% నష్టం. జాగ్రత్త అవసరం"
    
    def _get_scenario_recommendation(self, best: Dict, worst: Dict) -> str:
        best_loss = best.get('risk_analysis', {}).get('loss_probability', 50)
        worst_loss = worst.get('risk_analysis', {}).get('loss_probability', 50)
        
        if worst_loss - best_loss > 30:
            return "High variability - proceed with caution and monitor conditions closely"
        elif worst_loss > 70:
            return "Some scenarios show high risk - ensure mitigation measures are in place"
        else:
            return "Risk is manageable across scenarios - proceed with standard practices"


# Global instance
counterfactual_engine = CounterfactualEngine()
