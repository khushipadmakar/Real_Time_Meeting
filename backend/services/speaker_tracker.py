"""
Simple energy-based speaker turn detection.
In production, replace with a diarization model (e.g., pyannote.audio).
"""
import numpy as np

class SpeakerTracker:
    def __init__(self):
        self._speakers: list[str] = []
        self._current_idx = 0

    def register_speakers(self, names: list[str]):
        self._speakers = names

    def detect_speaker(self, audio_bytes: bytes) -> str:
        """
        Assign speaker label based on audio energy level.
        Returns 'Speaker N' labels when no diarization model is available.
        """
        audio = np.frombuffer(audio_bytes, dtype=np.float32)
        if audio.size == 0:
            return "Unknown"
        energy = float(np.sqrt(np.mean(audio ** 2)))
        # Rotate through registered speakers or use energy buckets
        if self._speakers:
            idx = self._current_idx % len(self._speakers)
            self._current_idx += 1
            return self._speakers[idx]
        # Fallback: bucket by energy
        if energy > 0.1:
            return "Speaker 1"
        elif energy > 0.05:
            return "Speaker 2"
        return "Speaker 3"
