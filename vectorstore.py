import pandas as pd

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

embeddings=HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore=None


def load_documents_into_vectorstore(files=None):

    global vectorstore

    docs=[]

    if files:

        for file in files:

            if file.name.endswith(".pdf"):

                loader=PyPDFLoader(file.name)
                docs.extend(loader.load())

            elif file.name.endswith((".xlsx",".xls")):

                df=pd.read_excel(file)

                for _,row in df.iterrows():

                    docs.append(
                        Document(
                            page_content=" | ".join(
                                [
                                    f"{c}:{v}"
                                    for c,v in row.items()
                                ]
                            )
                        )
                    )

    vectorstore=FAISS.from_documents(
        docs,
        embeddings
    )

    return "Knowledge Base Updated"
