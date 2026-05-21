"""
Topic clustering using TF-IDF + KMeans.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

def cluster_topics(texts: list[str], n_clusters: int = 5) -> list[dict]:
    """
    Returns list of {cluster_id, label, texts} dicts.
    Automatically reduces n_clusters if fewer texts are provided.
    """
    if len(texts) < 2:
        return [{"cluster_id": 0, "label": texts[0] if texts else "empty", "texts": texts}]

    k = min(n_clusters, len(texts))
    vec = TfidfVectorizer(max_features=500, stop_words="english")
    X = vec.fit_transform(texts)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    # Extract top terms per cluster as label
    terms = vec.get_feature_names_out()
    clusters: dict[int, list[str]] = {i: [] for i in range(k)}
    for text, label in zip(texts, labels):
        clusters[int(label)].append(text)

    result = []
    for cid in range(k):
        center = km.cluster_centers_[cid]
        top_terms = [terms[i] for i in np.argsort(center)[-3:][::-1]]
        result.append({
            "cluster_id": cid,
            "label": ", ".join(top_terms),
            "texts": clusters[cid],
        })
    return result
