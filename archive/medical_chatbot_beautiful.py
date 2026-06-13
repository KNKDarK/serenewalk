import streamlit as st
import json
import sqlite3
import hashlib
import re
import time
import random
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
from streamlit.components.v1 import html

# Page config - must be first
st.set_page_config(
    page_title="MediAI - Your Health Companion",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 70%;
        float: right;
        clear: both;
        animation: slideInRight 0.3s ease;
    }
    
    .bot-message {
        background: rgba(255,255,255,0.95);
        color: #333;
        padding: 12px 20px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 70%;
        float: left;
        clear: both;
        animation: slideInLeft 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        background: rgba(255,255,255,0.9);
        padding: 10px 15px;
        border-radius: 20px;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    /* Floating animation for title */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-title {
        animation: float 3s ease-in-out infinite;
        text-align: center;
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: bold;
    }
    
    /* Card effect */
    .card {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .card:hover {
        transform: translateY(-5px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Input field */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #667eea;
        transition: all 0.3s;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #764ba2;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Status indicator */
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
</style>
""", unsafe_allow_html=True)

# ============================================
# MEDICAL AI CLASS
# ============================================

class MedicalChatbot:
    def __init__(self):
        self.symptom_keywords = {
            'emergency': ['chest pain', 'difficulty breathing', 'severe bleeding', 'heart attack', 'stroke'],
            'high': ['high fever', 'severe pain', 'vomiting blood', 'confusion'],
            'moderate': ['fever', 'cough', 'headache', 'nausea', 'fatigue'],
            'low': ['runny nose', 'slight cough', 'sore throat', 'sneezing']
        }
        
        self.responses = {
            'greeting': [
                "Hey there! 👋 I'm MediAI, your health companion. How are you feeling today?",
                "Welcome! 💙 I'm here to listen and help. What's bothering you?",
                "Hello! 🌟 Tell me what's going on, and I'll do my best to help."
            ],
            'emergency': [
                "🚨 **URGENT!** Please call emergency services immediately!",
                "⚠️ **IMPORTANT** - These symptoms require immediate medical attention!",
                "🆘 **EMERGENCY DETECTED** - Seek medical care right away!"
            ],
            'caring': [
                "I understand how you feel. 💙 Let me help you figure this out.",
                "Thank you for sharing with me. I'm here to support you. 🌟",
                "I hear you. That sounds challenging. Let's work through this together. 🤝"
            ]
        }
    
    def extract_symptoms(self, text: str) -> List[str]:
        text_lower = text.lower()
        detected = []
        for category, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(keyword)
        return list(set(detected))
    
    def classify_severity(self, symptoms: List[str]) -> Tuple[str, float]:
        severity_levels = ['emergency', 'high', 'moderate', 'low']
        best_level = 'low'
        best_score = 0
        
        for level in severity_levels:
            score = sum(1 for s in symptoms if s in self.symptom_keywords[level])
            if score > best_score:
                best_score = score
                best_level = level
        
        confidence = min(0.95, best_score / max(1, len(symptoms)) + 0.3)
        return best_level, confidence
    
    def get_response(self, severity: str, symptoms: List[str]) -> str:
        if severity == 'emergency':
            return random.choice(self.responses['emergency'])
        elif not symptoms:
            return "Hmm, could you tell me more about your symptoms? The more details you share, the better I can help! 💙"
        else:
            base = random.choice(self.responses['caring'])
            
            if severity == 'high':
                return f"{base}\n\nBased on what you've shared, these seem quite serious. **Please see a doctor within 24 hours.** 🏥"
            elif severity == 'moderate':
                return f"{base}\n\nFrom what you've described, it appears to be moderate. **Rest up, stay hydrated, and monitor your symptoms.** 💊"
            else:
                return f"{base}\n\nYour symptoms seem mild. **Get plenty of rest, drink fluids, and take OTC remedies if needed.** You should feel better soon! 🌟"
    
    def analyze(self, text: str) -> Dict:
        symptoms = self.extract_symptoms(text)
        severity, confidence = self.classify_severity(symptoms)
        response = self.get_response(severity, symptoms)
        
        return {
            'symptoms': symptoms,
            'severity': severity.upper(),
            'confidence': confidence,
            'response': response,
            'is_emergency': severity == 'emergency'
        }

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.bot = MedicalChatbot()
    st.session_state.conversation_count = 0
    st.session_state.user_name = None

# ============================================
# HEADER SECTION
# ============================================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="floating-title">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center;">🩺 MediAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: white; font-size: 1.2em;">Your Empathetic Health Companion</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# NAME INPUT SECTION
# ============================================

if not st.session_state.user_name:
    st.markdown('<div class="card" style="max-width: 500px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ Welcome! ✨</h3>", unsafe_allow_html=True)
    name = st.text_input("What's your name?", placeholder="Enter your name...", key="name_input")
    
    if st.button("Start Conversation 💬", use_container_width=True):
        if name:
            st.session_state.user_name = name
            welcome_msg = f"🎉 Hi {name}! I'm so glad you're here. How can I help you today?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()
        else:
            st.warning("Please tell me your name first! 😊")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN CHAT INTERFACE
# ============================================

else:
    # Status bar
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.95); padding: 10px; border-radius: 15px; margin: 10px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span class="status-online"></span>
                    <span style="margin-left: 5px;">MediAI is online</span>
                </div>
                <div>
                    <span>👋 Hello, {st.session_state.user_name}!</span>
                </div>
                <div>
                    <span>💬 {len(st.session_state.messages)} messages</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        # Display all messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div style="display: flex; justify-content: flex-end;"><div class="user-message">🙋 {msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="display: flex; justify-content: flex-start;"><div class="bot-message">🤖 {msg["content"]}</div></div>', unsafe_allow_html=True)
    
    # Quick suggestion buttons
    st.markdown("### 💡 Quick Questions")
    col1, col2, col3, col4 = st.columns(4)
    
    suggestions = [
        ("🤒 Fever", "I have a fever"),
        ("🤕 Headache", "I have a headache"),
        ("😷 Cough", "I have a cough"),
        ("❤️ Chest pain", "I have chest pain")
    ]
    
    with col1:
        if st.button(suggestions[0][0], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[0][1]})
            with st.spinner("🧠 Analyzing..."):
                result = st.session_state.bot.analyze(suggestions[0][1])
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            st.rerun()
    
    with col2:
        if st.button(suggestions[1][0], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[1][1]})
            with st.spinner("🧠 Analyzing..."):
                result = st.session_state.bot.analyze(suggestions[1][1])
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            st.rerun()
    
    with col3:
        if st.button(suggestions[2][0], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[2][1]})
            with st.spinner("🧠 Analyzing..."):
                result = st.session_state.bot.analyze(suggestions[2][1])
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            st.rerun()
    
    with col4:
        if st.button(suggestions[3][0], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[3][1]})
            with st.spinner("🧠 Analyzing..."):
                result = st.session_state.bot.analyze(suggestions[3][1])
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            st.rerun()
    
    # Input section
    st.markdown("---")
    user_input = st.text_area(
        "",
        placeholder="💬 Type your message here... (e.g., 'I have a fever and headache for 2 days')",
        height=80,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        send_button = st.button("📤 Send Message", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": f"Chat cleared! How can I help you today, {st.session_state.user_name}? 💙"})
            st.rerun()
    
    # Process user input
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            time.sleep(0.5)  # Simulate thinking
            result = st.session_state.bot.analyze(user_input)
            
            # Add bot response
            st.session_state.messages.append({"role": "assistant", "content": result['response']})
            
            # Add additional info for emergencies
            if result['is_emergency']:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "🆘 **Please call emergency services immediately!** Don't wait - your safety is the priority. 🚑"
                })
        
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; font-size: 0.8em; padding: 20px;">
        <p>💙 Remember: I'm an AI assistant, not a doctor. For emergencies, call emergency services immediately.</p>
        <p>Made with ❤️ for your health and wellbeing</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ANIMATION SCRIPT
# ============================================

html("""
<script>
    // Auto-scroll to bottom of chat
    const scrollToBottom = () => {
        const containers = document.querySelectorAll('.stMarkdown');
        const lastContainer = containers[containers.length - 1];
        if (lastContainer) {
            lastContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    };
    
    // Call on load and after each update
    setTimeout(scrollToBottom, 100);
    setInterval(scrollToBottom, 1000);
</script>
""", height=0)
