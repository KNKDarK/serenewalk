import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model settings
    MODEL_PATH = "models/phi-3-mini-4k-instruct-q4_0.gguf"
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0.3))
    MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", 400))
    MODEL_CONTEXT_LENGTH = int(os.getenv("MODEL_CONTEXT_LENGTH", 2048))
    
    # Location services
    SEARCH_RADIUS_KM = float(os.getenv("SEARCH_RADIUS_KM", 5))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", 5))
    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")
    
    # App settings
    APP_TITLE = "AI Medical Advisor"
    APP_ICON = "🩺"
    DISCLAIMER = "⚠️ This AI system is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. In case of emergency, call your local emergency number immediately."
    
    # Medical disclaimer for advice generation
    DISCLAIMER_SHORT = "IMPORTANT: This is AI-generated advice only. Consult a doctor for proper medical care."
