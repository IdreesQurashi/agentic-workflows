"""
Whisper Speech-to-Text Engine
=============================
Transcribes audio files and microphone blobs into clean text.
Supports wav, mp3, ogg, webm, and m4a formats.
"""
import os
import tempfile
import whisper

_MODEL = None


def get_whisper_model():
    """Lazy load Whisper model on first request."""
    global _MODEL
    if _MODEL is None:
        print("[STT] Loading Whisper base model...")
        _MODEL = whisper.load_model("base")
        print("[STT] Whisper base model ready.")
    return _MODEL


def transcribe_audio_file(file_path: str) -> str:
    """Transcribe an audio file from disk."""
    if not os.path.exists(file_path):
        return ""
    try:
        model = get_whisper_model()
        result = model.transcribe(file_path, fp16=False)
        text = result.get("text", "").strip()
        return text
    except Exception as e:
        print(f"[STT Error] {e}")
        return ""


def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".webm") -> str:
    """Save audio bytes to a temp file and transcribe with Whisper."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        text = transcribe_audio_file(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return text
