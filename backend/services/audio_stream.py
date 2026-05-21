import asyncio
import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from backend.services.transcription import transcribe_audio_bytes
from backend.services.speaker_tracker import SpeakerTracker
from backend.config import settings

try:
    from backend.kafka.producer import publish_event as _publish
    def publish_event(topic, payload): _publish(topic, payload)
except Exception:
    def publish_event(topic, payload): pass

SAMPLE_RATE = 16000
CHUNK_BYTES = SAMPLE_RATE * 4 * 3  # 3 seconds of float32

async def handle_audio_stream(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    tracker = SpeakerTracker()
    buffer = bytearray()

    async def process_chunk(chunk: bytes):
        text = await asyncio.get_event_loop().run_in_executor(
            None, transcribe_audio_bytes, chunk
        )
        if not text:
            return
        speaker = tracker.detect_speaker(chunk)
        payload = {
            "meeting_id": meeting_id,
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            pass
        publish_event(settings.KAFKA_TOPIC_TRANSCRIPTS, payload)

    try:
        while True:
            try:
                data = await websocket.receive()
            except (WebSocketDisconnect, RuntimeError):
                break

            if data.get("type") == "websocket.disconnect":
                break
            if data.get("text") == "END":
                break
            if "bytes" in data and data["bytes"]:
                buffer.extend(data["bytes"])

            while len(buffer) >= CHUNK_BYTES:
                chunk = bytes(buffer[:CHUNK_BYTES])
                buffer = buffer[CHUNK_BYTES:]
                await process_chunk(chunk)

    finally:
        if buffer:
            await process_chunk(bytes(buffer))
