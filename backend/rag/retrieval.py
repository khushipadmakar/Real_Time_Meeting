"""
RAG retrieval pipeline — retrieves relevant chunks and generates grounded answers.
"""
from backend.rag.vector_store import retrieve
from backend.services.genai import answer_question

def rag_query(question: str, meeting_id: str | None = None, top_k: int = 5) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant transcript chunks from ChromaDB
    2. Pass to LLM for grounded answer generation
    """
    chunks = retrieve(question, meeting_id=meeting_id, top_k=top_k)
    context_texts = [c["text"] for c in chunks]
    answer = answer_question(question, context_texts)
    return {
        "answer": answer,
        "sources": chunks,
    }
