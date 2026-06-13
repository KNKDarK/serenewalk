from typing import Dict, Optional
from modules.medical_model import medical_advice
from modules.symptom_parser import identify_emergency_keywords

def generate_comprehensive_advice(
    model_path: str,
    symptom_summary: str,
    extracted_symptoms: Dict,
    location: Optional[Dict] = None
) -> Dict:
    """
    Generate comprehensive medical advice with triage level.
    """
    # Check for emergency keywords first
    emergency_keywords = identify_emergency_keywords(symptom_summary)
    
    if emergency_keywords:
        return {
            'triage_level': 'EMERGENCY',
            'message': f"⚠️ **URGENT MEDICAL ATTENTION NEEDED** ⚠️\n\n"
                      f"Your symptoms include potentially serious warning signs: {', '.join(emergency_keywords)}\n\n"
                      f"**PLEASE SEEK IMMEDIATE MEDICAL CARE** - Call emergency services or go to the nearest emergency room.\n\n"
                      f"Do not wait for AI advice. This could be life-threatening.",
            'advice': None,
            'requires_immediate_care': True
        }
    
    # Check for urgent but not emergency symptoms
    urgent_indicators = ['severe pain', 'high fever', 'vomiting blood', 'unable to eat']
    is_urgent = any(indicator in symptom_summary.lower() for indicator in urgent_indicators)
    
    # Get standard AI advice
    ai_advice = medical_advice(model_path, symptom_summary, location)
    
    if is_urgent:
        return {
            'triage_level': 'URGENT',
            'message': "🏥 **Should be seen within 24 hours**\n\n"
                      "Your symptoms suggest you should see a healthcare provider soon.\n\n"
                      f"{ai_advice}",
            'advice': ai_advice,
            'requires_immediate_care': False
        }
    else:
        return {
            'triage_level': 'NON-URGENT',
            'message': f"💡 **General Advice**\n\n{ai_advice}",
            'advice': ai_advice,
            'requires_immediate_care': False
        }

def format_advice_response(advice_dict: Dict) -> str:
    """
    Format the advice dictionary into a user-friendly string.
    """
    if advice_dict['triage_level'] == 'EMERGENCY':
        return advice_dict['message']
    else:
        return advice_dict['message']
