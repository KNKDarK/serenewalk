import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import os
import random
from datetime import datetime

# Try to load LLM
try:
    from llama_cpp import Llama
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False

st.set_page_config(page_title="AI Medical Assistant", page_icon="🤝", layout="wide")

# Custom CSS for human-like chat
st.markdown("""
<style>
.stChatMessage { padding: 20px; border-radius: 15px; margin: 10px 0; }
.human-message { background: linear-gradient(135deg, #667eea 0.assistant-message { background: linear-gradient(135deg, #f5f7fa 0.typing-indicator { display: inline-block; animation: pulse 1.5s infinite; }
@keyframes pulse { 0</style>
""", unsafe_allow_html=True)

# Title with friendly tone
st.title("🤝 Your AI Medical Assistant")
st.caption("I am here to help you with medical information. How are you feeling today?")
st.warning("⚠️ Remember: I am an AI assistant. For emergencies, please call emergency services immediately.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "conversation_style" not in st.session_state:
    st.session_state.conversation_style = "empathetic"

# Friendly greetings
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Load models
@st.cache_resource
def load_models():
    embed = SentenceTransformer("all-MiniLM-L6-v2")
    if os.path.exists("knowledge_base"):
        client = chromadb.PersistentClient(path="knowledge_base")
        try:
            collection = client.get_collection("medical_knowledge")
            return embed, collection
        except:
            return embed, None
    return embed, None

@st.cache_resource
def load_llm():
    if not LLM_AVAILABLE:
        return None
    model_path = "models/tinyllama.Q4_K_M.gguf"
    if os.path.exists(model_path) and os.path.getsize(model_path) > 1000000:
        try:
            return Llama(model_path=model_path, n_ctx=1024, n_threads=2, verbose=False)
        except:
            return None
    return None

# Human-like response generation
def generate_human_response(user_query, context_docs, llm, user_name):
    context = context_docs[0] if context_docs else "No specific medical information found."
    
    # Friendly conversational prompts
    name_context = f"My name is {user_name}. " if user_name else ""
    
    if llm:
        prompt = f"""<|im_start|>system
You are a friendly, empathetic medical assistant named MediBot. You talk like a caring human doctor.
Be warm, compassionate, and conversational. Use phrases like "I understand", "That sounds difficult", "Let me help".
Keep responses concise but caring. Never give harmful advice. Always include medical disclaimers.
Medical knowledge: {context}
<|im_end|>
<|im_start|>user
{name_context}{user_query}
<|im_end|>
<|im_start|>assistant
"""
        try:
            response = llm(prompt, max_tokens=300, temperature=0.7, echo=False)
            return response["choices"][0]["text"].strip()
        except:
            return get_fallback_response(user_query, context_docs, user_name)
    else:
        return get_fallback_response(user_query, context_docs, user_name)

# Fallback responses that sound human
def get_fallback_response(query, context_docs, user_name):
    name_prefix = f"{user_name}, " if user_name else ""
    
    caring_phrases = [
        "I understand how you must be feeling.",
        "Thank you for sharing that with me.",
        "Let me help you understand this better.",
        "I appreciate you telling me about this."
    ]
    
    if context_docs:
        return f"{random.choice(caring_phrases)} {name_prefix}Based on medical information: {context_docs[0][:300]}

Remember, this is general information. Please consult a healthcare provider for personalized care. Take care! 💙"
    else:
        return f"{random.choice(caring_phrases)} {name_prefix}I want to help you, but I don't have specific information about that. Could you please describe your symptoms differently? Or it would be best to consult a doctor who can examine you properly. I hope you feel better soon! 🌟"

# Load resources
with st.spinner("Loading my medical knowledge... 🧠"):
    embed_model, collection = load_models()
    llm = load_llm()

# Sidebar with friendly options
with st.sidebar:
    st.header("👤 About You")
    if not st.session_state.user_name:
        name_input = st.text_input("What should I call you?")
        if name_input:
            st.session_state.user_name = name_input
            st.success(f"Nice to meet you, {name_input}! 💙")
            st.rerun()
    else:
        st.success(f"Hello, {st.session_state.user_name}! 👋")
        if st.button("Change name"):
            st.session_state.user_name = None
            st.rerun()
    
    st.divider()
    st.header("🤖 My Status")
    if collection:
        st.success(f"✅ Medical knowledge: {collection.count()} topics")
    else:
        st.error("⚠️ Knowledge base not ready")
    
    if llm:
        st.success("✅ AI Brain: Active")
    else:
        st.info("📝 AI Brain: Demo mode (still caring!)")
    
    st.divider()
    st.header("💬 Conversation Style")
    style = st.selectbox("How should I talk?", ["Empathetic", "Professional", "Friendly"])
    st.session_state.conversation_style = style.lower()
    
    st.divider()
    st.header("📞 Emergency")
    st.info("If this is an emergency:
Call 911 (USA) or your local emergency number immediately!")

# Display chat history with human-like feel
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input with placeholder
if st.session_state.user_name:
    placeholder = f"How are you feeling today, {st.session_state.user_name}? 😊"
else:
    placeholder = "Tell me how you're feeling... I'm here to listen and help 💙"

prompt = st.chat_input(placeholder)

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            # Retrieve relevant info
            if collection:
                query_embed = embed_model.encode(prompt).tolist()
                results = collection.query(query_embeddings=[query_embed], n_results=1)
                docs = results["documents"][0] if results["documents"] else []
            else:
                docs = []
            
            # Generate human-like response
            response = generate_human_response(prompt, docs, llm, st.session_state.user_name)
            st.markdown(response)
            
            # Add a caring emoji based on context
            if "fever" in prompt.lower() or "pain" in prompt.lower():
                st.caption("💙 Take care, I hope you feel better soon!")
            elif "thank" in prompt.lower():
                st.caption("🌟 You're very welcome! Always here to help.")
            else:
                st.caption("💬 I'm here whenever you need me")
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Clear chat button
if st.sidebar.button("🗑️ Start New Conversation"):
    st.session_state.messages = []
    st.rerun()
