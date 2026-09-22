import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import TMP_DIR
import subprocess
import time
import re
import os

url_file = str(TMP_DIR / "active_tunnel_url.txt")
os.makedirs(os.path.dirname(url_file), exist_ok=True)

print("Starting cloudflared tunnel daemon...")
p = subprocess.Popen(
    ["/home/idrees/.local/bin/cloudflared", "tunnel", "--url", "http://localhost:5678"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

url_found = False
for line in iter(p.stdout.readline, ""):
    print(line, end="", flush=True)
    if not url_found:
        m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if m:
            url = m.group(0)
            with open(url_file, "w") as f:
                f.write(url.strip())
            print(f"\n===> ACTIVE TUNNEL URL WRITTEN TO {url_file}: {url} <===\n", flush=True)
            url_found = True

p.wait()
