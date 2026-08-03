import os
import tempfile
import pandas as pd

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# -------------------------------------------------------------------
# Embedding Model
# -------------------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = None


def load_documents_into_vectorstore(files=None):
    """
    Creates/Updates the FAISS Vector Store.

    If files=None:
        Loads the default FAQ Excel and Presentation PDF.

    If files are uploaded:
        Loads uploaded PDF/Excel files.
    """

    global vectorstore

    docs = []

    # ================================================================
    # CASE 1 : USER UPLOADS FILES
    # ================================================================

    if files:

        for file in files:

            # ---------------- PDF ----------------
            if file.name.endswith(".pdf"):

                # Streamlit uploader gives bytes, save temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file.read())
                    temp_path = tmp.name

                loader = PyPDFLoader(temp_path)
                docs.extend(loader.load())

                os.remove(temp_path)

            # ---------------- Excel ----------------
            elif file.name.endswith((".xlsx", ".xls")):

                df = pd.read_excel(file)

                for _, row in df.iterrows():
                    docs.append(
                        Document(
                            page_content=" | ".join(
                                f"{col}: {row[col]}" for col in df.columns
                            )
                        )
                    )

    # ================================================================
    # CASE 2 : LOAD DEFAULT FILES
    # ================================================================

    else:

        # Default PDF
        if os.path.exists("PragyanAI_Presentation.pdf"):
            loader = PyPDFLoader("PragyanAI_Presentation.pdf")
            docs.extend(loader.load())

        # Default Excel
        if os.path.exists("PragyanAI_FAQ.xlsx"):

            df = pd.read_excel("PragyanAI_FAQ.xlsx")

            for _, row in df.iterrows():
                docs.append(
                    Document(
                        page_content=" | ".join(
                            f"{col}: {row[col]}" for col in df.columns
                        )
                    )
                )

    # ================================================================
    # CREATE VECTOR STORE
    # ================================================================

    if len(docs) == 0:
        print("No documents found.")
        return "No documents found."

    vectorstore = FAISS.from_documents(
        docs,
        embeddings
    )

    print(f"Loaded {len(docs)} documents.")

    return f"Knowledge Base Updated ({len(docs)} chunks)"
