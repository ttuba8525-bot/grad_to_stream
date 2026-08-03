import streamlit as st
from vectorstore import load_documents_into_vectorstore
from rag import respond, clear_chat_history
from prompts import SALES_PROMPTS

st.set_page_config(
    page_title="PragyanAI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 PragyanAI Conversational Sales & FAQ Assistant")
st.write("Ask anything about PragyanAI.")

with st.sidebar:

    persona = st.selectbox(
        "Select Persona",
        list(SALES_PROMPTS.keys())
    )

    uploaded_files = st.file_uploader(
        "Upload PDFs or Excel",
        accept_multiple_files=True,
        type=["pdf","xlsx","xls"]
    )

    if uploaded_files:
        st.success(load_documents_into_vectorstore(uploaded_files))

    if st.button("Clear Memory"):
        clear_chat_history(persona)
        st.success("Chat history cleared.")

if "messages" not in st.session_state:
    st.session_state.messages=[]

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt:=st.chat_input("Ask a question..."):

    st.session_state.messages.append(
        {"role":"user","content":prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    answer=respond(prompt,persona)

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role":"assistant","content":answer}
    )
