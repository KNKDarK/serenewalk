import streamlit as st
import re
import random
import requests
import time
from datetime import datetime
from typing import Dict, List, Tuple
import hashlib

st.set_page_config(
    page_title="MediAI Pro - Advanced Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

# ============================================
# DARK THEME CSS
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .user-message {
        background: linear-gradient(135deg, #2a3f7e 0%, #1a2a5a 100%);
        color: #e0e8ff;
        padding: 12px 20px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 70%;
        float: right;
        clear: both;
        animation: slideInRight 0.3s ease;
        border: 1px solid #4a6faf;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1428 100%);
        color: #c8d0ff;
        padding: 12px 20px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 85%;
        float: left;
        clear: both;
        animation: slideInLeft 0.3s ease;
        border: 1px solid #3a5a9a;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2a3f7e 0%, #1a2a5a 100%);
        color: #e0e8ff;
        border: 1px solid #4a6faf;
        border-radius: 25px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #3a5f9e 0%, #2a3a7a 100%);
    }
    
    .stTextArea > div > div > textarea {
        background: #1a1f3a;
        color: #e0e8ff;
        border: 2px solid #3a5a9a;
        border-radius: 15px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6c9eff;
    }
    
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #4CAF50;
        border-radius: 50%;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    hr {
        border-color: #3a5a9a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# COMPREHENSIVE SYMPTOM DATABASE
# ============================================

SYMPTOM_DB = {
    'fever': {
        'keywords': ['fever', 'high temperature', 'hot', 'warm body', 'high fever', 'temperature'],
        'conditions': ['Common Cold', 'Influenza', 'COVID-19', 'Infection'],
        'advice': 'Monitor temperature every 4-6 hours. Stay hydrated with water and electrolytes. Rest and avoid strenuous activity.',
        'medications': 'Acetaminophen or Ibuprofen for fever >101°F',
        'severity': 'moderate'
    },
    'chills': {
        'keywords': ['chills', 'shivering', 'cold sweats', 'shaking'],
        'conditions': ['Fever response', 'Influenza', 'Infection'],
        'advice': 'Use warm blankets, drink warm fluids. Monitor for fever development.',
        'medications': 'Same as fever treatment',
        'severity': 'moderate'
    },
    'fatigue': {
        'keywords': ['fatigue', 'tired', 'exhausted', 'weak', 'no energy', 'lethargic'],
        'conditions': ['Viral infection', 'Anemia', 'Sleep deprivation', 'Stress'],
        'advice': 'Get adequate rest (7-9 hours). Stay hydrated. Light activity if possible.',
        'medications': 'Address underlying cause',
        'severity': 'moderate'
    },
    'headache': {
        'keywords': ['headache', 'head pain', 'migraine', 'pressure in head'],
        'conditions': ['Tension headache', 'Migraine', 'Sinusitis', 'Dehydration'],
        'advice': 'Rest in dark, quiet room. Apply cold compress. Stay hydrated.',
        'medications': 'NSAIDs (Ibuprofen, Naproxen) or Acetaminophen',
        'severity': 'moderate'
    },
    'sore throat': {
        'keywords': ['sore throat', 'scratchy throat', 'painful swallowing', 'throat pain'],
        'conditions': ['Viral pharyngitis', 'Strep throat', 'Allergies', 'Cold'],
        'advice': 'Gargle with warm salt water. Drink warm tea with honey. Use throat lozenges.',
        'medications': 'NSAIDs for pain, throat sprays',
        'severity': 'low'
    },
    'cough': {
        'keywords': ['cough', 'coughing', 'dry cough', 'wet cough', 'persistent cough'],
        'conditions': ['Common cold', 'Bronchitis', 'COVID-19', 'Allergies'],
        'advice': 'Stay hydrated, use humidifier, honey for cough (adults). Elevate head when sleeping.',
        'medications': 'Cough suppressants (dry cough), Expectorants (wet cough)',
        'severity': 'moderate'
    },
    'runny nose': {
        'keywords': ['runny nose', 'stuffy nose', 'nasal congestion', 'blocked nose'],
        'conditions': ['Common cold', 'Allergies', 'Sinusitis', 'Flu'],
        'advice': 'Use saline spray, humidifier, stay hydrated, elevate head.',
        'medications': 'Antihistamines, Decongestants',
        'severity': 'low'
    },
    'muscle pain': {
        'keywords': ['muscle pain', 'body aches', 'joint pain', 'muscle ache', 'sore muscles'],
        'conditions': ['Influenza', 'COVID-19', 'Fibromyalgia', 'Overexertion'],
        'advice': 'Rest, gentle stretching, warm baths, massage.',
        'medications': 'NSAIDs (Ibuprofen, Naproxen)',
        'severity': 'moderate'
    },
    'nausea': {
        'keywords': ['nausea', 'queasy', 'sick stomach', 'feel like vomiting'],
        'conditions': ['Gastroenteritis', 'Food poisoning', 'Migraine', 'Pregnancy'],
        'advice': 'Eat bland foods (crackers, toast). Sip clear fluids. Avoid strong odors.',
        'medications': 'Anti-nausea medications (consult doctor)',
        'severity': 'moderate'
    },
    'vomiting': {
        'keywords': ['vomiting', 'threw up', 'throwing up', 'vomit'],
        'conditions': ['Gastroenteritis', 'Food poisoning', 'Migraine'],
        'advice': 'Stop eating solid foods. Sip water or electrolyte solution. Rest.',
        'medications': 'Anti-emetics (prescription)',
        'severity': 'high'
    },
    'diarrhea': {
        'keywords': ['diarrhea', 'loose stool', 'watery stool', 'frequent bowel movements'],
        'conditions': ['Gastroenteritis', 'Food poisoning', 'IBS'],
        'advice': 'Stay hydrated with ORS. Eat BRAT diet (Banana, Rice, Applesauce, Toast).',
        'medications': 'Anti-diarrheal (if no fever/blood)',
        'severity': 'moderate'
    },
    'rash': {
        'keywords': ['rash', 'skin rash', 'hives', 'red spots', 'itchy skin'],
        'conditions': ['Allergic reaction', 'Viral rash', 'Eczema', 'Contact dermatitis'],
        'advice': 'Avoid scratching, cool compresses, oatmeal baths.',
        'medications': 'Antihistamines, Hydrocortisone cream',
        'severity': 'moderate'
    },
    'chest pain': {
        'keywords': ['chest pain', 'chest pressure', 'heart pain', 'tight chest'],
        'conditions': ['⚠️ EMERGENCY - Possible heart attack, Angina, Anxiety'],
        'advice': '⚠️ SEEK IMMEDIATE MEDICAL ATTENTION. Do not wait.',
        'medications': 'Emergency care required',
        'severity': 'emergency'
    },
    'difficulty breathing': {
        'keywords': ['difficulty breathing', 'shortness of breath', 'can\'t breathe', 'breathless'],
        'conditions': ['⚠️ EMERGENCY - Asthma, COVID-19, Heart issue, Pneumonia'],
        'advice': '⚠️ CALL 911 IMMEDIATELY',
        'medications': 'Emergency care required',
        'severity': 'emergency'
    },
    'swollen glands': {
        'keywords': ['swollen glands', 'swollen lymph nodes', 'enlarged nodes', 'lumps in neck'],
        'conditions': ['Infection', 'Mononucleosis', 'Flu', 'Strep throat'],
        'advice': 'Rest, warm compress on swollen area, stay hydrated.',
        'medications': 'NSAIDs for pain/swelling',
        'severity': 'moderate'
    },
    'mouth ulcers': {
        'keywords': ['mouth ulcers', 'canker sores', 'mouth sores', 'oral ulcers'],
        'conditions': ['Stress', 'Nutritional deficiency', 'Viral infection'],
        'advice': 'Avoid spicy/acidic foods, salt water rinse, topical gels.',
        'medications': 'Topical anesthetics, Antimicrobial mouthwash',
        'severity': 'low'
    }
}

# ============================================
# MEDICAL SEARCH ENGINE
# ============================================

class MedicalSearch:
    def __init__(self):
        self.cache = {}
    
    def search(self, query: str) -> Dict:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        if query_hash in self.cache:
            return self.cache[query_hash]
        
        results = {'summary': '', 'sources': []}
        
        try:
            url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}+medical&format=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('Abstract'):
                    results['summary'] = data['Abstract'][:500]
                    if data.get('AbstractURL'):
                        results['sources'].append(data['AbstractURL'])
        except:
            pass
        
        self.cache[query_hash] = results
        return results

# ============================================
# INTELLIGENT RESPONSE GENERATOR
# ============================================

class MedicalChatbot:
    def __init__(self):
        self.search_engine = MedicalSearch()
        self.emergency_keywords = ['chest pain', 'difficulty breathing', 'severe bleeding', 
                                   'heart attack', 'stroke', 'can\'t breathe', 'emergency']
    
    def extract_symptoms(self, text: str) -> List[Dict]:
        """Extract all symptoms with their details"""
        text_lower = text.lower()
        detected = []
        
        for symptom, info in SYMPTOM_DB.items():
            for keyword in info['keywords']:
                if keyword in text_lower:
                    detected.append({
                        'name': symptom,
                        'info': info
                    })
                    break
        
        return detected
    
    def analyze(self, text: str) -> Dict:
        """Analyze symptoms and generate response"""
        detected_symptoms = self.extract_symptoms(text)
        
        # Check for emergency first
        text_lower = text.lower()
        for emergency in self.emergency_keywords:
            if emergency in text_lower:
                return {
                    'is_emergency': True,
                    'response': """🚨 **EMERGENCY DETECTED - SEEK HELP IMMEDIATELY!** 🚨

**Call 911 or your local emergency number NOW!**

⚠️ Do not wait. Do not drive yourself if having chest pain or breathing difficulty.

Tell the operator:
- Your symptoms
- Your location  
- Any medical conditions

**This requires immediate professional medical attention.**""",
                    'symptoms': detected_symptoms
                }
        
        if not detected_symptoms:
            return {
                'is_emergency': False,
                'response': """I hear you, but I need more details to help you properly. 🌟

Could you please tell me:
- What specific symptoms are you experiencing? (fever, cough, headache, etc.)
- How long have you had them?
- How severe are they on a scale of 1-10?

The more details you share, the better I can assist you! 💙""",
                'symptoms': []
            }
        
        # Group symptoms by severity
        has_high = any(s['info']['severity'] == 'high' for s in detected_symptoms)
        conditions = set()
        all_advice = []
        all_meds = []
        symptom_names = []
        
        for s in detected_symptoms:
            symptom_names.append(s['name'])
            conditions.update(s['info']['conditions'])
            all_advice.append(s['info']['advice'])
            all_meds.append(s['info']['medications'])
        
        # Build intelligent response
        response_parts = []
        
        # Empathetic opening
        openings = [
            "Thank you for sharing that with me. 💙 Let me analyze your symptoms carefully.",
            "I understand how you're feeling. Here's what I've found based on your symptoms:",
            "I appreciate you telling me about this. Here's my analysis:",
            "Let me help you understand what might be going on."
        ]
        response_parts.append(random.choice(openings))
        
        # List detected symptoms
        response_parts.append(f"\n📋 **Symptoms I detected:** {', '.join(symptom_names)}")
        
        # Possible conditions
        response_parts.append(f"\n🩺 **Possible conditions:** {', '.join(list(conditions)[:4])}")
        
        # Advice
        unique_advice = list(set(all_advice))[:3]
        response_parts.append(f"\n⚕️ **Medical advice:**")
        for advice in unique_advice:
            response_parts.append(f"  • {advice}")
        
        # Medications
        unique_meds = list(set(all_meds))[:3]
        response_parts.append(f"\n💊 **Possible medications:** {', '.join(unique_meds)}")
        
        # Severity-based recommendation
        if has_high:
            response_parts.append("\n⚠️ **URGENT RECOMMENDATION:** Please see a doctor within 24 hours.")
        elif len(detected_symptoms) > 2:
            response_parts.append("\n💡 **Recommendation:** Monitor symptoms closely. Consider telemedicine consultation if symptoms persist.")
        else:
            response_parts.append("\n✅ **Recommendation:** Rest at home, stay hydrated. Most mild illnesses resolve within 3-5 days.")
        
        # When to seek care
        response_parts.append("\n🏥 **When to seek medical care:**")
        response_parts.append("• Fever >103°F (39.4°C) lasting more than 3 days")
        response_parts.append("• Difficulty breathing or chest pain")
        response_parts.append("• Severe dehydration (no urination for 8+ hours)")
        response_parts.append("• Confusion or difficulty staying awake")
        
        # Disclaimer
        response_parts.append("\n---\n*⚠️ I'm an AI assistant. This information is for educational purposes. Always consult a healthcare provider for medical advice.*")
        
        return {
            'is_emergency': False,
            'response': '\n'.join(response_parts),
            'symptoms': detected_symptoms,
            'conditions': list(conditions),
            'severity': 'high' if has_high else 'moderate'
        }

# ============================================
# SESSION STATE
# ============================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'bot' not in st.session_state:
    st.session_state.bot = MedicalChatbot()

# ============================================
# HEADER
# ============================================

st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h1 style="background: linear-gradient(135deg, #6c9eff, #4a6faf); 
               -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent;
               font-size: 2.5em;">
        🩺 MediAI Pro
    </h1>
    <p style="color: #a0b4e0;">Intelligent Medical Assistant with Real-time Symptom Analysis</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin: 10px 0;">
        <span class="status-online"></span>
        <span style="color: #a0b4e0;">AI Active • Ready to help</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🌙 Dashboard")
    st.markdown("---")
    
    st.markdown("### 📊 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    st.markdown("---")
    
    st.markdown("### ✨ Features")
    st.markdown("""
    - ✅ Real-time Symptom Analysis
    - ✅ Emergency Detection
    - ✅ Treatment Suggestions
    - ✅ Medication Information
    - ✅ Evidence-based Responses
    """)
    
    st.markdown("---")
    
    st.error("""
    🚨 **EMERGENCY?**
    
    Call **911** or your local emergency number immediately if you have:
    - Chest pain
    - Difficulty breathing
    - Severe bleeding
    - Loss of consciousness
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================
# MAIN CHAT
# ============================================

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div style="display: flex; justify-content: flex-end;"><div class="user-message">👤 {msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="display: flex; justify-content: flex-start;"><div class="bot-message">🤖 {msg["content"]}</div></div>', unsafe_allow_html=True)

# Quick questions
st.markdown("### 💡 Quick Questions")
cols = st.columns(4)
questions = [
    ("🤒 Fever & Chills", "I have fever and chills for 2 days"),
    ("🤕 Headache & Nausea", "I have severe headache and nausea"),
    ("😷 Cold & Cough", "I have cough and runny nose"),
    ("🩺 Multiple Symptoms", "I have fever, headache, fatigue, and sore throat")
]

for i, (label, text) in enumerate(questions):
    with cols[i]:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": text})
            with st.spinner("Analyzing symptoms..."):
                result = st.session_state.bot.analyze(text)
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            st.rerun()

# User input
st.markdown("---")
user_input = st.text_area(
    "",
    placeholder="💬 Describe your symptoms in detail... (e.g., 'I have fever, headache, muscle pain, and sore throat for 3 days')",
    height=80,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])
with col1:
    send = st.button("📤 Send", type="primary", use_container_width=True)

if send and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("🧠 Analyzing your symptoms..."):
        time.sleep(0.5)
        result = st.session_state.bot.analyze(user_input)
        st.session_state.messages.append({"role": "assistant", "content": result['response']})
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c9eff; font-size: 0.8em;">
    <p>⚡ Powered by AI Medical Intelligence | For informational purposes only</p>
</div>
""", unsafe_allow_html=True)
