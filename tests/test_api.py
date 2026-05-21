"""Tests for FastAPI endpoints using TestClient."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

# Patch heavy dependencies before importing app
import sys
sys.modules.setdefault("whisper", MagicMock())
sys.modules.setdefault("confluent_kafka", MagicMock())
sys.modules.setdefault("chromadb", MagicMock())
sys.modules.setdefault("sentence_transformers", MagicMock())
sys.modules.setdefault("openai", MagicMock())

from backend.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

async def test_create_meeting(client):
    r = await client.post("/meetings/", json={"title": "Test Meeting"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Test Meeting"
    assert "id" in data
    return data["id"]

async def test_list_meetings(client):
    r = await client.get("/meetings/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

async def test_get_meeting_not_found(client):
    r = await client.get("/meetings/nonexistent-id")
    assert r.status_code == 404

async def test_add_transcript(client):
    # Create meeting first
    m = await client.post("/meetings/", json={"title": "Transcript Test"})
    mid = m.json()["id"]
    r = await client.post("/transcripts/", json={
        "meeting_id": mid,
        "speaker": "Alice",
        "text": "This is a great meeting with excellent progress",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["speaker"] == "Alice"
    assert data["sentiment_score"] is not None

async def test_get_transcripts(client):
    m = await client.post("/meetings/", json={"title": "Get Transcripts Test"})
    mid = m.json()["id"]
    await client.post("/transcripts/", json={"meeting_id": mid, "speaker": "Bob", "text": "Hello"})
    r = await client.get(f"/transcripts/{mid}")
    assert r.status_code == 200
    assert len(r.json()) >= 1

async def test_end_meeting(client):
    m = await client.post("/meetings/", json={"title": "End Test"})
    mid = m.json()["id"]
    r = await client.post(f"/meetings/{mid}/end")
    assert r.status_code == 200
    assert r.json()["status"] == "ended"

async def test_process_meeting_no_transcripts(client):
    m = await client.post("/meetings/", json={"title": "Empty Meeting"})
    mid = m.json()["id"]
    r = await client.post(f"/analytics/{mid}/process")
    assert r.status_code == 400  # no transcripts

async def test_rag_query_endpoint(client):
    with patch("backend.routers.rag.rag_query") as mock_rag:
        mock_rag.return_value = {"answer": "Test answer", "sources": []}
        r = await client.post("/rag/query", json={"question": "What was discussed?"})
        assert r.status_code == 200
        assert "answer" in r.json()
