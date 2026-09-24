from langchain_core.prompts import PromptTemplate

try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    from langchain_community.llms import Ollama

from backend.rag.retriever import retrieve_policy


def answer_policy_question(scholarship_id: str, question: str) -> str:
    """
    Retrieve relevant policy text via RAG and use a LangChain chain
    to answer the user's question grounded in the retrieved text.
    """
    context = retrieve_policy(query=question, scholarship_id=scholarship_id)
    if not context:
        context = "No specific policy text found for this scholarship."

    prompt_template = PromptTemplate.from_template(
        "You are an AI assistant answering questions about scholarship policy.\n"
        "Answer the question accurately based ONLY on the retrieved policy context provided below.\n"
        "If the answer is not mentioned in the context, state that the policy does not specify this information.\n\n"
        "Retrieved Policy Context:\n{context}\n\n"
        "User Question: {question}\n\n"
        "Grounded Answer:"
    )

    llm = Ollama(model="llama3.1")
    chain = prompt_template | llm
    answer = chain.invoke({"context": context, "question": question})

    return str(answer).strip()
