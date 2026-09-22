import json
import re

transcript_path = "/home/idrees/.gemini/antigravity/brain/f615aab0-1333-425f-871a-fbc5627d4e84/.system_generated/logs/transcript_full.jsonl"
handles = set()

with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            found = re.findall(r'@([a-zA-Z0-9._]+)', content)
            handles.update(found)

import os
os.makedirs("/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp", exist_ok=True)
output_path = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp/instagram_handles.txt"
with open(output_path, 'w') as f:
    for handle in sorted(handles):
        f.write(handle + "\n")

print(f"Extracted {len(handles)} unique handles to {output_path}")
