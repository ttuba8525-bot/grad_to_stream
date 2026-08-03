import tempfile
from groq import Groq
import streamlit as st


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


def transcribe_audio(audio_bytes):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    with open(audio_path, "rb") as file:

        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            response_format="text",
            language="en"
        )

    return transcription
