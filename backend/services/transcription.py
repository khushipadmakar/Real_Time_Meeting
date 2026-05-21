"""
Transcription service using faster-whisper (Python 3.13 compatible).
"""
import tempfile
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from backend.config import settings

_model: WhisperModel | None = None

def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model

def transcribe_audio_bytes(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
    if audio_np.size == 0:
        return ""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio_np, sample_rate)
        segments, _ = get_model().transcribe(f.name, language=None)  # auto-detect language
    return " ".join(s.text for s in segments).strip()

def transcribe_file(path: str) -> str:
    segments, _ = get_model().transcribe(path)
    return " ".join(s.text for s in segments).strip()
