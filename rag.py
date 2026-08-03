import streamlit as st

from langchain_groq import ChatGroq

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_core.runnables.history import RunnableWithMessageHistory

from prompts import SALES_PROMPTS
from vectorstore import vectorstore

llm=ChatGroq(

    groq_api_key=st.secrets["GROQ_API_KEY"],

    model_name="llama-3.3-70b-versatile",

    temperature=0.3
)

store={}
