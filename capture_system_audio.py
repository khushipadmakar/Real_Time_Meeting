"""
Capture system audio (Teams/Meet) and stream to backend for real-time transcription.
Transcripts are saved to DB and appear live on dashboard.

Install: pip install sounddevice websocket-client numpy requests
Usage:
  python capture_system_audio.py --list-devices
  python capture_system_audio.py --meeting-id <id> --device <index>
"""
import argparse
import json
import threading
import numpy as np
import sounddevice as sd
import websocket
import requests

SAMPLE_RATE = 16000
CHUNK_SAMPLES = SAMPLE_RATE * 5  # 5 seconds — better accuracy
SILENCE_THRESHOLD = 0.01  # skip chunks below this energy level
BACKEND = "http://localhost:9000"
WS_URL = "ws://localhost:9000/ws/audio/{meeting_id}"

def list_devices():
    print("\nAvailable audio input devices:")
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            print(f"  [{i}] {d['name']}")
    print("\n→ Use 'CABLE Output (VB-Audio)' for Teams/Meet system audio")

def save_transcript(meeting_id, speaker, text):
    """Save transcript to DB so dashboard shows it."""
    try:
        requests.post(f"{BACKEND}/transcripts/", json={
            "meeting_id": meeting_id,
            "speaker": speaker,
            "text": text,
        }, timeout=5)
    except Exception:
        pass

def capture_and_stream(meeting_id: str, device: int | None):
    url = WS_URL.format(meeting_id=meeting_id)
    ws = websocket.WebSocket()
    ws.connect(url)
    print(f"\n✅ Connected — capturing audio for meeting: {meeting_id}")
    print("Speak now... Press Ctrl+C to stop.\n")

    buffer = np.array([], dtype=np.float32)
    lock = threading.Lock()

    def callback(indata, frames, time, status):
        nonlocal buffer
        mono = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        with lock:
            buffer = np.concatenate([buffer, mono])
            while len(buffer) >= CHUNK_SAMPLES:
                chunk = buffer[:CHUNK_SAMPLES].copy()
                buffer = buffer[CHUNK_SAMPLES:]
                # Skip silent chunks — prevents Whisper hallucination
                energy = float(np.sqrt(np.mean(chunk ** 2)))
                if energy > SILENCE_THRESHOLD:
                    ws.send_binary(chunk.tobytes())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                        device=device, callback=callback, blocksize=1024):
        try:
            while True:
                msg = ws.recv()
                if msg:
                    data = json.loads(msg)
                    speaker = data.get('speaker', 'Speaker')
                    text = data.get('text', '')
                    print(f"[{speaker}] {text}")
                    # Save to DB → dashboard auto-refreshes every 3s
                    threading.Thread(
                        target=save_transcript,
                        args=(meeting_id, speaker, text),
                        daemon=True
                    ).start()
        except KeyboardInterrupt:
            print("\n⏹ Stopped.")
            ws.send("END")
            ws.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--meeting-id", default="")
    parser.add_argument("--device", type=int, default=None)
    parser.add_argument("--list-devices", action="store_true")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
    elif not args.meeting_id:
        print("Usage:")
        print("  python capture_system_audio.py --list-devices")
        print("  python capture_system_audio.py --meeting-id <id> --device <index>")
    else:
        capture_and_stream(args.meeting_id, args.device)
