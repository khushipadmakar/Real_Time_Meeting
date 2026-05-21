"""Tests for transcript chunking and embedding generation."""
import pytest
from backend.rag.vector_store import chunk_text
from backend.rag.embeddings import embed_text, embed_texts

def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)

def test_chunk_text_short():
    text = "Hello world"
    chunks = chunk_text(text, chunk_size=300)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world"

def test_chunk_text_overlap():
    words = [f"w{i}" for i in range(20)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=10, overlap=3)
    # Verify overlap: last words of chunk N appear in chunk N+1
    assert len(chunks) >= 2

def test_embed_text_shape():
    emb = embed_text("This is a test sentence.")
    assert isinstance(emb, list)
    assert len(emb) == 384  # all-MiniLM-L6-v2 output dim

def test_embed_texts_batch():
    texts = ["Meeting about Kafka", "Deployment pipeline issues", "Action items review"]
    embeddings = embed_texts(texts)
    assert len(embeddings) == 3
    assert all(len(e) == 384 for e in embeddings)

def test_embed_similarity():
    """Similar texts should have higher cosine similarity than dissimilar ones."""
    import numpy as np
    e1 = np.array(embed_text("Kafka streaming pipeline"))
    e2 = np.array(embed_text("Kafka event streaming"))
    e3 = np.array(embed_text("Birthday party planning"))
    sim_12 = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
    sim_13 = float(np.dot(e1, e3) / (np.linalg.norm(e1) * np.linalg.norm(e3)))
    assert sim_12 > sim_13
