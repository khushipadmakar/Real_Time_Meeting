"""
GenAI pipeline using Groq API (OpenAI-compatible).
All outputs are grounded in the actual transcript text.
"""
import json
from openai import OpenAI
from backend.config import settings

_client: OpenAI | None = None

def _llm() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        )
    return _client

def _chat(system: str, user: str, json_mode: bool = False) -> str:
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = _llm().chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        **kwargs,
    )
    return resp.choices[0].message.content.strip()

# ── Summarization ──────────────────────────────────────────────────────────────

def summarize_meeting(transcript_text: str) -> str:
    return _chat(
        "You are a meeting analyst. Summarize the meeting concisely, covering key decisions, "
        "main discussion points, and outcomes. Be factual and grounded in the transcript.",
        f"TRANSCRIPT:\n{transcript_text}\n\nProvide a 3-5 sentence summary.",
    )

# ── Action Item Extraction ─────────────────────────────────────────────────────

def extract_action_items(transcript_text: str) -> list[dict]:
    """Returns list of {assignee, task, priority}."""
    raw = _chat(
        "You are a meeting assistant. Extract all action items from the transcript. "
        "Return JSON: {\"action_items\": [{\"assignee\": str, \"task\": str, \"priority\": \"high|medium|low\"}]}",
        f"TRANSCRIPT:\n{transcript_text}",
        json_mode=True,
    )
    data = json.loads(raw)
    return data.get("action_items", [])

# ── Follow-up Email ────────────────────────────────────────────────────────────

def generate_followup_email(summary: str, action_items: list[dict]) -> str:
    items_text = "\n".join(f"- {a['assignee']}: {a['task']}" for a in action_items)
    return _chat(
        "You are a professional assistant. Write a concise follow-up email based on the meeting summary and action items.",
        f"SUMMARY:\n{summary}\n\nACTION ITEMS:\n{items_text}\n\nWrite the email.",
    )

# ── Q&A ────────────────────────────────────────────────────────────────────────

def answer_question(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    return _chat(
        "You are a meeting knowledge assistant. Answer questions using only the provided meeting context. "
        "If the answer is not in the context, say so.",
        f"CONTEXT:\n{context}\n\nQUESTION: {question}",
    )

# ── Conversation Explanation ───────────────────────────────────────────────────

def explain_segment(text: str) -> str:
    return _chat(
        "You are a meeting analyst. Explain what is being discussed in this transcript segment, "
        "including any implied context or decisions.",
        f"SEGMENT:\n{text}",
    )
