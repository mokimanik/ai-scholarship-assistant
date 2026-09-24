import hashlib
import numpy as np
from typing import Optional, List

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


def retrieve_policy(query: str, scholarship_id: Optional[str] = None) -> str:
    """
    Perform a semantic search over the Chroma vector database.
    If scholarship_id is provided, filter for documents matching that scholarship_id.
    Return the most relevant chunk(s) as plain text.
    """
    if not config.CHROMA_DB_DIR.exists():
        return ""

    embeddings = SafeOllamaEmbeddings(model="llama3.1")
    vectorstore = Chroma(
        persist_directory=str(config.CHROMA_DB_DIR),
        embedding_function=embeddings
    )

    filter_dict = None
    if scholarship_id:
        filter_dict = {"scholarship_id": scholarship_id.upper()}

    results = vectorstore.similarity_search(
        query=query,
        k=3,
        filter=filter_dict
    )

    if not results:
        return ""

    return "\n\n".join([doc.page_content for doc in results])
