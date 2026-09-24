import os
import hashlib
import numpy as np
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from backend import config


class SafeOllamaEmbeddings(OllamaEmbeddings):
    """
    OllamaEmbeddings subclass for model 'llama3.1'.
    Falls back gracefully if the local Ollama server lacks embeddings support.
    """
    def __init__(self, model: str = "llama3.1", **kwargs):
        super().__init__(model=model, **kwargs)

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for word in words:
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            val = ((h >> 16) % 1000) / 1000.0 - 0.5
            vec[idx] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return super().embed_documents(texts)
        except Exception as e:
            print(f"[Notice] Ollama embedding API call fallback triggered: {e}")
            return [self._fallback_embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        try:
            return super().embed_query(text)
        except Exception as e:
            print(f"[Notice] Ollama embedding query fallback triggered: {e}")
            return self._fallback_embed(text)


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
    """Load policy documents, split into chunks, embed using OllamaEmbeddings (llama3.1), and store in Chroma DB."""
    raw_docs = load_documents()
    if not raw_docs:
        print("No documents found in docs/ to ingest.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(raw_docs)

    embeddings = SafeOllamaEmbeddings(model="llama3.1")

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
