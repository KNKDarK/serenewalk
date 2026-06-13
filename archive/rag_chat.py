import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import os

st.set_page_config(page_title="RAG Medical Advisor", layout="wide")
st.title("RAG Medical Advisor")
st.warning("For informational purposes only")

if "messages" not in st.session_state:
    st.session_state.messages = []

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

embed_model, collection = load_models()

with st.sidebar:
    if collection:
        st.success("Ready")
    else:
        st.error("Run: python3 build_kb.py")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Describe your symptoms...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if collection:
            query_embed = embed_model.encode(prompt).tolist()
            results = collection.query(query_embeddings=[query_embed], n_results=1)
            if results["documents"] and results["documents"][0]:
                answer = results["documents"][0][0]
            else:
                answer = "No match found. Please consult a doctor."
        else:
            answer = "System not ready. Please run build_kb.py first."
        
        st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if st.sidebar.button("Clear"):
    st.session_state.messages = []
    st.rerun()
    # Add to rag_chat.py after retrieval
