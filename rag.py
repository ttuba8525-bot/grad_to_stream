import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from prompts import SALES_PROMPTS
import vectorstore

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="llama-3.3-70b-versatile",
    temperature=0.3,
)

# ---------------------------------------------------------------------------
# Chat History Store
# ---------------------------------------------------------------------------

store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# ---------------------------------------------------------------------------
# RAG Chain
# ---------------------------------------------------------------------------

def create_rag_chain(persona_name: str, retrieved_context: str):
    system_instruction = SALES_PROMPTS.get(
        persona_name,
        SALES_PROMPTS["PragyanAI Student Counselor"],
    ).format(context=retrieved_context)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    return prompt | llm | StrOutputParser()


# ---------------------------------------------------------------------------
# Streamlit Response Function
# ---------------------------------------------------------------------------

def respond(message, persona_name):

    if not message.strip():
        return ""

    retriever = vectorstore.vectorstore.as_retriever(search_kwargs={"k": 4})

    relevant_docs = retriever.invoke(message)

    context_str = "\n".join(
        [f"- {doc.page_content}" for doc in relevant_docs]
    )

    session_id = (
        f"pragyan_session_{persona_name.replace(' ', '_')}"
    )

    base_chain = create_rag_chain(
        persona_name,
        context_str,
    )

    conversational_chain = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    return conversational_chain.invoke(
        {"input": message},
        config={
            "configurable": {
                "session_id": session_id
            }
        },
    )


# ---------------------------------------------------------------------------
# Clear Chat
# ---------------------------------------------------------------------------

def clear_chat_history(persona_name):

    session_id = (
        f"pragyan_session_{persona_name.replace(' ', '_')}"
    )

    if session_id in store:
        store[session_id].clear()
