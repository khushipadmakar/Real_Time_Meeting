"""
Anomaly detection for meeting engagement using Isolation Forest.
Detects unusual silence gaps, sentiment drops, or participation imbalances.
"""
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_anomalies(transcripts: list[dict]) -> list[dict]:
    """
    transcripts: list of {speaker, text, timestamp, sentiment_score}
    Returns list of anomalous transcript entries with anomaly_score.
    """
    if len(transcripts) < 5:
        return []

    features = []
    for t in transcripts:
        word_count = len(t.get("text", "").split())
        sentiment = t.get("sentiment_score") or 0.0
        features.append([word_count, sentiment])

    X = np.array(features)
    clf = IsolationForest(contamination=0.1, random_state=42)
    preds = clf.fit_predict(X)
    scores = clf.score_samples(X)

    anomalies = []
    for i, (pred, score) in enumerate(zip(preds, scores)):
        if pred == -1:
            anomalies.append({**transcripts[i], "anomaly_score": round(float(score), 4)})
    return anomalies
