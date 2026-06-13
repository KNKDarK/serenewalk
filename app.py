import streamlit as st
import sys
import os
import functools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n.translator import t, translator, set_language, get_current_language
from core.triage import triage
from core.engine import MedicalEngine, get_medical_engine

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get shared medical engine
engine = get_medical_engine()
st.session_state.engine = engine

# Ensure translator is synced with session state
lang = st.session_state.get("language", "en")
translator.set_language(lang)

# Get current language - must be done AFTER syncing translator
current_lang = get_current_language()

# Page config - uses current language
st.set_page_config(
    page_title=t("app.title"),
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;700&family=Noto+Sans+Devanagari:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Inter:wght@400;700&family=Noto+Color+Emoji&display=swap');

/* ISOLATION SHIELD - Target only specific text areas to protect icons */

/* 1. Main Content Markdown and Custom UI */
.stMarkdown p, .stMarkdown li, .stMarkdown label,
.stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricLabel"],
.emergency-banner, .emergency-header, .result-card, .card-title {
    font-family: 'Inter', 'Noto Sans Telugu', 'Noto Sans Devanagari', 'Noto Sans JP', sans-serif !important;
}

/* 2. Text Inputs and Buttons */
.stTextArea textarea, .stTextInput input, .stButton button div {
    font-family: 'Inter', 'Noto Sans Telugu', 'Noto Sans Devanagari', 'Noto Sans JP', sans-serif !important;
}

/* 3. ABSOLUTE CHROME PROTECTION - Force native fonts for Streamlit UI "Chrome" */
/* We explicitly exclude headers, the sidebar toggle, and expander headers */
[data-testid="stHeader"], 
[data-testid="stSidebarNav"], 
[data-testid="stSidebar"] [role="button"],
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [role="button"] {
    font-family: var(--st-font-family, "Source Sans Pro", sans-serif) !important;
}

/* 4. TOTAL ICON RESTORATION - High specificity override for all possible icons */
[data-testid*="Icon"], [data-testid="stIcon"], svg, i, [aria-hidden="true"],
summary span[aria-hidden="true"], [role="button"] span {
    font-family: 'streamlit-icons' !important;
    text-transform: none !important;
    font-variant-ligatures: common-ligatures !important;
}

/* Premium UI Styles */
.main {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #1A1C24;
}

/* Emergency Banner */
.emergency-banner {
    background: linear-gradient(90deg, #FF4B4B 0%, #FF6B35 100%);
    color: white;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(255, 75, 75, 0.3);
    position: relative;
    overflow: hidden;
}

.emergency-banner::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { left: -100%; }
    100% { left: 100%; }
}

.emergency-header {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
}

.siren-icon {
    font-size: 32px;
    margin-right: 16px;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
}

/* Result Cards */
.result-card {
    background-color: #262730;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #36393F;
    height: 100%;
    transition: transform 0.2s;
}

.result-card:hover {
    transform: translateY(-4px);
    border-color: #FF6B35;
}

.card-title {
    color: #FF6B35;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
}

.card-icon {
    margin-right: 10px;
}

/* Fix for placeholders */
::placeholder {
    font-family: 'Inter', 'Noto Sans Telugu', 'Noto Sans Devanagari', 'Noto Sans JP', 'Noto Color Emoji', sans-serif !important;
    opacity: 0.7;
}

/* General Layout Refinement */
.stButton button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<a href="#main-content" class="skip-link">' + t("accessibility.skip_to_content") + '</a>', unsafe_allow_html=True)

# Main Content
st.markdown(f'<div id="main-content" role="main">', unsafe_allow_html=True)

st.title(t("app.title"))
st.markdown(f"**{t('app.subtitle')}**")

st.warning(t("app.emergency_warning"))

# Language selector toggle in sidebar
st.sidebar.markdown(f"**{t('app.language_label')}**")
row1 = st.sidebar.columns(2)
with row1[0]:
    if st.button("EN", use_container_width=True, type="primary" if current_lang == "en" else "secondary"):
        set_language("en")
        st.session_state.language = "en"
        st.rerun()
with row1[1]:
    if st.button("తెలుగు", use_container_width=True, type="primary" if current_lang == "te" else "secondary"):
        set_language("te")
        st.session_state.language = "te"
        st.rerun()

row2 = st.sidebar.columns(2)
with row2[0]:
    if st.button("हिन्दी", use_container_width=True, type="primary" if current_lang == "hi" else "secondary"):
        set_language("hi")
        st.session_state.language = "hi"
        st.rerun()
with row2[1]:
    if st.button("日本語", use_container_width=True, type="primary" if current_lang == "ja" else "secondary"):
        set_language("ja")
        st.session_state.language = "ja"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header(t("app.sidebar.emergency_numbers"))
st.sidebar.markdown("""
- 🇺🇸 USA: **911**
- 🇬🇧 UK: **999**
- 🇪🇺 EU: **112**
- 🇮🇳 India: **102** / **108**
""")

st.sidebar.header(t("app.sidebar.when_to_seek_emergency"))
emergency_symptoms = {
    "en": [
        "Chest pain or pressure",
        "Difficulty breathing",
        "Sudden severe headache",
        "Loss of consciousness",
        "Severe bleeding",
        "Sudden confusion or weakness"
    ],
    "te": [
        "ఛాతీ నొప్పి లేదా ఒత్తిడి",
        "శ్వాస తీసుకోవడంలో ఇబ్బంది",
        "అకస్మాత్తుగా తీవ్ర తలనొప్పి",
        "స్పృహ కోల్పోవడం",
        "తీవ్ర రక్తస్రావం",
        "అకస్మాత్తుగా గందరగోళం లేదా బలహీనత"
    ],
    "hi": [
        "सीने में दर्द या दबाव",
        "सांस लेने में कठिनाई",
        "अचानक तेज सिरदर्द",
        "बेहोशी",
        "गंभीर रक्तस्राव",
        "अचानक भ्रम या कमजोरी"
    ],
    "ja": [
        "胸の痛みや圧迫感",
        "呼吸困難",
        "突然の激しい頭痛",
        "意識消失",
        "激しい出血",
        "突然の混乱や脱力"
    ]
}

for symptom in emergency_symptoms.get(current_lang, emergency_symptoms["en"]):
    st.sidebar.markdown(f"- {symptom}")

st.sidebar.markdown("---")
st.sidebar.header(t("app.sidebar.system_status"))

status = st.session_state.engine.get_status()
if status["kb_available"]:
    st.sidebar.success("✅ " + t("app.sidebar.kb_ready"))
else:
    st.sidebar.warning("⚠️ " + t("app.sidebar.kb_not_ready"))

if st.sidebar.button(t("app.sidebar.clear_chat"), use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# Medical Translator in sidebar
st.sidebar.markdown("---")
st.sidebar.header(t("translator.header"))
trans_input = st.sidebar.text_area(t("translator.input_label"), height=100, key="trans_input")
if st.sidebar.button(t("translator.translate_button"), use_container_width=True):
    if trans_input:
        # Simple translation logic for common symptoms if LLM is not available
        # In a real app, this would call an API or the LLM
        translation_result = st.session_state.engine.analyze(trans_input, lang=current_lang)
        st.sidebar.info(f"**{t('translator.result_label')}:**\n\n{translation_result['advice']}")
    else:
        st.sidebar.warning(t("translator.input_label"))

# Clear sidebar
st.sidebar.markdown('', unsafe_allow_html=True)

st.markdown("---")

# Symptoms input
create_accessible_header = lambda text, level=1: st.markdown(f'<h{level} role="heading">{text}</h{level}>', unsafe_allow_html=True)

create_accessible_header(t("symptoms.header"), level=2)

user_input = st.text_area(
    t("symptoms.input_label"),
    height=150,
    placeholder=t("symptoms.placeholder"),
    label_visibility="visible"
)

col1, col2 = st.columns([1, 4])
with col1:
    analyze_clicked = st.button(t("symptoms.analyze_button"), type="primary", use_container_width=True)

if analyze_clicked and user_input:
    with st.spinner(t("symptoms.analyzing")):
        result = st.session_state.engine.analyze(user_input, lang=current_lang)
        st.session_state.chat_history.append({
            "symptoms": user_input,
            "result": result,
            "time": __import__("datetime").datetime.now().strftime("%H:%M:%S")
        })

    if result["is_emergency"]:
        st.markdown(f"""
            <div class="emergency-banner">
                <div class="emergency-header">
                    <span class="siren-icon">🚨</span> {t('results.emergency_action')}
                </div>
                <div>{result['action']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        severity = result["triage_level"].lower()
        severity_icons = {"high": "🔴", "moderate": "🟡", "low": "🟢"}
        icon = severity_icons.get(severity, "ℹ️")
        st.success(f"{icon} {t('results.severity_label')}: **{result['triage_level']}**")

    st.markdown("---")
    
    # Custom Card Layout for Results
    col_cards = st.columns(2)
    
    with col_cards[0]:
        st.markdown(f"""
            <div class="result-card">
                <div class="card-title"><span class="card-icon">🔍</span> {t('results.symptoms_found')}</div>
                <div style="font-size: 24px; font-weight: 800; margin-bottom: 8px;">{len(result["symptoms"])}</div>
                <div style="color: #888;">{", ".join(result["symptoms"]) if result["symptoms"] else t('advice_messages.your_symptoms')}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_cards[1]:
        st.markdown(f"""
            <div class="result-card">
                <div class="card-title"><span class="card-icon">⚡</span> {t('results.confidence')}</div>
                <div style="font-size: 24px; font-weight: 800; margin-bottom: 8px;">{result['confidence']*100:.1f}%</div>
                <div style="color: #888;">{t('accessibility.analysis_result')}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Advice Section
    if not result["is_emergency"]:
        st.info(f"**{t('results.advice')}:** {result['advice']}")

    col_info = st.columns(2)
    with col_info[0]:
        if result.get("timeframe"):
            st.info(f"**{t('results.timeframe')}:** {result['timeframe']}")
    with col_info[1]:
        if result.get("doctor_advice"):
            st.info(f"**{t('results.when_to_see_doctor')}:** {result['doctor_advice']}")

elif analyze_clicked and not user_input:
    st.warning(t("symptoms.input_label"))

if st.session_state.chat_history:
    st.markdown("---")
    create_accessible_header(t("app.history"), level=2)

    for chat in reversed(st.session_state.chat_history[-3:]):
        expander_title = t("app.history_entry", time=chat['time'])
        with st.expander(expander_title):
            st.markdown(f"**{t('symptoms.header')}:** {chat['symptoms']}")
            result = chat.get("result", {})
            if result:
                st.markdown(f"**{t('results.severity_label')}:** {result.get('triage_level', 'N/A')}")
                st.markdown(f"**{t('results.advice')}:** {result.get('advice', 'N/A')}")

st.markdown('</div>', unsafe_allow_html=True)

st.caption(f"{t('app.title')} | {t('app.subtitle')}")
