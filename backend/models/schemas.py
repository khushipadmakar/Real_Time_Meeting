from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MeetingCreate(BaseModel):
    title: str = "Untitled Meeting"

class MeetingOut(BaseModel):
    id: str
    title: str
    started_at: datetime
    ended_at: Optional[datetime]
    status: str
    model_config = {"from_attributes": True}

class TranscriptIn(BaseModel):
    meeting_id: str
    speaker: str = "Unknown"
    text: str

class TranscriptOut(TranscriptIn):
    id: str
    timestamp: datetime
    sentiment_score: Optional[float]
    model_config = {"from_attributes": True}

class ActionItemOut(BaseModel):
    id: str
    meeting_id: str
    assignee: str
    task: str
    priority: str
    resolved: bool
    model_config = {"from_attributes": True}

class SummaryOut(BaseModel):
    id: str
    meeting_id: str
    summary: str
    topics: list
    created_at: datetime
    model_config = {"from_attributes": True}

class SpeakerOut(BaseModel):
    id: str
    meeting_id: str
    name: str
    speaking_time_seconds: float
    turn_count: int
    avg_sentiment: float
    model_config = {"from_attributes": True}

class QueryIn(BaseModel):
    question: str
    meeting_id: Optional[str] = None
