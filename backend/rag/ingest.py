import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from backend import config


def load_documents() -> List[Document]:
    """Load all .txt files from docs/ and attach scholarship_id metadata."""
    docs = []
    if not config.DOCS_DIR.exists():
        return docs

    for file_path in config.DOCS_DIR.glob("*.txt"):
        scholarship_id = file_path.stem.upper()
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        doc = Document(
            page_content=text,
            metadata={
                "scholarship_id": scholarship_id,
                "source": str(file_path)
            }
        )
        docs.append(doc)

    return docs


def ingest_documents():
    """Load policy documents, split into chunks, embed using GoogleGenerativeAIEmbeddings (models/embedding-001), and store in Chroma DB."""
    raw_docs = load_documents()
    if not raw_docs:
        print("No documents found in docs/ to ingest.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(raw_docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GEMINI_API_KEY
    )

    os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(config.CHROMA_DB_DIR)
    )
    print(f"Successfully ingested {len(chunks)} chunks into Chroma DB at {config.CHROMA_DB_DIR}")
    return vectorstore


if __name__ == "__main__":
    ingest_documents()
