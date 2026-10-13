#!/usr/bin/env python3
"""
Indeed Master MCP Server for Antigravity
Exposes authenticated Indeed job search, details, and employer research tools.
Handles automatic token refresh via local OAuth token cache.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("IndeedEngine")

TOKEN_CACHE_FILE = "/home/idrees/.gemini/antigravity/indeed_tokens.json"
CLIENT_CACHE_FILE = "/home/idrees/.gemini/antigravity/indeed_client.json"
INDEED_MCP_URL = "https://mcp.indeed.com/claude/mcp"
TOKEN_ENDPOINT = "https://apis.indeed.com/oauth/v2/tokens"


def _load_tokens() -> Dict[str, Any]:
    if not os.path.exists(TOKEN_CACHE_FILE):
        raise RuntimeError("No tokens found. Run indeed_auth.py first.")
    with open(TOKEN_CACHE_FILE, "r") as f:
        return json.load(f)


def _save_tokens(tokens: Dict[str, Any]):
    os.makedirs(os.path.dirname(TOKEN_CACHE_FILE), exist_ok=True)
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def _get_valid_access_token() -> str:
    tokens = _load_tokens()
    obtained_at = tokens.get("obtained_at", 0)
    expires_in = tokens.get("expires_in", 3600)
    refresh_token = tokens.get("refresh_token")
    client_id = tokens.get("client_id")

    # If within 120 seconds of expiry, refresh
    if time.time() > (obtained_at + expires_in - 120):
        if not refresh_token:
            return tokens.get("access_token", "")
        
        payload = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with httpx.Client(timeout=20.0) as client:
            resp = client.post(TOKEN_ENDPOINT, data=payload, headers=headers)
            if resp.status_code == 200:
                new_tokens = resp.json()
                new_tokens["obtained_at"] = time.time()
                new_tokens["client_id"] = client_id
                if "refresh_token" not in new_tokens:
                    new_tokens["refresh_token"] = refresh_token
                _save_tokens(new_tokens)
                return new_tokens["access_token"]
            else:
                # Fallback to current access token if refresh fails temporarily
                return tokens.get("access_token", "")

    return tokens.get("access_token", "")


def _rpc_call(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    token = _get_valid_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {}
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(INDEED_MCP_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        return resp.json()


@mcp.tool()
def indeed_status() -> str:
    """Check connectivity to Indeed MCP server and OAuth token state."""
    try:
        tokens = _load_tokens()
        obtained_at = tokens.get("obtained_at", 0)
        expires_in = tokens.get("expires_in", 3600)
        remaining = int((obtained_at + expires_in) - time.time())
        client_id = tokens.get("client_id", "unknown")
        
        # Test call to remote MCP
        test_resp = _rpc_call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "AntigravityIndeedClient", "version": "1.0"}
        })
        
        status = {
            "status": "ready" if "result" in test_resp else "error",
            "client_id": client_id,
            "token_remaining_seconds": max(0, remaining),
            "remote_initialize": test_resp
        }
        return json.dumps(status, indent=2)
    except Exception as e:
        return json.dumps({"status": "unauthenticated", "error": str(e)}, indent=2)


@mcp.tool()
def list_indeed_remote_tools() -> str:
    """Discover all raw tools published by Indeed MCP server."""
    try:
        resp = _rpc_call("tools/list")
        return json.dumps(resp, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def call_indeed_remote_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a raw tool on Indeed MCP server.
    
    Args:
        tool_name: The name of the remote tool on Indeed (e.g. search_jobs, get_job_details).
        arguments: Dictionary of arguments required by the tool.
    """
    try:
        resp = _rpc_call("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return json.dumps(resp, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    mcp.run()

