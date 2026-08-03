import os
import tempfile
import pandas as pd

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# -------------------------------------------------------
# Embedding Model
# -------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = None


def load_documents_into_vectorstore(files=None):
    """
    Creates/Updates the FAISS Vector Store.

    If files=None:
        Loads the default files from the data folder.

    If files are provided:
        Loads uploaded PDF/Excel files.
    """

    global vectorstore

    docs = []

    # -------------------------------------------------------
    # CASE 1 : Uploaded Files
    # -------------------------------------------------------

    if files:

        for file in files:

            # PDF
            if file.name.endswith(".pdf"):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file.read())
                    temp_path = tmp.name

                loader = PyPDFLoader(temp_path)
                docs.extend(loader.load())

                os.remove(temp_path)

            # Excel
            elif file.name.endswith((".xlsx", ".xls")):

                df = pd.read_excel(file)

                for _, row in df.iterrows():

                    docs.append(
                        Document(
                            page_content=" | ".join(
                                f"{col}: {row[col]}"
                                for col in df.columns
                            )
                        )
                    )

    # -------------------------------------------------------
    # CASE 2 : Default Files
    # -------------------------------------------------------

    else:

        pdf_path = os.path.join("data", "Presentation.pdf")

        if os.path.exists(pdf_path):
            loader = PyPDFLoader(pdf_path)
            docs.extend(loader.load())

        excel_path = os.path.join("data", "PragyanAI_FAQ.xlsx")

        if os.path.exists(excel_path):

            df = pd.read_excel(excel_path)

            for _, row in df.iterrows():

                docs.append(
                    Document(
                        page_content=" | ".join(
                            f"{col}: {row[col]}"
                            for col in df.columns
                        )
                    )
                )

    # -------------------------------------------------------
    # Create Vector Store
    # -------------------------------------------------------

    if len(docs) == 0:
        print("❌ No documents found.")
        return "No documents found."

    print(f"Loaded {len(docs)} documents.")

    vectorstore = FAISS.from_documents(
        docs,
        embeddings
    )

    return f"Knowledge Base Updated ({len(docs)} chunks)"
