"""Transcript ingestion and retrieval endpoints."""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.db_models import MeetingTranscript
from backend.models.schemas import TranscriptIn, TranscriptOut
from backend.ml.sentiment import score_text
try:
    from backend.kafka.producer import publish_event as _publish
    def publish_event(topic, payload): _publish(topic, payload)
except Exception:
    def publish_event(topic, payload): pass
from backend.config import settings

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

@router.post("/", response_model=TranscriptOut)
async def add_transcript(body: TranscriptIn, db: AsyncSession = Depends(get_db)):
    sentiment = score_text(body.text)
    t = MeetingTranscript(
        id=str(uuid.uuid4()),
        meeting_id=body.meeting_id,
        speaker=body.speaker,
        text=body.text,
        sentiment_score=sentiment,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    publish_event(settings.KAFKA_TOPIC_TRANSCRIPTS, {
        "meeting_id": body.meeting_id, "speaker": body.speaker, "text": body.text
    })
    return t

@router.get("/{meeting_id}", response_model=list[TranscriptOut])
async def get_transcripts(meeting_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MeetingTranscript)
        .where(MeetingTranscript.meeting_id == meeting_id)
        .order_by(MeetingTranscript.timestamp)
    )
    return result.scalars().all()

@router.post("/upload-audio/{meeting_id}")
async def upload_audio(meeting_id: str, file: UploadFile = File(...)):
    """Upload an audio file and transcribe it."""
    import tempfile, os
    from backend.services.transcription import transcribe_file
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(await file.read())
        tmp_path = f.name
    text = transcribe_file(tmp_path)
    os.unlink(tmp_path)
    return {"meeting_id": meeting_id, "text": text}
