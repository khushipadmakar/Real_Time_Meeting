"""
Analytics endpoint — ML + GenAI pipeline.
Optimized: Groq calls run in parallel, ChromaDB indexing in executor.
"""
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.database import get_db
from backend.models.db_models import (
    MeetingTranscript, MeetingSummary, MeetingActionItem,
    MeetingSpeaker, MeetingEmbedding
)
from backend.ml.topic_clustering import cluster_topics
from backend.ml.speaker_analysis import analyze_speakers
from backend.ml.anomaly_detection import detect_anomalies
from backend.ml.engagement import compute_engagement_score
from backend.services.genai import summarize_meeting, extract_action_items
from backend.rag.vector_store import chunk_text, index_chunks
try:
    from backend.kafka.producer import publish_event as _pub
    def publish_event(t, p): _pub(t, p)
except Exception:
    def publish_event(t, p): pass
from backend.config import settings

router = APIRouter(prefix="/analytics", tags=["analytics"])

def _run_ml(transcript_dicts):
    """All CPU-bound ML in one executor call."""
    texts = [t["text"] for t in transcript_dicts]
    return {
        "speaker_stats": analyze_speakers(transcript_dicts),
        "topics": cluster_topics(texts),
        "anomalies": detect_anomalies(transcript_dicts),
    }

@router.post("/{meeting_id}/process")
async def process_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    # Load transcripts
    result = await db.execute(
        select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting_id)
    )
    transcripts = result.scalars().all()
    if not transcripts:
        raise HTTPException(400, "No transcripts found for this meeting")

    transcript_dicts = [
        {"speaker": t.speaker, "text": t.text,
         "timestamp": t.timestamp.isoformat(), "sentiment_score": t.sentiment_score}
        for t in transcripts
    ]
    full_text = "\n".join(f"{t['speaker']}: {t['text']}" for t in transcript_dicts)
    loop = asyncio.get_event_loop()

    # Run ML (CPU) + both Groq calls in parallel
    ml_task = loop.run_in_executor(None, _run_ml, transcript_dicts)
    summary_task = loop.run_in_executor(None, summarize_meeting, full_text)
    actions_task = loop.run_in_executor(None, extract_action_items, full_text)

    ml_result, summary_text, action_items = await asyncio.gather(
        ml_task, summary_task, actions_task
    )

    speaker_stats = ml_result["speaker_stats"]
    topics = ml_result["topics"]
    anomalies = ml_result["anomalies"]
    engagement = compute_engagement_score(speaker_stats, len(anomalies), len(transcript_dicts))

    # ChromaDB indexing in executor (non-blocking)
    chunks = chunk_text(full_text)
    chroma_ids = await loop.run_in_executor(None, index_chunks, chunks, meeting_id)

    # Clear old analytics for this meeting before saving new
    await db.execute(delete(MeetingSummary).where(MeetingSummary.meeting_id == meeting_id))
    await db.execute(delete(MeetingActionItem).where(MeetingActionItem.meeting_id == meeting_id))
    await db.execute(delete(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id))
    await db.execute(delete(MeetingEmbedding).where(MeetingEmbedding.meeting_id == meeting_id))

    # Persist
    db.add(MeetingSummary(id=str(uuid.uuid4()), meeting_id=meeting_id,
                          summary=summary_text, topics=[t["label"] for t in topics]))
    for item in action_items:
        db.add(MeetingActionItem(id=str(uuid.uuid4()), meeting_id=meeting_id,
                                 assignee=item.get("assignee", "Unassigned"),
                                 task=item.get("task", ""),
                                 priority=item.get("priority", "medium")))
    for sp in speaker_stats:
        db.add(MeetingSpeaker(id=str(uuid.uuid4()), meeting_id=meeting_id,
                              name=sp["name"], speaking_time_seconds=sp["speaking_time_seconds"],
                              turn_count=sp["turn_count"], avg_sentiment=sp["avg_sentiment"]))
    for chunk, cid in zip(chunks, chroma_ids):
        db.add(MeetingEmbedding(id=str(uuid.uuid4()), meeting_id=meeting_id,
                                chunk_text=chunk, chroma_id=cid))
    await db.commit()

    # Kafka events (fire and forget)
    publish_event(settings.KAFKA_TOPIC_SUMMARIES, {"meeting_id": meeting_id, "summary": summary_text})
    publish_event(settings.KAFKA_TOPIC_ACTION_ITEMS, {"meeting_id": meeting_id, "items": action_items})
    if anomalies:
        publish_event(settings.KAFKA_TOPIC_ALERTS, {"meeting_id": meeting_id, "anomalies": len(anomalies)})

    return {
        "meeting_id": meeting_id,
        "summary": summary_text,
        "action_items": action_items,
        "topics": topics,
        "speaker_stats": speaker_stats,
        "anomalies": anomalies,
        "engagement_score": engagement,
    }

@router.get("/{meeting_id}")
async def get_analytics(meeting_id: str, db: AsyncSession = Depends(get_db)):
    summary_res = await db.execute(
        select(MeetingSummary).where(MeetingSummary.meeting_id == meeting_id)
    )
    summary = summary_res.scalars().first()
    actions_res = await db.execute(
        select(MeetingActionItem).where(MeetingActionItem.meeting_id == meeting_id)
    )
    speakers_res = await db.execute(
        select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id)
    )
    return {
        "summary": summary.summary if summary else None,
        "topics": summary.topics if summary else [],
        "action_items": [
            {"assignee": a.assignee, "task": a.task, "priority": a.priority, "resolved": a.resolved}
            for a in actions_res.scalars().all()
        ],
        "speakers": [
            {"name": s.name, "speaking_time_seconds": s.speaking_time_seconds,
             "turn_count": s.turn_count, "avg_sentiment": s.avg_sentiment}
            for s in speakers_res.scalars().all()
        ],
    }
