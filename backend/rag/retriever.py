from typing import Optional, List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from backend import config


def retrieve_policy(query: str, scholarship_id: Optional[str] = None) -> str:
    """
    Perform a semantic search over the Chroma vector database using GoogleGenerativeAIEmbeddings.
    If scholarship_id is provided, filter for documents matching that scholarship_id.
    Return the most relevant chunk(s) as plain text.
    """
    if not config.CHROMA_DB_DIR.exists():
        return ""

    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GEMINI_API_KEY
    )
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
