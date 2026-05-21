"""
Speaker activity analysis — computes participation metrics from transcript rows.
"""
from collections import defaultdict
from datetime import datetime

def analyze_speakers(transcripts: list[dict]) -> list[dict]:
    """
    transcripts: list of {speaker, text, timestamp, sentiment_score}
    Returns list of {name, speaking_time_seconds, turn_count, avg_sentiment, participation_pct}
    """
    stats: dict[str, dict] = defaultdict(lambda: {
        "turn_count": 0, "word_count": 0, "sentiments": []
    })
    for t in transcripts:
        sp = t.get("speaker", "Unknown")
        stats[sp]["turn_count"] += 1
        stats[sp]["word_count"] += len(t.get("text", "").split())
        if t.get("sentiment_score") is not None:
            stats[sp]["sentiments"].append(t["sentiment_score"])

    total_words = sum(s["word_count"] for s in stats.values()) or 1
    result = []
    for name, s in stats.items():
        avg_sent = round(sum(s["sentiments"]) / len(s["sentiments"]), 3) if s["sentiments"] else 0.0
        result.append({
            "name": name,
            "speaking_time_seconds": round(s["word_count"] / 2.5, 1),  # ~150 wpm
            "turn_count": s["turn_count"],
            "avg_sentiment": avg_sent,
            "participation_pct": round(s["word_count"] / total_words * 100, 1),
        })
    return sorted(result, key=lambda x: x["speaking_time_seconds"], reverse=True)
