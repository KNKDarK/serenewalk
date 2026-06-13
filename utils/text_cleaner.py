import re
from typing import List

def clean_user_input(text: str) -> str:
    """
    Clean and normalize user input text.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.,!?;:()\-]', '', text)
    
    # Normalize case (keep for medical terms)
    text = text.strip()
    
    return text

def extract_medical_entities(text: str) -> List[str]:
    """
    Simple medical entity extraction based on keywords.
    """
    medical_terms = {
        'symptom': ['pain', 'fever', 'cough', 'headache', 'nausea', 'fatigue', 
                   'dizziness', 'rash', 'swelling', 'bleeding'],
        'medication': ['aspirin', 'ibuprofen', 'paracetamol', 'antibiotic', 
                      'insulin', 'inhaler'],
        'condition': ['diabetes', 'hypertension', 'asthma', 'allergy', 
                     'infection', 'inflammation']
    }
    
    text_lower = text.lower()
    found_entities = []
    
    for category, terms in medical_terms.items():
        for term in terms:
            if term in text_lower:
                found_entities.append(f"{category}:{term}")
    
    return found_entities

def anonymize_text(text: str) -> str:
    """
    Remove potential personal identifiers from text.
    """
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove potential names (simplistic - looks for capitalized words at start)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove "My name is X" patterns
        line = re.sub(r'\b(my name is|i am|called)\s+[A-Z][a-z]+\b', r'\1 [NAME]', line, flags=re.IGNORECASE)
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length while preserving complete sentences.
    """
    if len(text) <= max_length:
        return text
    
    # Truncate to max_length
    truncated = text[:max_length]
    
    # Find last sentence boundary
    last_period = truncated.rfind('.')
    last_exclaim = truncated.rfind('!')
    last_question = truncated.rfind('?')
    
    last_boundary = max(last_period, last_exclaim, last_question)
    
    if last_boundary > max_length * 0.7:  # Only use boundary if it's not too early
        truncated = truncated[:last_boundary + 1]
    
    return truncated + "..."
