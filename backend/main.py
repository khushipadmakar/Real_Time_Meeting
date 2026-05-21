"""
Main FastAPI application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import meetings, transcripts, analytics, rag, agent
from backend.services.audio_stream import handle_audio_stream

# Kafka consumers are optional — skip if Kafka is not running
try:
    from backend.kafka.consumers import start_all_consumers
    _kafka_available = True
except Exception:
    _kafka_available = False

os.makedirs("./data/chroma", exist_ok=True)
os.makedirs("./data", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if _kafka_available:
        try:
            start_all_consumers()
        except Exception as e:
            print(f"[warn] Kafka consumers not started: {e}")
    yield

app = FastAPI(title="Real-Time AI Meeting Platform", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(meetings.router)
app.include_router(transcripts.router)
app.include_router(analytics.router)
app.include_router(rag.router)
app.include_router(agent.router)

# WebSocket for real-time audio streaming
@app.websocket("/ws/audio/{meeting_id}")
async def audio_ws(websocket: WebSocket, meeting_id: str):
    await handle_audio_stream(websocket, meeting_id)

@app.get("/health")
async def health():
    return {"status": "ok"}
