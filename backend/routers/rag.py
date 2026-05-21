"""RAG query endpoint and follow-up email generation."""
from fastapi import APIRouter
from backend.models.schemas import QueryIn
from backend.rag.retrieval import rag_query
from backend.services.genai import generate_followup_email, explain_segment
from pydantic import BaseModel

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/query")
async def query_meetings(body: QueryIn):
    result = rag_query(body.question, meeting_id=body.meeting_id)
    return result

class EmailRequest(BaseModel):
    summary: str
    action_items: list[dict]

@router.post("/followup-email")
async def followup_email(body: EmailRequest):
    email = generate_followup_email(body.summary, body.action_items)
    return {"email": email}

class ExplainRequest(BaseModel):
    text: str

@router.post("/explain")
async def explain(body: ExplainRequest):
    return {"explanation": explain_segment(body.text)}
