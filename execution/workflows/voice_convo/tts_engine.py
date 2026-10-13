"""
Neural Text-to-Speech Engine
============================
Generates natural conversational audio using Edge-TTS.
Default voice: en-US-ChristopherNeural (crisp, professional male)
Alternative: en-US-AriaNeural (expressive female)
"""
import asyncio
import edge_tts
import os
import tempfile
import uuid

AUDIO_DIR = "/home/idrees/Antigravity/storage/voice_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

DEFAULT_VOICE = "en-US-ChristopherNeural"


async def synthesize_speech_async(text: str, voice: str = DEFAULT_VOICE) -> str:
    """Synthesizes text into an MP3 file and returns the file path."""
    if not text.strip():
        text = "I am listening."

    filename = f"reply_{uuid.uuid4().hex[:10]}.mp3"
    out_path = os.path.join(AUDIO_DIR, filename)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)
    return out_path


def synthesize_speech(text: str, voice: str = DEFAULT_VOICE) -> str:
    """Synchronous wrapper for synthesize_speech_async."""
    return asyncio.run(synthesize_speech_async(text, voice))
