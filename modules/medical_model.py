import streamlit as st
import os

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    st.warning("⚠️ AI model library not installed")

@st.cache_resource
def load_model(model_path):
    if not LLAMA_AVAILABLE:
        return None
    if not os.path.exists(model_path):
        st.error(f"Model not found at {model_path}")
        return None
    try:
        llm = Llama(model_path=model_path, n_ctx=512, n_threads=2, verbose=False)
        return llm
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def summarize_symptoms(model_path, user_text):
    llm = load_model(model_path)
    if not llm:
        return "AI model not available"
    prompt = f"Summarize these symptoms briefly: {user_text}\nSummary:"
    try:
        response = llm(prompt, max_tokens=100, temperature=0.2, echo=False)
        return response["choices"][0]["text"].strip()
    except:
        return f"Symptoms: {user_text[:100]}..."

def medical_advice(model_path, symptom_summary, location=None):
    llm = load_model(model_path)
    if not llm:
        return generate_fallback_advice(symptom_summary)
    prompt = f"Give brief medical advice for: {symptom_summary}\nAdvice:"
    try:
        response = llm(prompt, max_tokens=200, temperature=0.3, echo=False)
        return response["choices"][0]["text"].strip()
    except:
        return generate_fallback_advice(symptom_summary)

def generate_fallback_advice(symptoms):
    symptoms_lower = symptoms.lower()
    if "fever" in symptoms_lower:
        return "Rest, stay hydrated, monitor temperature. See doctor if fever persists."
    elif "headache" in symptoms_lower:
        return "Rest in dark room, stay hydrated. Seek care if severe."
    elif "pain" in symptoms_lower:
        return "Rest area, consider OTC pain relievers. Seek care for severe pain."
    else:
        return "Monitor symptoms, rest, stay hydrated. Contact healthcare provider if worsens."
