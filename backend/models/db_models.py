import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

def _uuid() -> str:
    return str(uuid.uuid4())

class Meeting(Base):
    __tablename__ = "meetings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String, default="Untitled Meeting")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")  # active | ended
    transcripts: Mapped[list["MeetingTranscript"]] = relationship(back_populates="meeting")
    summaries: Mapped[list["MeetingSummary"]] = relationship(back_populates="meeting")
    action_items: Mapped[list["MeetingActionItem"]] = relationship(back_populates="meeting")
    speakers: Mapped[list["MeetingSpeaker"]] = relationship(back_populates="meeting")

class MeetingTranscript(Base):
    __tablename__ = "meeting_transcripts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    speaker: Mapped[str] = mapped_column(String, default="Unknown")
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    meeting: Mapped["Meeting"] = relationship(back_populates="transcripts")

class MeetingSummary(Base):
    __tablename__ = "meeting_summaries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    summary: Mapped[str] = mapped_column(Text)
    topics: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meeting: Mapped["Meeting"] = relationship(back_populates="summaries")

class MeetingActionItem(Base):
    __tablename__ = "meeting_action_items"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    assignee: Mapped[str] = mapped_column(String)
    task: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String, default="medium")
    resolved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")

class MeetingSpeaker(Base):
    __tablename__ = "meeting_speakers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    name: Mapped[str] = mapped_column(String)
    speaking_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    turn_count: Mapped[int] = mapped_column(default=0)
    avg_sentiment: Mapped[float] = mapped_column(Float, default=0.0)
    meeting: Mapped["Meeting"] = relationship(back_populates="speakers")

class MeetingEmbedding(Base):
    __tablename__ = "meeting_embeddings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column(String)
    chunk_text: Mapped[str] = mapped_column(Text)
    chroma_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
