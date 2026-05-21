"""Meetings CRUD endpoints."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.db_models import Meeting
from backend.models.schemas import MeetingCreate, MeetingOut

router = APIRouter(prefix="/meetings", tags=["meetings"])

@router.post("/", response_model=MeetingOut)
async def create_meeting(body: MeetingCreate, db: AsyncSession = Depends(get_db)):
    m = Meeting(id=str(uuid.uuid4()), title=body.title)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

@router.get("/", response_model=list[MeetingOut])
async def list_meetings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).order_by(Meeting.started_at.desc()))
    return result.scalars().all()

@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    m = await db.get(Meeting, meeting_id)
    if not m:
        raise HTTPException(404, "Meeting not found")
    return m

@router.post("/{meeting_id}/end", response_model=MeetingOut)
async def end_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    m = await db.get(Meeting, meeting_id)
    if not m:
        raise HTTPException(404, "Meeting not found")
    m.status = "ended"
    m.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(m)
    return m
