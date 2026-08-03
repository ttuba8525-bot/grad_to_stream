import streamlit as st
import tempfile
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

from vectorstore import load_documents_into_vectorstore
from rag import respond, clear_chat_history
from prompts import SALES_PROMPTS

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------

st.set_page_config(
    page_title="PragyanAI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------------

load_documents_into_vectorstore()

# --------------------------------------------------------
# TITLE
# --------------------------------------------------------

st.title("🤖 PragyanAI Conversational Sales & FAQ Assistant")
st.write("Ask anything about PragyanAI.")

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------

with st.sidebar:

    st.header("Settings")

    persona = st.selectbox(
        "Select Persona",
        list(SALES_PROMPTS.keys())
    )

    uploaded_files = st.file_uploader(
        "Upload PDFs or Excel",
        accept_multiple_files=True,
        type=["pdf", "xlsx", "xls"]
    )

    if uploaded_files:
        msg = load_documents_into_vectorstore(uploaded_files)
        st.success(msg)

    if st.button("🗑 Clear Memory"):
        clear_chat_history(persona)
        st.session_state.messages = []
        st.success("Chat history cleared.")

# --------------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# VOICE INPUT
# --------------------------------------------------------

st.markdown("### 🎤 Voice Input")

audio = mic_recorder(
    start_prompt="🎙 Start Recording",
    stop_prompt="⏹ Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice"
)

voice_prompt = ""

if audio:

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio["bytes"])
        temp_audio = f.name

    try:

        with sr.AudioFile(temp_audio) as source:
            audio_data = recognizer.record(source)

        voice_prompt = recognizer.recognize_google(audio_data)

        st.success(f"🎤 You said: {voice_prompt}")

    except Exception as e:
        st.error(f"Speech Recognition Error: {e}")

# --------------------------------------------------------
# TEXT INPUT
# --------------------------------------------------------

text_prompt = st.chat_input("Ask a question...")

# --------------------------------------------------------
# USE EITHER TEXT OR VOICE
# --------------------------------------------------------

prompt = text_prompt if text_prompt else voice_prompt

# --------------------------------------------------------
# CHATBOT
# --------------------------------------------------------

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):

        answer = respond(
            prompt,
            persona
        )

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
