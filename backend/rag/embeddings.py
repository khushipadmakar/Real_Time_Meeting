"""
Embedding generation using sentence-transformers (local, no API cost).
"""
from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None

def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedder().encode(texts, convert_to_numpy=True).tolist()

def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
