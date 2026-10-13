"""
Conversational Voice Brain
==========================
Generates concise, natural conversational responses tailored for spoken dialogue.
Queries and updates the SQLite Knowledge Graph in real time.
Uses the 6-key rotating pool targeting gemini-flash-lite-latest.
"""
import json
import os
import sqlite3
from google import genai

KEYS_FILE = "/home/idrees/Antigravity/job_agent/gemini_keys_pool.json"
MODEL_ID = "gemini-flash-lite-latest"
DB_PATH = "/home/idrees/Antigravity/storage/knowledge_graph.db"


def _get_key() -> str:
    """Retrieve next active key from the rotating pool."""
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                pool = json.load(f)
            keys = pool.get("active_keys", [])
            if keys:
                idx = pool.get("current_index", 0) % len(keys)
                pool["current_index"] = (idx + 1) % len(keys)
                with open(KEYS_FILE, "w") as f:
                    json.dump(pool, f, indent=2)
                return keys[idx]
        except Exception:
            pass
    return os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_PLACEHOLDER")


def get_relevant_memories(query: str) -> str:
    """Search knowledge graph for context related to words in the query."""
    if not os.path.exists(DB_PATH):
        return ""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Split query into words to search entities
        words = [w.strip() for w in query.split() if len(w.strip()) > 3]
        matches = []
        for word in words[:5]:
            cur.execute("SELECT name, entity_type, details FROM entities WHERE name LIKE ? OR details LIKE ? LIMIT 3", (f"%{word}%", f"%{word}%"))
            for row in cur.fetchall():
                matches.append(f"[{row['entity_type']}] {row['name']}: {row['details']}")

        cur.execute("SELECT source_entity, relation, target_entity FROM relations LIMIT 5")
        relations = [f"{r['source_entity']} -> {r['relation']} -> {r['target_entity']}" for r in cur.fetchall()]

        conn.close()
        out = ""
        if matches:
            out += "RELEVANT FACTS:\n" + "\n".join(matches[:4]) + "\n"
        if relations:
            out += "KNOWN RELATIONSHIPS:\n" + "\n".join(relations[:4]) + "\n"
        return out
    except Exception:
        return ""


def generate_voice_response(user_text: str, conversation_history: list = None) -> str:
    """
    Generate a spoken-optimized response.
    Constraints:
    - 1 to 3 punchy sentences.
    - Natural spoken rhythm, conversational and authoritative.
    - Zero markdown asterisks, hashes, or bullet points.
    """
    memory_context = get_relevant_memories(user_text)

    history_str = ""
    if conversation_history:
        for turn in conversation_history[-4:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_str += f"{role.upper()}: {content}\n"

    system_instruction = f"""You are Enki, autonomous AI system architect and technical execution partner for Idrees.
You are speaking out loud over real time voice audio.

CRITICAL VOICE INVARIANTS:
1. Speak in clean, direct spoken English.
2. Keep your response between 1 and 3 concise sentences. Never ramble.
3. NEVER use markdown symbols, bullet points, asterisks, or dashes. The text will be read directly by a speech synthesizer.
4. When technical questions or system status are asked, give the exact technical fact immediately.

{memory_context}

RECENT CONVERSATION:
{history_str}
"""

    keys = []
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                pool = json.load(f)
                keys = pool.get("active_keys", [])
        except Exception:
            pass
    if not keys:
        keys = [os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_PLACEHOLDER")]

    models_order = [MODEL_ID, "gemma-4-26b-a4b-it"]

    for key in keys:
        client = genai.Client(api_key=key, http_options={"timeout": 10000})
        for m_name in models_order:
            try:
                response = client.models.generate_content(
                    model=m_name,
                    contents=[system_instruction, f"USER SAID: {user_text}"],
                    config={"max_output_tokens": 180, "temperature": 0.4}
                )
                reply = response.text.strip()
                # Clean up any leftover asterisks or markdown symbols that ruin TTS
                reply = reply.replace("*", "").replace("#", "").replace("`", "").replace("-", " ")
                return reply
            except Exception as e:
                print(f"[Brain Error with {m_name} key ...{key[-6:]}] {e}")
                continue

    return "All systems are online, but model inference is experiencing peak latency. Please repeat your query."
