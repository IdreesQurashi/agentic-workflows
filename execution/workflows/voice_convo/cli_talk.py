#!/usr/bin/env python3
"""
CLI Voice Terminal — Speak and Listen in Terminal
=================================================
Allows conversational voice interaction directly from the Linux terminal.
Synthesizes neural speech and plays it out loud via ffplay.

Usage:
    python3 cli_talk.py "Who is Marcus Vance?"
    python3 cli_talk.py --interactive
"""
import sys
import os
import subprocess
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from voice_brain import generate_voice_response
from tts_engine import synthesize_speech


def speak_text(text: str):
    """Synthesize neural voice and play out loud via ffplay."""
    try:
        mp3_path = synthesize_speech(text)
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", mp3_path],
            check=True
        )
    except Exception as e:
        print(f"[Audio Playback Error] {e}")


def converse(prompt: str, history: list = None):
    print(f"\n[You]: {prompt}")
    reply = generate_voice_response(prompt, history)
    print(f"[Enki]: {reply}\n")
    print("▶ Speaking response through audio device...")
    speak_text(reply)
    return reply


def interactive_loop():
    print("\n" + "=" * 60)
    print("  🎙️  ENKI VOICE CLI — INTERACTIVE CONVERSATION")
    print("  Type your prompt and press Enter. Enki will speak.")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 60 + "\n")

    history = []
    while True:
        try:
            user_input = input("[You]: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Session terminated.")
                break

            reply = converse(user_input, history)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enki CLI Voice Terminal")
    parser.add_argument("query", nargs="?", default="", help="Single question to ask Enki")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch continuous voice dialogue loop")

    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_loop()
    else:
        converse(args.query)
