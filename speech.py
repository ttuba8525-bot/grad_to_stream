import os
import tempfile

import streamlit as st
from groq import Groq

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


def transcribe_audio(audio_bytes):
    """
    Transcribes microphone audio using Groq Whisper.
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        temp_path = tmp.name

    try:
        with open(temp_path, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                response_format="text"
            )

        return transcription

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
