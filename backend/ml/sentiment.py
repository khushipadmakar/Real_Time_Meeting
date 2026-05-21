"""
Sentiment scoring using a simple lexicon-based approach (no external API needed).
Returns a float in [-1, 1].
"""
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_POS = {"good","great","excellent","positive","happy","success","well","agree","perfect","love","nice","helpful","productive","resolved","done","completed"}
_NEG = {"bad","poor","issue","problem","fail","failed","error","wrong","disagree","concern","delay","blocked","stuck","critical","urgent","broken"}

def score_text(text: str) -> float:
    words = set(text.lower().split()) - ENGLISH_STOP_WORDS
    pos = len(words & _POS)
    neg = len(words & _NEG)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 3)
