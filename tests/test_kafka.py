"""Tests for Kafka producer (mocked) and consumer handler logic."""
import pytest
import json
from unittest.mock import patch, MagicMock

def test_publish_event_calls_produce():
    mock_producer = MagicMock()
    with patch("backend.kafka.producer._get_producer", return_value=mock_producer):
        from backend.kafka.producer import publish_event
        payload = {"meeting_id": "m1", "text": "hello"}
        publish_event("meeting.transcripts", payload)
        mock_producer.produce.assert_called_once()
        call_kwargs = mock_producer.produce.call_args
        assert call_kwargs[0][0] == "meeting.transcripts"
        assert json.loads(call_kwargs[1]["value"].decode()) == payload

def test_publish_event_handles_kafka_error():
    """publish_event should not raise even if Kafka is down."""
    mock_producer = MagicMock()
    mock_producer.produce.side_effect = Exception("Kafka unavailable")
    with patch("backend.kafka.producer._get_producer", return_value=mock_producer):
        from backend.kafka.producer import publish_event
        # Should not raise
        publish_event("meeting.transcripts", {"meeting_id": "m1", "text": "test"})

def test_on_transcript_handler():
    """Consumer transcript handler should not raise on valid payload."""
    from backend.kafka.consumers import on_transcript
    payload = {"meeting_id": "m1", "speaker": "Alice", "text": "Great progress today"}
    on_transcript(payload)  # should not raise

def test_on_alert_handler():
    from backend.kafka.consumers import on_alert
    on_alert({"meeting_id": "m1", "anomalies": 3})  # should not raise
