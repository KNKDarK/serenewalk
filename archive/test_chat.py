import streamlit as st
st.title("Test Chat")
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
prompt = st.chat_input("Say something")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        st.write("Echo: " + prompt)
        st.session_state.messages.append({"role": "assistant", "content": "Echo: " + prompt})
    st.rerun()
