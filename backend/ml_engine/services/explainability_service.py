"""
Explainability Service - Trust Builder
Converts ML jargon into farmer-friendly Telugu/English explanations.

Philosophy: Farmers trust AI that explains 'why' in their language.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """
    Core Innovation: Convert technical AI outputs into trust-building explanations.
    
    Instead of: "78% confidence, RandomForest prediction"
    We say: "మట్టికి బాగా సరిపోతుంది. వాతావరణం అనుకూలం" 
            (Fits soil well. Weather is favorable)
    """
    
    def __init__(self):
        # Crop names in Telugu
        self.crop_names_te = {
            'Rice': 'వరి', 'Cotton': 'పత్తి', 'Maize': 'మొక్కజొన్న',
            'Groundnut': 'వేరుశెనగ', 'Chilli': 'మిర్చి', 'Sugarcane': 'చెరకు',
            'Turmeric': 'పసుపు', 'Tobacco': 'పొగాకు', 'Pulses': 'పప్పులు',
            'Red Gram': 'కందులు', 'Bengal Gram': 'శెనగలు',
            'Sunflower': 'సూర్యకాంతం', 'Tomato': 'టమాటో'
        }
    
    def explain_recommendation(self, crop: str, recommendation: Dict,
                              language: str = 'en') -> Dict:
        """
        Generate comprehensive explanation for a crop recommendation.
        
        Args:
            crop: Crop name
            recommendation: Full recommendation dict
            language: 'en' or 'te'
        
        Returns:
            Structured explanation with short (SMS-friendly) and detailed versions
        """
        if language == 'te':
            return self._explain_telugu(crop, recommendation)
        else:
            return self._explain_english(crop, recommendation)
    
    def _explain_english(self, crop: str, rec: Dict) -> Dict:
        """Generate English explanation."""
        confidence = rec.get('confidence', 70)
        risk_analysis = rec.get('risk_analysis', {})
        loss_prob = risk_analysis.get('loss_probability', 50)
        risk_breakdown = risk_analysis.get('risk_breakdown', {})
        
        # Build reason components
        reasons = []
        concerns = []
        
        # Soil match
        reason = rec.get('reason', '')
        if 'soil' in reason.lower() or 'Excellent match' in reason:
            reasons.append("soil suits this crop")
        
        # Weather
        weather_risk = risk_breakdown.get('weather_risk', {})
        if weather_risk.get('level') == 'Low':
            reasons.append("weather is favorable")
        elif weather_risk.get('level') == 'High':
            concerns.append("weather may be challenging")
        
        # Market
        market_risk = risk_breakdown.get('market_risk', {})
        if market_risk.get('level') == 'High':
            concerns.append("market prices can fluctuate")
        
        # Construct short explanation (SMS-friendly, <100 chars)
        if loss_prob < 30:
            short = f"✅ {crop}: Good choice. {', '.join(reasons[:2])}"
        elif loss_prob < 60:
            short = f"⚠️ {crop}: Okay option but {concerns[0] if concerns else 'watch conditions'}"
        else:
            short = f"❌ {crop}: Risky. {concerns[0] if concerns else 'High risk'}"
        
        short = short[:95] + "..." if len(short) > 95 else short
        
        # Detailed explanation
        detailed_parts = [
            f"**Why {crop}?**"
        ]
        
        if reasons:
            detailed_parts.append(f"✓ " + ", ".join(reasons))
        
        if concerns:
            detailed_parts.append(f"⚠ Concerns: " + ", ".join(concerns))
        
        # Risk breakdown
        detailed_parts.append(f"\n**Risk Analysis:**")
        detailed_parts.append(f"• Loss probability: {loss_prob}%")
        detailed_parts.append(f"• Weather risk: {weather_risk.get('level', 'Medium')}")
        detailed_parts.append(f"• Market risk: {market_risk.get('level', 'Medium')}")
        
        # What to watch
        dominant_risk = risk_analysis.get('dominant_risk', 'Weather')
        detailed_parts.append(f"\n**Monitor:** {dominant_risk} conditions closely")
        
        return {
            'short': short,
            'detailed': '\n'.join(detailed_parts),
            'voice_friendly': short,  # Same as short for English
            'sms_compatible': True,
            'character_count': len(short)
        }
    
    def _explain_telugu(self, crop: str, rec: Dict) -> Dict:
        """Generate Telugu explanation (farmer vocabulary)."""
        crop_te = self.crop_names_te.get(crop, crop)
        confidence = rec.get('confidence', 70)
        risk_analysis = rec.get('risk_analysis', {})
        loss_prob = risk_analysis.get('loss_probability', 50)
        risk_breakdown = risk_analysis.get('risk_breakdown', {})
        
        # Build Telugu reasons
        reasons = []
        concerns = []
        
        # Soil match
        reason = rec.get('reason', '')
        if 'soil' in reason.lower() or 'Excellent match' in reason:
            reasons.append("మట్టికి బాగా సరిపోతుంది")
        
        # Weather
        weather_risk = risk_breakdown.get('weather_risk', {})
        if weather_risk.get('level') == 'Low':
            reasons.append("వాతావరణం అనుకూలం")
        elif weather_risk.get('level') == 'High':
            concerns.append("వాతావరణం సవాలుగా ఉండవచ్చు")
        
        # Water
        water_needs = rec.get('water_needs', 'Medium')
        forecast_insight = rec.get('forecast_insight', '')
        if 'rain' in forecast_insight.lower() and 'favorable' in forecast_insight.lower():
            reasons.append("వర్షం సరిపడా ఉంటుంది")
        elif water_needs == 'High' and weather_risk.get('level') == 'High':
            concerns.append("ఎక్కువ నీరు కావాలి కానీ వర్షం తక్కువ")
        
        # Market
        market_risk = risk_breakdown.get('market_risk', {})
        if market_risk.get('level') == 'High':
            concerns.append("ధరలు మారవచ్చు")
        
        # Construct short Telugu explanation (SMS-friendly)
        if loss_prob < 30:
            short = f"✅ {crop_te}: మంచి ఎంపిక. {'. '.join(reasons[:2])}"
        elif loss_prob < 60:
            short = f"⚠️ {crop_te}: సరే కానీ {concerns[0] if concerns else 'జాగ్రత్త'}"
        else:
            short = f"❌ {crop_te}: రిస్క్ ఎక్కువ. {concerns[0] if concerns else 'జాగ్రత్తగా ఆలోచించండి'}"
        
        short = short[:95] + "..." if len(short) > 95 else short
        
        # Detailed Telugu explanation
        detailed_parts = [
            f"**{crop_te} ఎందుకు?**"
        ]
        
        if reasons:
            detailed_parts.append("✓ " + ", ".join(reasons))
        
        if concerns:
            detailed_parts.append("⚠ జాగ్రత్తలు: " + ", ".join(concerns))
        
        # Risk breakdown in Telugu
        detailed_parts.append(f"\n**రిస్క్ విశ్లేషణ:**")
        detailed_parts.append(f"• నష్టం అవకాశం: {loss_prob}%")
        
        weather_level_te = {'Low': 'తక్కువ', 'Medium': 'మధ్యస్థం', 'High': 'అధికం'}
        detailed_parts.append(f"• వాతావరణ రిస్క్: {weather_level_te.get(weather_risk.get('level', 'Medium'), 'మధ్యస్థం')}")
        detailed_parts.append(f"• మార్కెట్ రిస్క్: {weather_level_te.get(market_risk.get('level', 'Medium'), 'మధ్యస్థం')}")
        
        # What to monitor
        risk_map = {'Weather': 'వాతావరణం', 'Market': 'మార్కెట్', 'Pest': 'తెగులు', 'Cost': 'ఖర్చు'}
        dominant = risk_analysis.get('dominant_risk', 'Weather')
        detailed_parts.append(f"\n**గమనించండి:** {risk_map.get(dominant, dominant)} జాగ్రత్తగా చూడండి")
        
        return {
            'short': short,
            'detailed': '\n'.join(detailed_parts),
            'voice_friendly': short.replace('✅', '').replace('⚠️', '').replace('❌', ''),
            'sms_compatible': True,
            'character_count': len(short)
        }
    
    def explain_risk_comparison(self, crop_a: str, crop_b: str,
                               rec_a: Dict, rec_b: Dict,
                               language: str = 'en') -> str:
        """
        Explain why one crop is better/riskier than another.
        
        Example: "Cotton has higher yield but pulses are safer in low rain"
        """
        loss_a = rec_a.get('risk_analysis', {}).get('loss_probability', 50)
        loss_b = rec_b.get('risk_analysis', {}).get('loss_probability', 50)
        
        if language == 'te':
            return self._compare_telugu(crop_a, crop_b, rec_a, rec_b, loss_a, loss_b)
        else:
            return self._compare_english(crop_a, crop_b, rec_a, rec_b, loss_a, loss_b)
    
    def _compare_english(self, crop_a: str, crop_b: str, rec_a: Dict, rec_b: Dict,
                        loss_a: int, loss_b: int) -> str:
        """English comparison."""
        safer_crop = crop_a if loss_a < loss_b else crop_b
        riskier_crop = crop_b if loss_a < loss_b else crop_a
        safer_rec = rec_a if loss_a < loss_b else rec_b
        
        yield_a = rec_a.get('yield_potential', 'Medium')
        yield_b = rec_b.get('yield_potential', 'Medium')
        
        if yield_a == 'High' and yield_b != 'High' and loss_a > loss_b:
            return f"{crop_a} has higher yield potential but {crop_b} is safer with lower risk"
        elif loss_a < loss_b:
            diff = loss_b - loss_a
            return f"{safer_crop} is safer ({diff}% lower risk) than {riskier_crop}"
        else:
            return f"Both options have similar risk levels"
    
    def _compare_telugu(self, crop_a: str, crop_b: str, rec_a: Dict, rec_b: Dict,
                       loss_a: int, loss_b: int) -> str:
        """Telugu comparison."""
        crop_a_te = self.crop_names_te.get(crop_a, crop_a)
        crop_b_te = self.crop_names_te.get(crop_b, crop_b)
        
        safer_crop = crop_a_te if loss_a < loss_b else crop_b_te
        riskier_crop = crop_b_te if loss_a < loss_b else crop_a_te
        
        yield_a = rec_a.get('yield_potential', 'Medium')
        yield_b = rec_b.get('yield_potential', 'Medium')
        
        if yield_a == 'High' and yield_b != 'High' and loss_a > loss_b:
            return f"{crop_a_te} దిగుబడి ఎక్కువ కానీ {crop_b_te} సురక్షితం"
        elif loss_a < loss_b:
            diff = loss_b - loss_a
            return f"{safer_crop} {riskier_crop} కంటే {diff}% సురక్షితం"
        else:
            return "రెండు ఎంపికలు సమానమైన రిస్క్ ఉన్నాయి"
    
    def explain_why_not(self, crop: str, rec: Dict, language: str = 'en') -> str:
        """
        Explain why a crop might NOT be suitable.
        
        This builds trust - showing what could go wrong.
        """
        risk_analysis = rec.get('risk_analysis', {})
        loss_prob = risk_analysis.get('loss_probability', 50)
        
        if loss_prob < 40:
            # Low risk - explain minor concerns
            if language == 'te':
                return f"పెద్ద సమస్యలు లేవు, కానీ సాధారణ జాగ్రత్తలు కావాలి"
            return "No major issues, but standard care needed"
        
        # High risk - explain main concerns
        dominant_risk = risk_analysis.get('dominant_risk', 'Weather')
        risk_breakdown = risk_analysis.get('risk_breakdown', {})
        risk_desc = risk_breakdown.get(f'{dominant_risk.lower()}_risk', {}).get('description', '')
        
        if language == 'te':
            risk_map = {'Weather': 'వాతావరణం', 'Market': 'మార్కెట్ ధరలు',
                       'Pest': 'తెగులు', 'Cost': 'ఖర్చు'}
            return f"{risk_map.get(dominant_risk, dominant_risk)} సమస్య ఉండవచ్చు. రిస్క్ {loss_prob}%"
        
        return f"{dominant_risk} conditions may be challenging. Risk: {loss_prob}%"
    
    def generate_voice_script(self, crop: str, rec: Dict, language: str = 'te') -> str:
        """
        Generate ultra-short voice-friendly script for SMS/voice bots.
        
        Max 160 characters (single SMS).
        """
        if language == 'te':
            crop_te = self.crop_names_te.get(crop, crop)
            loss_prob = rec.get('risk_analysis', {}).get('loss_probability', 50)
            
            if loss_prob < 30:
                script = f"{crop_te} బాగుంటుంది. మట్టి సరిపోతుంది. రిస్క్ తక్కువ."
            elif loss_prob < 60:
                script = f"{crop_te} సరే. కానీ వాతావరణం చూడండి. రిస్క్ మధ్యస్థం."
            else:
                script = f"{crop_te} రిస్క్ ఎక్కువ. వేరే పంట ఆలోచించండి."
        else:
            loss_prob = rec.get('risk_analysis', {}).get('loss_probability', 50)
            if loss_prob < 30:
                script = f"{crop} is good. Soil fits well. Low risk."
            elif loss_prob < 60:
                script = f"{crop} is okay. Watch weather. Medium risk."
            else:
                script = f"{crop} is risky. Consider alternatives."
        
        return script[:160]


# Global instance
explainability_service = ExplainabilityService()
