"""
Enki Voice Conversation Engine — Production Server
===================================================
Real-time full-duplex conversational voice server combining:
1. OpenAI Whisper (STT audio transcription)
2. Gemini 2.0 Flash Lite Rotating Pool (Conversational Brain)
3. SQLite Knowledge Graph (Persistent Memory & Entity Recall)
4. Edge-TTS Neural Speech (Studio-grade low-latency TTS)
5. FastAPI + HTML5 Interactive HUD

Usage:
    python3 app.py
    Open http://localhost:8050 in browser
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

sys.path.insert(0, os.path.dirname(__file__))

from voice_brain import generate_voice_response, DB_PATH
from tts_engine import synthesize_speech_async, AUDIO_DIR
from stt_engine import transcribe_audio_bytes

app = FastAPI(
    title="Enki Voice Conversation Engine",
    description="Real-time voice dialogue agent with persistent knowledge graph memory",
    version="2.0.0"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Mount static files and audio cache
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    text: str
    history: Optional[List[ChatTurn]] = []
    use_neural_tts: Optional[bool] = True


@app.get("/")
def index():
    """Serve the Voice AI interactive interface."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Voice HUD index.html not found"}


@app.get("/audio/{filename}")
def serve_audio(filename: str):
    """Serve generated neural audio stream."""
    path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not found")


@app.post("/api/voice/chat")
async def voice_chat(req: ChatRequest):
    """
    Process transcribed text, query memory graph, think with Gemini,
    and synthesize crisp neural speech.
    """
    history_dicts = [{"role": h.role, "content": h.content} for h in (req.history or [])]
    reply = generate_voice_response(req.text, history_dicts)

    audio_url = None
    if req.use_neural_tts:
        try:
            audio_path = await synthesize_speech_async(reply)
            filename = os.path.basename(audio_path)
            audio_url = f"/audio/{filename}"
        except Exception as e:
            print(f"[TTS Error] {e}")

    return {
        "user_text": req.text,
        "reply": reply,
        "audio_url": audio_url
    }


@app.post("/api/voice/talk")
async def voice_talk(file: UploadFile = File(...)):
    """
    End-to-end audio pipeline:
    Audio File Upload -> Whisper STT -> Memory + Gemini Brain -> Neural TTS -> Audio Stream
    """
    contents = await file.read()
    suffix = os.path.splitext(file.filename or "recording.webm")[1] or ".webm"

    transcript = transcribe_audio_bytes(contents, suffix=suffix)
    if not transcript:
        return {
            "transcript": "",
            "reply": "I did not catch that. Could you repeat?",
            "audio_url": None
        }

    reply = generate_voice_response(transcript)
    audio_path = await synthesize_speech_async(reply)
    filename = os.path.basename(audio_path)

    return {
        "transcript": transcript,
        "reply": reply,
        "audio_url": f"/audio/{filename}"
    }


@app.get("/api/voice/health")
def voice_health():
    """Health status and telemetry."""
    return {
        "status": "online",
        "engine": "Enki Voice Core",
        "stt": "OpenAI Whisper",
        "tts": "Edge-TTS Neural (Christopher)",
        "llm": "gemini-flash-lite-latest",
        "knowledge_graph": DB_PATH
    }


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  🎙️  ENKI VOICE CONVERSATION ENGINE")
    print("  Interactive HUD: http://localhost:8050")
    print("  Health Status:   http://localhost:8050/api/voice/health")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8050)
