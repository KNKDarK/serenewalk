import re
from typing import Dict, List

def extract_symptoms(text: str) -> Dict:
    """
    Extract structured symptom information from user text.
    """
    text_lower = text.lower()
    
    # Common symptom keywords
    symptom_keywords = {
        'pain': ['pain', 'ache', 'hurt', 'sore'],
        'fever': ['fever', 'temperature', 'hot', 'chills'],
        'respiratory': ['cough', 'breathing', 'shortness', 'wheeze'],
        'digestive': ['nausea', 'vomit', 'diarrhea', 'stomach', 'bloating'],
        'neurological': ['headache', 'dizzy', 'confusion', 'numb'],
        'fatigue': ['tired', 'fatigue', 'exhaustion', 'weak'],
        'skin': ['rash', 'itch', 'redness', 'swelling']
    }
    
    # Time indicators
    time_patterns = {
        'days': r'(\d+)\s*days?',
        'hours': r'(\d+)\s*hours?',
        'weeks': r'(\d+)\s*weeks?',
        'months': r'(\d+)\s*months?'
    }
    
    # Extract symptoms
    detected_symptoms = []
    for category, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_symptoms.append(keyword)
    
    # Extract duration
    duration = None
    for unit, pattern in time_patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            duration = f"{match.group(1)} {unit}"
            break
    
    # Extract severity indicators
    severity_words = ['severe', 'mild', 'moderate', 'extreme', 'intense']
    severity = None
    for word in severity_words:
        if word in text_lower:
            severity = word
            break
    
    return {
        'symptoms': list(set(detected_symptoms)),  # Remove duplicates
        'duration': duration,
        'severity': severity,
        'raw_text': text
    }

def identify_emergency_keywords(text: str) -> List[str]:
    """
    Identify potential emergency keywords that require immediate attention.
    """
    emergency_keywords = [
        'chest pain', 'heart attack', 'stroke', 'severe bleeding',
        'difficulty breathing', 'unconscious', 'seizure', 'suicidal',
        'poison', 'overdose', 'paralysis', 'cannot speak', 'blue lips'
    ]
    
    text_lower = text.lower()
    found = [kw for kw in emergency_keywords if kw in text_lower]
    return found

def format_symptoms_for_display(symptom_dict: Dict) -> str:
    """
    Format the extracted symptoms for display to user.
    """
    lines = []
    
    if symptom_dict['symptoms']:
        lines.append(f"**Detected symptoms:** {', '.join(symptom_dict['symptoms'])}")
    
    if symptom_dict['duration']:
        lines.append(f"**Duration:** {symptom_dict['duration']}")
    
    if symptom_dict['severity']:
        lines.append(f"**Severity:** {symptom_dict['severity'].capitalize()}")
    
    return '\n'.join(lines) if lines else "No specific symptoms extracted. Please provide more details."
