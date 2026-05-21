"""Tests for GenAI pipeline (mocked LLM calls) and RAG retrieval."""
import pytest
import json
from unittest.mock import patch, MagicMock

SAMPLE_TRANSCRIPT = """
Alice: We need to fix the Kafka consumer lag issue by Friday.
Bob: I will handle the deployment pipeline review.
Alice: Great. Also, the CI/CD workflow is broken and needs urgent attention.
Charlie: I can look into the Databricks cluster configuration.
"""

def _mock_llm_response(content: str):
    mock = MagicMock()
    mock.choices[0].message.content = content
    return mock

def test_summarize_meeting():
    summary_text = "The meeting focused on Kafka lag, deployment, and CI/CD issues."
    with patch("backend.services.genai._llm") as mock_llm:
        mock_llm.return_value.chat.completions.create.return_value = _mock_llm_response(summary_text)
        from backend.services.genai import summarize_meeting
        result = summarize_meeting(SAMPLE_TRANSCRIPT)
        assert isinstance(result, str)
        assert len(result) > 0

def test_extract_action_items():
    items = [
        {"assignee": "Alice", "task": "Fix Kafka consumer lag", "priority": "high"},
        {"assignee": "Bob", "task": "Review deployment pipeline", "priority": "medium"},
    ]
    with patch("backend.services.genai._llm") as mock_llm:
        mock_llm.return_value.chat.completions.create.return_value = _mock_llm_response(
            json.dumps({"action_items": items})
        )
        from backend.services.genai import extract_action_items
        result = extract_action_items(SAMPLE_TRANSCRIPT)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["assignee"] == "Alice"

def test_generate_followup_email():
    email_text = "Dear team, following up on today's meeting..."
    with patch("backend.services.genai._llm") as mock_llm:
        mock_llm.return_value.chat.completions.create.return_value = _mock_llm_response(email_text)
        from backend.services.genai import generate_followup_email
        result = generate_followup_email("Summary text", [{"assignee": "Alice", "task": "Fix Kafka"}])
        assert isinstance(result, str)
        assert len(result) > 0

def test_answer_question():
    answer = "The deployment issue was discussed by Alice and Bob."
    with patch("backend.services.genai._llm") as mock_llm:
        mock_llm.return_value.chat.completions.create.return_value = _mock_llm_response(answer)
        from backend.services.genai import answer_question
        result = answer_question("What deployment issues were discussed?", ["Alice: deployment failed"])
        assert isinstance(result, str)

def test_rag_query_integration():
    """Test full RAG pipeline with mocked retrieval and LLM."""
    mock_chunks = [
        {"text": "Kafka consumer lag was discussed", "metadata": {"meeting_id": "m1"}, "score": 0.92},
    ]
    with patch("backend.rag.retrieval.retrieve", return_value=mock_chunks), \
         patch("backend.rag.retrieval.answer_question", return_value="Kafka lag was the main issue"):
        from backend.rag.retrieval import rag_query
        result = rag_query("What was discussed about Kafka?", meeting_id="m1")
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) == 1
