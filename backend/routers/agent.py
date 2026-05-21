"""AI Agent endpoint."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.db_models import MeetingTranscript, MeetingActionItem
from backend.ml.anomaly_detection import detect_anomalies
from backend.services.agent import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/{meeting_id}/analyze")
async def agent_analyze(meeting_id: str, db: AsyncSession = Depends(get_db)):
    transcripts_res = await db.execute(
        select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting_id)
    )
    transcripts = transcripts_res.scalars().all()
    if not transcripts:
        raise HTTPException(400, "No transcripts found")

    transcript_dicts = [
        {"speaker": t.speaker, "text": t.text, "sentiment_score": t.sentiment_score}
        for t in transcripts
    ]
    full_text = "\n".join(f"{t['speaker']}: {t['text']}" for t in transcript_dicts)

    actions_res = await db.execute(
        select(MeetingActionItem).where(MeetingActionItem.meeting_id == meeting_id)
    )
    action_items = [
        {"assignee": a.assignee, "task": a.task, "priority": a.priority}
        for a in actions_res.scalars().all()
    ]
    anomalies = detect_anomalies(transcript_dicts)

    # Run agent (Groq call) in executor so it doesn't block event loop
    loop = asyncio.get_event_loop()
    report = await loop.run_in_executor(
        None, run_agent, meeting_id, full_text, action_items, anomalies
    )
    return report
