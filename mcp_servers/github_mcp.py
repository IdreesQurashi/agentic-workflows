import json
import urllib.request
import urllib.parse
import base64
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GitHubEngine")

import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")")
USER_AGENT = "AntigravityGitHubMCP/1.0"
BASE_URL = "https://api.github.com"

def _request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json"
    }
    encoded_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

@mcp.tool()
def list_repositories(username: str = "IdreesQurashi") -> str:
    """List all GitHub repositories for IdreesQurashi with description, stars, and URL."""
    try:
        repos = _request(f"/users/{username}/repos?sort=updated")
        output = [f"=== GitHub Repositories for {username} ==="]
        for r in repos:
            output.append(f"• {r['name']} ({r.get('visibility', 'public')})")
            output.append(f"  Description: {r.get('description') or 'No description'}")
            output.append(f"  URL: {r['html_url']}")
            output.append(f"  Stars: {r['stargazers_count']} | Forks: {r['forks_count']}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing repos: {e}"

@mcp.tool()
def get_repo_details(repo_name: str, owner: str = "IdreesQurashi") -> str:
    """Get metadata, default branch, open issues count, and latest commit info for a repository."""
    try:
        repo = _request(f"/repos/{owner}/{repo_name}")
        commits = _request(f"/repos/{owner}/{repo_name}/commits?per_page=1")
        latest_sha = commits[0]["sha"][:7] if commits else "None"
        latest_msg = commits[0]["commit"]["message"].split("\n")[0] if commits else "None"
        return f"Repo: {repo['full_name']}\nDefault Branch: {repo['default_branch']}\nOpen Issues: {repo['open_issues_count']}\nLatest Commit: [{latest_sha}] {latest_msg}\nURL: {repo['html_url']}"
    except Exception as e:
        return f"Error getting repo details: {e}"

@mcp.tool()
def read_github_file(repo_name: str, file_path: str, branch: str = "main", owner: str = "IdreesQurashi") -> str:
    """Read any file directly from a GitHub repository via API."""
    try:
        data = _request(f"/repos/{owner}/{repo_name}/contents/{file_path}?ref={branch}")
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
    except Exception as e:
        return f"Error reading file from GitHub: {e}"

@mcp.tool()
def create_github_issue(repo_name: str, title: str, body: str, owner: str = "IdreesQurashi") -> str:
    """Create a new issue on a GitHub repository."""
    try:
        data = {"title": title, "body": body}
        res = _request(f"/repos/{owner}/{repo_name}/issues", method="POST", data=data)
        return f"Issue created: #{res['number']} - {res['html_url']}"
    except Exception as e:
        return f"Error creating issue: {e}"

if __name__ == "__main__":
    mcp.run()
