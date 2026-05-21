"""
Engagement scoring — combines participation balance, sentiment, and anomaly rate
into a single 0-100 score.
"""
import numpy as np

def compute_engagement_score(speaker_stats: list[dict], anomaly_count: int, total_transcripts: int) -> float:
    if not speaker_stats or total_transcripts == 0:
        return 0.0

    # Participation balance (Gini coefficient, lower = more balanced = better)
    times = np.array([s["speaking_time_seconds"] for s in speaker_stats])
    if times.sum() == 0:
        balance_score = 0.0
    else:
        times_sorted = np.sort(times)
        n = len(times_sorted)
        gini = (2 * np.sum((np.arange(1, n+1)) * times_sorted) / (n * times_sorted.sum())) - (n + 1) / n
        balance_score = max(0.0, 1.0 - gini)

    # Average sentiment (map [-1,1] → [0,1])
    avg_sent = np.mean([s["avg_sentiment"] for s in speaker_stats])
    sentiment_score = (avg_sent + 1) / 2

    # Anomaly penalty
    anomaly_rate = anomaly_count / total_transcripts
    anomaly_score = max(0.0, 1.0 - anomaly_rate * 5)

    score = (balance_score * 0.4 + sentiment_score * 0.4 + anomaly_score * 0.2) * 100
    return round(float(score), 1)
