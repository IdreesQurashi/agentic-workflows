import sqlite3
import os
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MemoryGraph")

DB_DIR = "/home/idrees/Antigravity/storage"
DB_PATH = os.path.join(DB_DIR, "knowledge_graph.db")

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            entity_type TEXT NOT NULL,
            details TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_entity TEXT NOT NULL,
            relation TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@mcp.tool()
def store_memory_fact(name: str, entity_type: str, details: str) -> str:
    """Store or update a persistent fact about a person, company, client, strategy, or project."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO entities (name, entity_type, details, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET
                details = excluded.details,
                entity_type = excluded.entity_type,
                updated_at = CURRENT_TIMESTAMP
        """, (name, entity_type, details))
        conn.commit()
        conn.close()
        return f"Persistent memory stored for '{name}' ({entity_type})."
    except Exception as e:
        return f"Error storing memory: {e}"

@mcp.tool()
def recall_memory(search_term: str) -> str:
    """Recall facts, relationships, and history about any person, company, or topic."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM entities 
            WHERE name LIKE ? OR details LIKE ? OR entity_type LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        entities = cur.fetchall()
        
        cur.execute("""
            SELECT * FROM relations 
            WHERE source_entity LIKE ? OR target_entity LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        relations = cur.fetchall()
        
        conn.close()
        
        if not entities and not relations:
            return f"No memories found matching '{search_term}'."
            
        results = [f"=== Memories for '{search_term}' ==="]
        for e in entities:
            results.append(f"• [{e['entity_type']}] {e['name']}: {e['details']}")
            
        if relations:
            results.append("\n=== Relationships ===")
            for r in relations:
                results.append(f"• {r['source_entity']} -> {r['relation']} -> {r['target_entity']}")
                
        return "\n".join(results)
    except Exception as e:
        return f"Error recalling memory: {e}"

@mcp.tool()
def link_memory_entities(source_entity: str, relation: str, target_entity: str) -> str:
    """Create a relationship edge between two entities in the knowledge graph."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO relations (source_entity, relation, target_entity)
            VALUES (?, ?, ?)
        """, (source_entity, relation, target_entity))
        conn.commit()
        conn.close()
        return f"Linked '{source_entity}' -> [{relation}] -> '{target_entity}'"
    except Exception as e:
        return f"Error linking entities: {e}"

if __name__ == "__main__":
    mcp.run()
