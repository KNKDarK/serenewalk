import streamlit as st
import requests
import json
import re
import random
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
from streamlit_js_eval import get_geolocation
import math

# Page config
st.set_page_config(
    page_title="MediAI - Medical Assistant with Hospital Locator",
    page_icon="🏥",
    layout="wide"
)

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .hospital-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .hospital-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .emergency-badge {
        background: #ff4444;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 12px;
        display: inline-block;
    }
    
    .clinic-badge {
        background: #4CAF50;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 12px;
        display: inline-block;
    }
    
    .distance-badge {
        background: #2196F3;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 12px;
        display: inline-block;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background: white;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .location-box {
        background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOCATION SERVICES
# ============================================

class LocationService:
    def __init__(self):
        self.user_location = None
        self.nearby_hospitals = []
    
    def get_location_from_ip(self) -> Optional[Dict]:
        """Get location from IP address (fallback)"""
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'lat': data.get('latitude', 0),
                    'lon': data.get('longitude', 0),
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'ip': data.get('ip', 'Unknown')
                }
        except:
            pass
        return None
    
    def get_nearby_hospitals(self, lat: float, lon: float, radius_km: float = 5) -> List[Dict]:
        """Find nearby hospitals and clinics using OpenStreetMap Overpass API"""
        hospitals = []
        
        # Overpass API query for hospitals and clinics
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="clinic"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="doctors"](around:{radius_km * 1000},{lat},{lon});
          node["healthcare"="hospital"](around:{radius_km * 1000},{lat},{lon});
          node["healthcare"="clinic"](around:{radius_km * 1000},{lat},{lon});
          way["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
          way["amenity"="clinic"](around:{radius_km * 1000},{lat},{lon});
        );
        out body;
        """
        
        try:
            response = requests.get(overpass_url, params={"data": query}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    
                    # Determine facility type
                    if 'hospital' in tags.get('amenity', '') or 'hospital' in tags.get('healthcare', ''):
                        facility_type = 'hospital'
                        badge = '🏥'
                    elif 'clinic' in tags.get('amenity', '') or 'clinic' in tags.get('healthcare', ''):
                        facility_type = 'clinic'
                        badge = '🏪'
                    else:
                        facility_type = 'medical'
                        badge = '🩺'
                    
                    # Get name
                    name = tags.get('name', 'Unknown Facility')
                    
                    # Calculate distance
                    element_lat = element.get('lat')
                    element_lon = element.get('lon')
                    distance = self.calculate_distance(lat, lon, element_lat, element_lon) if element_lat else float('inf')
                    
                    # Get address
                    address = tags.get('addr:full', '')
                    if not address:
                        address = f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip()
                    if not address:
                        address = "Address not available"
                    
                    hospitals.append({
                        'name': name,
                        'type': facility_type,
                        'badge': badge,
                        'lat': element_lat,
                        'lon': element_lon,
                        'distance_km': round(distance, 2),
                        'address': address,
                        'phone': tags.get('phone', 'N/A'),
                        'opening_hours': tags.get('opening_hours', '24/7' if facility_type == 'hospital' else 'Unknown')
                    })
                
                # Sort by distance
                hospitals.sort(key=lambda x: x['distance_km'])
                
        except Exception as e:
            st.error(f"Error finding nearby facilities: {str(e)}")
        
        return hospitals[:10]  # Return top 10
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers using Haversine formula"""
        if not lat2 or not lon2:
            return float('inf')
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_nominatim_address(self, lat: float, lon: float) -> str:
        """Get address from coordinates using Nominatim"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18"
            headers = {'User-Agent': 'MedicalAdvisor/1.0'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('display_name', 'Unknown location')[:100]
        except:
            pass
        return "Location detected"

# ============================================
# MEDICAL CHATBOT
# ============================================

class MedicalChatbot:
    def __init__(self):
        self.symptom_keywords = {
            'fever': ['fever', 'high temperature', 'hot', 'warm'],
            'cough': ['cough', 'coughing', 'dry cough'],
            'headache': ['headache', 'head pain', 'migraine'],
            'fatigue': ['tired', 'fatigue', 'exhausted', 'weak'],
            'nausea': ['nausea', 'queasy', 'sick stomach'],
            'vomiting': ['vomit', 'throwing up'],
            'diarrhea': ['diarrhea', 'loose stool'],
            'chest pain': ['chest pain', 'chest pressure'],
            'difficulty breathing': ['difficulty breathing', 'shortness breath'],
            'sore throat': ['sore throat', 'scratchy throat'],
            'runny nose': ['runny nose', 'stuffy nose', 'congestion'],
            'body aches': ['body aches', 'muscle pain', 'joint pain']
        }
        
        self.treatment_advice = {
            'fever': 'Monitor temperature, stay hydrated, rest. Take acetaminophen or ibuprofen if fever >101°F.',
            'cough': 'Stay hydrated, use honey (adults), rest. Consider cough suppressants for dry cough.',
            'headache': 'Rest in dark room, stay hydrated, apply cold compress. Take OTC pain relievers.',
            'fatigue': 'Get adequate sleep (7-9 hours), rest when needed, stay hydrated.',
            'nausea': 'Eat bland foods (crackers, toast), sip clear fluids, avoid strong odors.',
            'vomiting': 'Stop eating solids, sip water/electrolytes, rest stomach.',
            'diarrhea': 'Stay hydrated with ORS, eat BRAT diet, avoid dairy.',
            'chest pain': '⚠️ SEEK IMMEDIATE MEDICAL ATTENTION',
            'difficulty breathing': '⚠️ CALL EMERGENCY SERVICES',
            'sore throat': 'Gargle warm salt water, drink warm tea with honey.',
            'runny nose': 'Use saline spray, humidifier, stay hydrated.',
            'body aches': 'Rest, gentle stretching, warm baths, take NSAIDs.'
        }
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from user input"""
        text_lower = text.lower()
        detected = []
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(symptom)
                    break
        
        return list(set(detected))
    
    def check_emergency(self, symptoms: List[str]) -> bool:
        """Check if symptoms require emergency care"""
        emergency_symptoms = ['chest pain', 'difficulty breathing']
        return any(s in emergency_symptoms for s in symptoms)
    
    def generate_response(self, user_input: str, location_info: Dict = None) -> Dict:
        """Generate medical response with location-based recommendations"""
        
        # Extract symptoms
        symptoms = self.extract_symptoms(user_input)
        
        # Check for emergency
        is_emergency = self.check_emergency(symptoms)
        
        if is_emergency:
            response = {
                'type': 'emergency',
                'message': """🚨 **MEDICAL EMERGENCY DETECTED** 🚨

**⚠️ PLEASE CALL EMERGENCY SERVICES (911) IMMEDIATELY!**

Do not wait. These symptoms require urgent medical attention.

**What to do:**
1. Call 911 or your local emergency number
2. Tell them your symptoms and location
3. Stay calm and wait for help
4. Do not drive yourself to the hospital

**Emergency services will guide you on what to do next.**""",
                'symptoms': symptoms,
                'needs_emergency_care': True
            }
            
            # Add nearest hospital info if location available
            if location_info and location_info.get('nearby_hospitals'):
                nearest = location_info['nearby_hospitals'][0]
                response['message'] += f"\n\n**📍 Nearest Hospital:**\n{nearest['name']} ({nearest['distance_km']} km away)"
            
            return response
        
        # Build normal response
        response_parts = []
        
        # Empathetic opening
        openings = [
            "Thank you for sharing that with me. 💙",
            "I understand how you're feeling.",
            "I appreciate you telling me about your symptoms."
        ]
        response_parts.append(random.choice(openings))
        
        if symptoms:
            response_parts.append(f"\n📋 **Symptoms detected:** {', '.join(symptoms)}")
            
            # Provide treatment advice
            response_parts.append("\n💊 **Treatment advice:**")
            for symptom in symptoms[:4]:
                if symptom in self.treatment_advice:
                    response_parts.append(f"• **{symptom.title()}:** {self.treatment_advice[symptom]}")
            
            # General recommendations
            response_parts.append("\n✅ **Recommendations:**")
            response_parts.append("• Get plenty of rest (7-9 hours)")
            response_parts.append("• Stay hydrated with water and electrolytes")
            response_parts.append("• Eat light, nutritious foods")
            response_parts.append("• Monitor your symptoms")
            
            # When to see a doctor
            response_parts.append("\n🏥 **When to see a doctor:**")
            response_parts.append("• Fever >103°F for more than 3 days")
            response_parts.append("• Symptoms lasting more than 7-10 days")
            response_parts.append("• Worsening symptoms instead of improving")
            
            # Location-based recommendation
            if location_info and location_info.get('nearby_hospitals'):
                response_parts.append(f"\n📍 **Nearby Medical Facilities:**")
                for hospital in location_info['nearby_hospitals'][:3]:
                    response_parts.append(f"• {hospital['badge']} **{hospital['name']}** - {hospital['distance_km']} km away")
        else:
            response_parts.append("\n📋 Could you please provide more details about your symptoms?")
            response_parts.append("\nFor example:")
            response_parts.append("• What specific symptoms are you experiencing?")
            response_parts.append("• How long have you had them?")
            response_parts.append("• How severe are they?")
        
        # Disclaimer
        response_parts.append("\n---\n*⚠️ I'm an AI assistant. This information is for educational purposes. Always consult a healthcare provider for medical advice.*")
        
        return {
            'type': 'normal',
            'message': '\n'.join(response_parts),
            'symptoms': symptoms,
            'needs_emergency_care': False
        }

# ============================================
# SESSION STATE
# ============================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'bot' not in st.session_state:
    st.session_state.bot = MedicalChatbot()
if 'location_service' not in st.session_state:
    st.session_state.location_service = LocationService()
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'nearby_facilities' not in st.session_state:
    st.session_state.nearby_facilities = []
if 'location_shared' not in st.session_state:
    st.session_state.location_shared = False

# ============================================
# HEADER
# ============================================

st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h1 style="color: white;">🏥 MediAI Pro</h1>
    <p style="color: white;">Medical Assistant with Real-time Hospital Locator</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - LOCATION & HOSPITALS
# ============================================

with st.sidebar:
    st.markdown("## 📍 Location Services")
    
    # Location buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📍 Get My Location", use_container_width=True):
            with st.spinner("Getting your location..."):
                # Try browser geolocation first
                try:
                    from streamlit_js_eval import get_geolocation
                    location = get_geolocation()
                    if location and 'coords' in location:
                        st.session_state.user_location = {
                            'lat': location['coords']['latitude'],
                            'lon': location['coords']['longitude'],
                            'source': 'browser'
                        }
                        st.success("Location detected via browser!")
                    else:
                        # Fallback to IP-based location
                        ip_location = st.session_state.location_service.get_location_from_ip()
                        if ip_location:
                            st.session_state.user_location = ip_location
                            st.session_state.user_location['source'] = 'ip'
                            st.info(f"Location: {ip_location.get('city', 'Unknown')}")
                except:
                    # Fallback to IP-based location
                    ip_location = st.session_state.location_service.get_location_from_ip()
                    if ip_location:
                        st.session_state.user_location = ip_location
                        st.session_state.user_location['source'] = 'ip'
                        st.info(f"Location: {ip_location.get('city', 'Unknown')}")
                
                if st.session_state.user_location:
                    st.session_state.location_shared = True
                    st.rerun()
    
    with col2:
        if st.button("🗺️ Manual Location", use_container_width=True):
            st.session_state.location_shared = False
            st.session_state.user_location = None
            st.rerun()
    
    # Manual location input
    if not st.session_state.location_shared:
        st.markdown("### Enter location manually:")
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude", value=0.0, format="%.4f")
        with col2:
            manual_lon = st.number_input("Longitude", value=0.0, format="%.4f")
        
        if st.button("Set Manual Location", use_container_width=True):
            if manual_lat != 0 or manual_lon != 0:
                st.session_state.user_location = {
                    'lat': manual_lat,
                    'lon': manual_lon,
                    'source': 'manual'
                }
                st.session_state.location_shared = True
                st.rerun()
    
    # Display location and find hospitals
    if st.session_state.user_location and st.session_state.location_shared:
        loc = st.session_state.user_location
        
        st.markdown(f"""
        <div class="location-box">
            📍 <strong>Your Location</strong><br>
            Lat: {loc['lat']:.4f}<br>
            Lon: {loc['lon']:.4f}<br>
            Source: {loc.get('source', 'unknown')}
        </div>
        """, unsafe_allow_html=True)
        
        # Find nearby hospitals button
        if st.button("🔍 Find Nearby Hospitals & Clinics", type="primary", use_container_width=True):
            with st.spinner("Searching for nearby medical facilities..."):
                radius = st.slider("Search radius (km)", 1, 20, 5)
                st.session_state.nearby_facilities = st.session_state.location_service.get_nearby_hospitals(
                    loc['lat'], loc['lon'], radius
                )
                
                if st.session_state.nearby_facilities:
                    st.success(f"Found {len(st.session_state.nearby_facilities)} facilities within {radius}km")
                else:
                    st.warning("No facilities found. Try increasing search radius.")
        
        # Display nearby hospitals
        if st.session_state.nearby_facilities:
            st.markdown("### 🏥 Nearby Medical Facilities")
            
            for facility in st.session_state.nearby_facilities:
                badge_class = "emergency-badge" if facility['type'] == 'hospital' else "clinic-badge"
                badge_text = "🏥 HOSPITAL" if facility['type'] == 'hospital' else "🏪 CLINIC"
                
                st.markdown(f"""
                <div class="hospital-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{facility['badge']} {facility['name']}</strong>
                            <span class="{badge_class}" style="margin-left: 10px;">{badge_text}</span>
                        </div>
                        <span class="distance-badge">📍 {facility['distance_km']} km</span>
                    </div>
                    <div style="margin-top: 10px; font-size: 14px; color: #666;">
                        📍 {facility['address']}<br>
                        📞 Phone: {facility['phone']}<br>
                        🕐 Hours: {facility['opening_hours']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Google Maps link
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <a href="https://www.google.com/maps/search/hospitals+clinics/@{loc['lat']},{loc['lon']},12z" 
                   target="_blank" style="text-decoration: none;">
                    <button style="background: #2196F3; color: white; border: none; padding: 10px 20px; 
                                   border-radius: 25px; cursor: pointer;">
                        🗺️ View on Google Maps
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚨 Emergency Info")
    st.info("""
    **Emergency Numbers:**
    - 🇺🇸 USA: **911**
    - 🇬🇧 UK: **999**
    - 🇮🇳 India: **102** or **108**
    - 🇪🇺 EU: **112**
    """)

# ============================================
# MAIN CHAT INTERFACE
# ============================================

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

# Quick questions
st.markdown("### 💡 Quick Questions")
cols = st.columns(4)
questions = [
    ("🤒 Fever", "I have a fever of 101°F and chills"),
    ("🤕 Headache", "I have a severe headache for 2 days"),
    ("😷 Cold", "I have cough, runny nose, and sore throat"),
    ("🏥 Near me", "Find nearest hospital")
]

for i, (label, text) in enumerate(questions):
    with cols[i]:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": text})
            
            with st.spinner("Analyzing..."):
                location_info = None
                if st.session_state.user_location and st.session_state.nearby_facilities:
                    location_info = {'nearby_hospitals': st.session_state.nearby_facilities}
                
                result = st.session_state.bot.generate_response(text, location_info)
                st.session_state.messages.append({"role": "assistant", "content": result['message']})
            st.rerun()

# User input
st.markdown("---")
user_input = st.text_area(
    "",
    placeholder="Describe your symptoms or ask for hospital locations...",
    height=80,
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    send = st.button("📤 Send", type="primary", use_container_width=True)

if send and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("🧠 Analyzing..."):
        # Prepare location info for response
        location_info = None
        if st.session_state.user_location and st.session_state.nearby_facilities:
            location_info = {'nearby_hospitals': st.session_state.nearby_facilities}
        
        result = st.session_state.bot.generate_response(user_input, location_info)
        st.session_state.messages.append({"role": "assistant", "content": result['message']})
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; font-size: 0.8em;">
    <p>⚡ Powered by AI | 🏥 Real-time Hospital Locator | 📍 Privacy-focused location services</p>
    <p>For emergencies, call your local emergency number immediately</p>
</div>
""", unsafe_allow_html=True)
