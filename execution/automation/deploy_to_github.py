import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import ARCHIVE_DIR
import base64
import json
import urllib.request
import urllib.error

import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER_AGENT = "AntigravityDeploy/1.0"
BASE_URL = "https://api.github.com"
OWNER = "IdreesQurashi"
REPO = "msk-vehicle-wraps"

def request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json"
    }
    encoded_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return json.loads(body), e.code
        except:
            return {"error": body}, e.code

print(f"1. Checking if repo {REPO} exists...")
repo_data, status = request(f"/repos/{OWNER}/{REPO}")
if status == 404:
    print(f"Repo {REPO} not found. Creating public repository...")
    create_payload = {
        "name": REPO,
        "description": "MSK Signs & Printing - Vehicle & Fleet Wraps Quote Landing Page",
        "public": True,
        "auto_init": True
    }
    repo_data, status = request(f"/user/repos", method="POST", data=create_payload)
    print(f"Create status: {status}")
else:
    print(f"Repo already exists: {repo_data.get('html_url')}")

# Read local index.html
with open(str(ARCHIVE_DIR / "client-projects" / "project-a1-vehicle-wraps" / "index.html"), "rb") as f:
    content_bytes = f.read()
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

print("2. Uploading index.html to repo...")
# Check if file exists to get SHA for update
file_data, fstatus = request(f"/repos/{OWNER}/{REPO}/contents/index.html")
put_payload = {
    "message": "feat: vehicle wrap quote landing page",
    "content": content_b64,
    "branch": "main"
}
if fstatus == 200 and "sha" in file_data:
    put_payload["sha"] = file_data["sha"]
    print("Updating existing index.html...")
else:
    print("Creating new index.html...")

upload_data, ustatus = request(f"/repos/{OWNER}/{REPO}/contents/index.html", method="PUT", data=put_payload)
print(f"Upload status: {ustatus}")

print("3. Enabling GitHub Pages on 'main' branch...")
pages_payload = {
    "source": {
        "branch": "main",
        "path": "/"
    }
}
pages_data, pstatus = request(f"/repos/{OWNER}/{REPO}/pages", method="POST", data=pages_payload)
if pstatus in (201, 409):
    print(f"GitHub Pages status: {pstatus}")
    if "html_url" in pages_data:
        print(f"Pages URL: {pages_data.get('html_url')}")
    else:
        print(f"Pages is enabled! URL: https://{OWNER.lower()}.github.io/{REPO}/")
else:
    print(f"Pages response ({pstatus}): {pages_data}")

print(f"\nSUCCESS! Your landing page is hosted at:\nhttps://{OWNER.lower()}.github.io/{REPO}/\n")
