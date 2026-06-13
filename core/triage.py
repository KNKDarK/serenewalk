from typing import Dict, List, Tuple, Optional
from i18n.translator import t
import streamlit as st

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "severe bleeding", "heart attack",
    "stroke", "unconscious", "ఛాతీ నొప్పి", "శ్వాసకోశ సమస్య", "తీవ్ర రక్తస్రావం",
    "గుండెపోటు", "స్ట్రోక్", "స్పృహ కోల్పోవడం",
    "सीने में दर्द", "सांस लेने में कठिनाई", "गंभीर रक्तस्राव",
    "दिल का दौरा", "स्ट्रोक", "बेहोश",
    "胸の痛み", "呼吸困難", "激しい出血", "心臓発作", "脳卒中", "意識不明",
    "cancer", "hiv", "aids", "tumor", "malignancy", "కర్కాటక వ్యాధి", "హెచ్ఐవి", "ఎయిడ్స్", "कैंसर", "एचआईवी", "एड्स", "癌", "エイズ"
]

URGENT_KEYWORDS = [
    "severe pain", "high fever", "vomiting blood", "unable to eat",
    "confusion", "dehydration",
    "తీవ్ర నొప్పి", "అధిక జ్వరం", "రక్తం వాంతి", "తినలేకపోవడం",
    "గందరగోళం", "నిర్జలీకరణ",
    "गंभीर दर्द", "तेज़ बुखार", "खून की उल्टी", "खा नहीं पा रहे",
    "भ्रम", "निर्जलीकरण",
    "激しい痛み", "高熱", "吐血", "食事ができない", "錯乱", "脱水"
]

SYMPTOM_KEYWORDS = {
    "emergency": [
        "chest pain", "difficulty breathing", "severe bleeding", "heart attack",
        "stroke", "unconscious",
        "ఛాతీ నొప్పి", "శ్వాసకోశ సమస్య", "తీవ్ర రక్తస్రావం", "గుండెపోటు",
        "सीने में दर्द", "सांस लेने में कठिनाई", "गंभीर रक्तस्राव", "दिल का दौरा",
        "胸の痛み", "呼吸困難", "激しい出血", "心臓発作",
        "cancer", "hiv", "aids", "tumor", "malignancy", "కర్కాటక వ్యాధి", "హెచ్ఐవి", "ఎయిడ్స్", "कैंसर", "एचआईवी", "एड्स", "癌", "腫瘍", "エイズ"
    ],
    "high": [
        "high fever", "severe pain", "vomiting blood", "dehydration", "confusion",
        "అధిక జ్వరం", "తీవ్ర నొప్పి", "రక్తం వాంతి", "నిర్జలీకరణ",
        "तेज़ बुखार", "गंभीर दर्द", "खून की उल्टी", "निर्जलीकरण",
        "高熱", "激しい痛み", "吐血", "脱水", "錯乱",
        "diabetes", "blood sugar", "insulin", "మధుమేహం", "చక్కెర వ్యాధి", "मधुमेह", "शुगर", "糖尿病", "インスリン"
    ],
    "moderate": [
        "fever", "cough", "headache", "nausea", "fatigue", "body aches",
        "జ్వరం", "దగ్గు", "తలనొప్పి", "వాంతులు", "అలసట",
        "बुखार", "खांसी", "सिरदर्द", "जी मिचलाना", "थकान",
        "発熱", "咳", "頭痛", "吐き気", "倦怠感", "筋肉痛"
    ],
    "low": [
        "runny nose", "slight cough", "mild headache", "sore throat", "sneezing",
        "జలుబు", "చిన్న దగ్గు", "తేలికయిన తలనొప్పి", "గొంతు నొప్పి",
        "जुकाम", "हल्की खांसी", "हल्का सिरदर्द", "गले में खराश",
        "鼻水", "軽い咳", "軽い頭痛", "喉の痛み", "くしゃみ"
    ]
}

ADVICE_MAP = {
    "emergency": {
        "action_key": "advice_messages.emergency",
        "time": "Immediate",
        "time_te": "వెంటనే",
        "time_hi": "तुरंत",
        "time_ja": "直ちに"
    },
    "high": {
        "action_key": "advice_messages.high",
        "time": "Within 24 hours",
        "time_te": "24 గంటల్లో",
        "time_hi": "24 घंटे के अंदर",
        "time_ja": "24時間以内"
    },
    "moderate": {
        "action_key": "advice_messages.moderate",
        "time": "2-3 days",
        "time_te": "2-3 రోజులు",
        "time_hi": "2-3 दिन",
        "time_ja": "2-3日"
    },
    "low": {
        "action_key": "advice_messages.low",
        "time": "As needed",
        "time_te": "అవసరమైనప్పుడు",
        "time_hi": "आवश्यकता अनुसार",
        "time_ja": "必要に応じて"
    }
}

DOCTOR_ADVICE = {
    "en": "Consult a doctor if symptoms persist or worsen.",
    "te": "లక్షణాలు కొనసాగితే లేదా మరింత తీవ్రమైతే డాక్టర్‌ను సంప్రదించండి.",
    "hi": "यदि लक्षण बने रहते हैं या बिगड़ते हैं तो डॉक्टर से परामर्श करें।",
    "ja": "症状が続く場合や悪化する場合は、医師に相談してください。"
}


def detect_emergency_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    return [kw for kw in EMERGENCY_KEYWORDS if kw in text_lower]


def extract_symptoms(text: str) -> List[str]:
    text_lower = text.lower()
    detected = []
    for category, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(keyword)
    return list(set(detected))


def classify_severity(symptoms: List[str]) -> Tuple[str, float]:
    severity_levels = ["emergency", "high", "moderate", "low"]
    best_level = "low"
    best_score = 0

    for level in severity_levels:
        score = sum(1 for s in symptoms if s in SYMPTOM_KEYWORDS[level])
        if score > best_score:
            best_score = score
            best_level = level

    confidence = min(0.95, best_score / max(1, len(symptoms)) + 0.3)
    return best_level, confidence


def get_advice(severity: str, lang: str = "en") -> Dict:
    advice = ADVICE_MAP.get(severity, ADVICE_MAP["low"])
    return {
        "action": t(advice["action_key"]),
        "timeframe": advice.get(f"time_{lang}", advice["time"]),
        "doctor_advice": DOCTOR_ADVICE.get(lang, DOCTOR_ADVICE["en"])
    }


@st.cache_data
def triage(text: str, lang: str = "en") -> Dict:
    emergency = detect_emergency_keywords(text)
    if emergency:
        timeframe = "Immediate"
        if lang == "te": timeframe = "వెంటనే"
        elif lang == "hi": timeframe = "तुरंत"
        elif lang == "ja": timeframe = "直ちに"
        
        return {
            "triage_level": "EMERGENCY",
            "is_emergency": True,
            "symptoms": emergency,
            "confidence": 1.0,
            "message": t("results.seek_immediate"),
            "action": t("advice_messages.emergency"),
            "timeframe": timeframe
        }

    symptoms = extract_symptoms(text)
    severity, confidence = classify_severity(symptoms)
    advice = get_advice(severity, lang)

    return {
        "triage_level": severity.upper(),
        "is_emergency": severity == "emergency",
        "symptoms": symptoms,
        "confidence": confidence,
        "message": t("advice_messages." + severity),
        "action": advice["action"],
        "timeframe": advice["timeframe"],
        "doctor_advice": advice["doctor_advice"]
    }
