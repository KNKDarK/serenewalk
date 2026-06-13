import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import os

st.set_page_config(page_title="RAG Medical Advisor", layout="wide")
st.title("RAG Medical Advisor")
st.warning("For informational purposes only. Emergency: Call emergency services.")

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_vector_db():
    if os.path.exists("knowledge_base"):
        client = chromadb.PersistentClient(path="knowledge_base")
        try:
            return client.get_collection("medical_knowledge")
        except:
            return None
    return None

def retrieve_info(query, collection, embed_model):
    if not collection:
        return []
    query_embedding = embed_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    return results["documents"][0] if results["documents"] else []

embed_model = load_embedding_model()
collection = load_vector_db()

with st.sidebar:
    st.header("Status")
    if collection:
        st.success("Ready")
    else:
        st.error("Run: python3 build_knowledge_base.py")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a medical question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            docs = retrieve_info(prompt, collection, embed_model)
        if docs:
            response = docs[0]
        else:
            response = "No information found. Please consult a doctor."
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("Clear"):
    st.session_state.messages = []
    st.rerun()
