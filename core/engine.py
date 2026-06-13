import os
import json
from typing import Dict, List, Optional, Tuple
from core.triage import triage, extract_symptoms, classify_severity, EMERGENCY_KEYWORDS, SYMPTOM_KEYWORDS
from i18n.translator import t, get_current_language

try:
    from core.knowledge import KnowledgeBase
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

import streamlit as st

@st.cache_resource
def get_medical_engine(model_path: Optional[str] = None, kb_path: str = "data/kb"):
    return MedicalEngine(model_path=model_path, kb_path=kb_path)


class MedicalEngine:
    def __init__(self, model_path: Optional[str] = None, kb_path: str = "data/kb"):
        self.model_path = model_path or os.getenv("MODEL_PATH", "models/medical-model.bin")
        self.kb = None
        self.llm = None

        if KB_AVAILABLE:
            try:
                self.kb = KnowledgeBase(path=kb_path)
            except Exception:
                self.kb = None

        if LLAMA_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=512, n_threads=2, verbose=False)
            except Exception:
                self.llm = None

    def _retrieve_context(self, query: str) -> List[str]:
        if self.kb:
            try:
                return self.kb.retrieve(query, n_results=2)
            except Exception:
                return []
        return []

    def _llm_inference(self, prompt: str) -> Optional[str]:
        if self.llm:
            try:
                response = self.llm(prompt, max_tokens=200, temperature=0.3, echo=False)
                return response["choices"][0]["text"].strip()
            except Exception:
                return None
        return None

    def _fallback_advice(self, symptoms: List[str], lang: str = "en") -> str:
        symptom_text = ", ".join(symptoms) if symptoms else t("advice_messages.your_symptoms")
        return t("advice_messages.rest_hydrate") + f" ({symptom_text})"

    def analyze(self, text: str, lang: Optional[str] = None) -> Dict:
        lang = lang or get_current_language()
        triage_result = triage(text, lang)

        context = self._retrieve_context(text)
        kb_advice = None
        if context:
            kb_advice = context[0]

        llm_advice = None
        if self.llm:
            symptoms = extract_symptoms(text)
            prompt = f"Provide brief medical advice for these symptoms: {', '.join(symptoms)}\nAdvice:"
            llm_advice = self._llm_inference(prompt)

        symptoms = extract_symptoms(text)
        severity, confidence = classify_severity(symptoms)
        fallback = self._fallback_advice(symptoms, lang)

        final_advice = kb_advice or llm_advice or fallback

        return {
            "text": text,
            "triage_level": triage_result["triage_level"],
            "is_emergency": triage_result["is_emergency"],
            "symptoms": symptoms,
            "confidence": confidence,
            "message": triage_result["message"],
            "action": triage_result["action"],
            "timeframe": triage_result["timeframe"],
            "doctor_advice": triage_result.get("doctor_advice", ""),
            "advice": final_advice,
            "context_source": "KB" if kb_advice else ("LLM" if llm_advice else "Fallback"),
            "kb_context": context
        }

    def get_status(self) -> Dict:
        return {
            "kb_available": self.kb is not None,
            "llm_available": self.llm is not None,
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path)
        }
