"""Tests for ML pipeline: sentiment, clustering, speaker analysis, anomaly detection."""
import pytest
from backend.ml.sentiment import score_text
from backend.ml.topic_clustering import cluster_topics
from backend.ml.speaker_analysis import analyze_speakers
from backend.ml.anomaly_detection import detect_anomalies
from backend.ml.engagement import compute_engagement_score

# ── Sentiment ──────────────────────────────────────────────────────────────────

def test_sentiment_positive():
    assert score_text("Great meeting, excellent progress, everything resolved") > 0

def test_sentiment_negative():
    assert score_text("Critical error, deployment failed, blocked by issue") < 0

def test_sentiment_neutral():
    assert score_text("The meeting started at 10am") == 0.0

def test_sentiment_range():
    score = score_text("good bad good bad")
    assert -1.0 <= score <= 1.0

# ── Topic Clustering ───────────────────────────────────────────────────────────

def test_cluster_topics_basic():
    texts = [
        "Kafka streaming pipeline delay",
        "Kafka consumer lag issue",
        "Deployment failed in staging",
        "CI/CD pipeline broken",
        "Action items from last sprint",
    ]
    clusters = cluster_topics(texts, n_clusters=2)
    assert len(clusters) == 2
    assert all("label" in c and "texts" in c for c in clusters)

def test_cluster_topics_single():
    clusters = cluster_topics(["only one text"])
    assert len(clusters) == 1

def test_cluster_topics_fewer_than_k():
    texts = ["text one", "text two"]
    clusters = cluster_topics(texts, n_clusters=5)
    assert len(clusters) == 2  # auto-reduced

# ── Speaker Analysis ───────────────────────────────────────────────────────────

SAMPLE_TRANSCRIPTS = [
    {"speaker": "Alice", "text": "We need to fix the Kafka lag issue", "sentiment_score": -0.5},
    {"speaker": "Bob", "text": "I agree, it is critical", "sentiment_score": -0.3},
    {"speaker": "Alice", "text": "Great, let us resolve it today", "sentiment_score": 0.8},
    {"speaker": "Charlie", "text": "I will handle the deployment", "sentiment_score": 0.2},
]

def test_speaker_analysis_names():
    stats = analyze_speakers(SAMPLE_TRANSCRIPTS)
    names = {s["name"] for s in stats}
    assert "Alice" in names and "Bob" in names and "Charlie" in names

def test_speaker_analysis_participation():
    stats = analyze_speakers(SAMPLE_TRANSCRIPTS)
    total_pct = sum(s["participation_pct"] for s in stats)
    assert abs(total_pct - 100.0) < 1.0  # should sum to ~100%

def test_speaker_analysis_turn_count():
    stats = analyze_speakers(SAMPLE_TRANSCRIPTS)
    alice = next(s for s in stats if s["name"] == "Alice")
    assert alice["turn_count"] == 2

# ── Anomaly Detection ──────────────────────────────────────────────────────────

def test_anomaly_detection_returns_list():
    transcripts = [
        {"speaker": "A", "text": "normal text here", "sentiment_score": 0.1},
        {"speaker": "B", "text": "another normal segment", "sentiment_score": 0.2},
        {"speaker": "C", "text": "x", "sentiment_score": -0.9},  # potential anomaly
        {"speaker": "A", "text": "good progress today", "sentiment_score": 0.5},
        {"speaker": "B", "text": "agreed on the plan", "sentiment_score": 0.3},
        {"speaker": "C", "text": "deployment is fine", "sentiment_score": 0.1},
    ]
    anomalies = detect_anomalies(transcripts)
    assert isinstance(anomalies, list)

def test_anomaly_detection_too_few():
    assert detect_anomalies([{"speaker": "A", "text": "hi", "sentiment_score": 0}]) == []

# ── Engagement Score ───────────────────────────────────────────────────────────

def test_engagement_score_range():
    speakers = [
        {"speaking_time_seconds": 120, "avg_sentiment": 0.3},
        {"speaking_time_seconds": 80, "avg_sentiment": 0.1},
    ]
    score = compute_engagement_score(speakers, anomaly_count=1, total_transcripts=10)
    assert 0 <= score <= 100

def test_engagement_score_empty():
    assert compute_engagement_score([], 0, 0) == 0.0
