"""
ChromaDB vector store — stores transcript chunks with embeddings and metadata.
"""
import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.config import settings
from backend.rag.embeddings import embed_texts

_client: chromadb.ClientAPI | None = None
COLLECTION_NAME = "meeting_transcripts"

def _get_collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

def index_chunks(chunks: list[str], meeting_id: str, metadata_extra: dict | None = None) -> list[str]:
    """Embed and store chunks. Returns list of chroma IDs."""
    if not chunks:
        return []
    col = _get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    embeddings = embed_texts(chunks)
    metadatas = [{"meeting_id": meeting_id, **(metadata_extra or {})} for _ in chunks]
    col.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return ids

def retrieve(query: str, meeting_id: str | None = None, top_k: int = 5) -> list[dict]:
    """Retrieve top-k relevant chunks for a query."""
    col = _get_collection()
    from backend.rag.embeddings import embed_text
    query_emb = embed_text(query)
    where = {"meeting_id": meeting_id} if meeting_id else None
    results = col.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": doc, "metadata": meta, "score": round(1 - dist, 4)})
    return chunks

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks
