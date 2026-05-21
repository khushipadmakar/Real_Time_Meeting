"""
AI Agent — agentic workflow that analyzes a completed meeting and:
1. Decides if escalation is needed
2. Identifies unresolved discussions
3. Detects missed/unassigned action items
4. Generates reminders
5. Prioritizes follow-ups

Uses LLM with structured JSON output for each decision.
"""
import json
from backend.services.genai import _chat

def run_agent(meeting_id: str, transcript_text: str, action_items: list[dict], anomalies: list[dict]) -> dict:
    """
    Returns a structured agent report with decisions and recommendations.
    """
    items_text = json.dumps(action_items, indent=2)
    anomaly_text = json.dumps([a.get("text", "") for a in anomalies[:5]], indent=2)

    raw = _chat(
        system=(
            "You are an AI meeting agent. Analyze the meeting and return a JSON report with these keys:\n"
            "- needs_escalation: bool\n"
            "- escalation_reason: str (empty if false)\n"
            "- unresolved_topics: list[str]\n"
            "- missed_action_items: list[str] (tasks mentioned but not assigned)\n"
            "- reminders: list[{assignee: str, reminder: str}]\n"
            "- prioritized_followups: list[{task: str, priority: high|medium|low, reason: str}]\n"
            "Be concise and grounded in the transcript."
        ),
        user=(
            f"TRANSCRIPT:\n{transcript_text[:3000]}\n\n"
            f"EXTRACTED ACTION ITEMS:\n{items_text}\n\n"
            f"ANOMALOUS SEGMENTS:\n{anomaly_text}"
        ),
        json_mode=True,
    )
    return json.loads(raw)
