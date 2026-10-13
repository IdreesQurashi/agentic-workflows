#!/usr/bin/env python3
"""
Claude Code Master MCP Server
=============================
Autonomous MCP server for controlling, auditing, executing, and configuring
Claude Code (Anthropic CLI) and its underlying 9-key Gemini LiteLLM rotating proxy.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ClaudeCodeMaster")

CLAUDE_BIN = "/home/idrees/.local/bin/claude"
PROXY_BASE_URL = "http://127.0.0.1:4000"
PROXY_DIR = "/home/idrees/Antigravity/claude_proxy"
START_PROXY_SCRIPT = "/home/idrees/Antigravity/claude_proxy/start_claude_proxy.sh"
PROXY_LOG = "/home/idrees/Antigravity/claude_proxy/litellm.log"
CLAUDE_HOME = "/home/idrees/.claude"
CLAUDE_JSON_STATE = "/home/idrees/.claude.json"


def _get_claude_env() -> Dict[str, str]:
    """Return environment variables configured to route Claude Code through local LiteLLM."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = PROXY_BASE_URL
    env["ANTHROPIC_API_KEY"] = "dummy"
    return env


@mcp.tool()
def claude_execute_task(
    prompt: str,
    cwd: str = "/home/idrees",
    danger_mode: bool = True,
    timeout_seconds: int = 180,
    model: str = "",
    extra_flags: str = ""
) -> str:
    """Execute a task non interactively using Claude Code CLI routed through the local Gemini proxy.
    
    Args:
        prompt: The command or natural language instruction for Claude Code.
        cwd: Working directory to run the task in (defaults to /home/idrees).
        danger_mode: If True, bypasses interactive permission prompts using --dangerously-skip-permissions.
        timeout_seconds: Maximum seconds before terminating the execution (default 180).
        model: Optional model override (e.g. 'claude-sonnet-5' or 'claude-opus-5').
        extra_flags: Additional CLI flags to pass to claude.
    """
    if not os.path.exists(CLAUDE_BIN):
        return f"Error: Claude Code binary not found at {CLAUDE_BIN}"

    working_dir = os.path.expanduser(cwd)
    if not os.path.exists(working_dir):
        return f"Error: Working directory does not exist: {working_dir}"

    cmd = [CLAUDE_BIN, "-p", prompt]
    if danger_mode:
        cmd.append("--dangerously-skip-permissions")
    if model.strip():
        cmd.extend(["--model", model.strip()])
    if extra_flags.strip():
        cmd.extend(extra_flags.strip().split())

    try:
        proc = subprocess.run(
            cmd,
            cwd=working_dir,
            env=_get_claude_env(),
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        output = proc.stdout.strip()
        err = proc.stderr.strip()
        status_line = f"[Exit Code: {proc.returncode}]"

        result = [status_line]
        if output:
            result.append(output)
        if err:
            result.append(f"[STDERR]\n{err}")

        return "\n\n".join(result) if result else "Execution completed with no output."
    except subprocess.TimeoutExpired:
        return f"Error: Claude Code task timed out after {timeout_seconds} seconds."
    except Exception as e:
        return f"Execution Error: {e}"


@mcp.tool()
def claude_get_system_status() -> str:
    """Inspect complete real time status of Claude Code CLI and its LiteLLM proxy engine."""
    report = []

    # 1. Claude CLI Check
    if os.path.exists(CLAUDE_BIN):
        try:
            ver = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True, text=True, timeout=5)
            version_str = ver.stdout.strip() if ver.returncode == 0 else "Unknown version"
        except Exception as e:
            version_str = f"Error querying version: {e}"
        report.append(f"Claude Code Binary: {CLAUDE_BIN} ({version_str})")
    else:
        report.append(f"Claude Code Binary: MISSING at {CLAUDE_BIN}")

    # 2. LiteLLM Proxy Process Check
    try:
        ps_check = subprocess.run(["pgrep", "-fa", "litellm"], capture_output=True, text=True, timeout=5)
        if ps_check.stdout.strip():
            pids = [line.split()[0] for line in ps_check.stdout.strip().splitlines()]
            report.append(f"LiteLLM Proxy: RUNNING (PID: {', '.join(pids)}) on {PROXY_BASE_URL}")
        else:
            report.append("LiteLLM Proxy: STOPPED (not running)")
    except Exception as e:
        report.append(f"LiteLLM Proxy Check Error: {e}")

    # 3. Key Pool Check
    key_pool_file = os.path.join(PROXY_DIR, "claude_proxy_keys.env")
    if os.path.exists(key_pool_file):
        with open(key_pool_file, "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip().startswith("CLAUDE_GEMINI_KEY")]
        report.append(f"Gemini Key Pool: {len(keys)} active Google accounts configured")
    else:
        report.append("Gemini Key Pool: config file missing")

    # 4. Global Settings & Permissions
    settings_file = os.path.join(CLAUDE_HOME, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            mode = data.get("permissions", {}).get("defaultMode", "standard")
            report.append(f"Default Permission Mode: {mode}")
            report.append(f"Theme: {data.get('theme', 'dark')} | Output Style: {data.get('outputStyle', 'standard')}")
        except Exception as e:
            report.append(f"Settings Read Error: {e}")

    # 5. Skills and Plugins
    skills_dir = os.path.join(CLAUDE_HOME, "skills")
    if os.path.exists(skills_dir):
        skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
        report.append(f"Installed Skills ({len(skills)}): {', '.join(skills) if skills else 'none'}")

    return "\n".join(report)


@mcp.tool()
def claude_manage_proxy(action: str = "status") -> str:
    """Manage the LiteLLM rotating proxy that feeds Claude Code.
    
    Args:
        action: One of 'status', 'start', 'restart', 'stop', or 'logs'.
    """
    act = action.strip().lower()

    if act == "status":
        try:
            ps_check = subprocess.run(["pgrep", "-fa", "litellm"], capture_output=True, text=True, timeout=5)
            if ps_check.stdout.strip():
                return f"LiteLLM Proxy is ACTIVE.\nProcesses:\n{ps_check.stdout.strip()}"
            return "LiteLLM Proxy is currently INACTIVE."
        except Exception as e:
            return f"Status check error: {e}"

    elif act in ("start", "restart"):
        try:
            subprocess.run(["pkill", "-f", "litellm"], capture_output=True)
            res = subprocess.run(["bash", START_PROXY_SCRIPT], capture_output=True, text=True, timeout=10)
            return f"LiteLLM Proxy restarted successfully.\nOutput:\n{res.stdout.strip()}"
        except Exception as e:
            return f"Failed to restart proxy: {e}"

    elif act == "stop":
        try:
            subprocess.run(["pkill", "-f", "litellm"], capture_output=True)
            return "LiteLLM Proxy process terminated."
        except Exception as e:
            return f"Failed to stop proxy: {e}"

    elif act == "logs":
        if not os.path.exists(PROXY_LOG):
            return f"Log file not found: {PROXY_LOG}"
        try:
            res = subprocess.run(["tail", "-n", "50", PROXY_LOG], capture_output=True, text=True, timeout=5)
            return f"Last 50 lines of {PROXY_LOG}:\n\n{res.stdout.strip()}"
        except Exception as e:
            return f"Error reading logs: {e}"

    return f"Unknown action: '{action}'. Permitted actions: status, start, restart, stop, logs."


@mcp.tool()
def claude_run_doctor(cwd: str = "/home/idrees") -> str:
    """Run 'claude doctor' health checkup to diagnose environment, settings, and permissions."""
    if not os.path.exists(CLAUDE_BIN):
        return f"Error: Claude Code binary not found at {CLAUDE_BIN}"

    working_dir = os.path.expanduser(cwd)
    try:
        proc = subprocess.run(
            [CLAUDE_BIN, "doctor"],
            cwd=working_dir,
            env=_get_claude_env(),
            capture_output=True,
            text=True,
            timeout=30
        )
        return proc.stdout.strip() or proc.stderr.strip() or "Claude doctor completed with no output."
    except Exception as e:
        return f"Doctor execution error: {e}"


@mcp.tool()
def claude_list_sessions() -> str:
    """List recent Claude Code sessions, projects, and token metrics."""
    if not os.path.exists(CLAUDE_JSON_STATE):
        return "No Claude Code state file found at ~/.claude.json"

    try:
        with open(CLAUDE_JSON_STATE, "r", encoding="utf-8") as f:
            data = json.load(f)

        projects = data.get("projects", {})
        output = [f"Registered Projects in State ({len(projects)}):"]
        for ppath, details in projects.items():
            last_sess = details.get("lastSessionId", "none")
            last_ver = details.get("lastVersionBase", "unknown")
            output.append(f"\nProject: {ppath}")
            output.append(f"  Last Session ID: {last_sess}")
            output.append(f"  Version: {last_ver}")
            allowed = details.get("allowedTools", [])
            output.append(f"  Allowed Tools: {', '.join(allowed) if allowed else 'default'}")

        return "\n".join(output)
    except Exception as e:
        return f"Error reading sessions: {e}"


@mcp.tool()
def claude_read_config(target: str = "all") -> str:
    """Read configuration files for Claude Code.
    
    Args:
        target: 'global_settings', 'mcp_servers', 'claude_md', 'project_state', or 'all'.
    """
    t = target.strip().lower()
    files_map = {
        "global_settings": os.path.join(CLAUDE_HOME, "settings.json"),
        "mcp_servers": os.path.join(CLAUDE_HOME, "mcp.json"),
        "claude_md": os.path.join(CLAUDE_HOME, "CLAUDE.md"),
        "project_state": CLAUDE_JSON_STATE,
    }

    if t in files_map:
        fpath = files_map[t]
        if not os.path.exists(fpath):
            return f"File does not exist: {fpath}"
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            return f"--- {fpath} ---\n" + f.read()

    result = []
    for name, fpath in files_map.items():
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    preview = content if len(content) < 1500 else content[:1500] + "\n...[truncated]"
                    result.append(f"=== {name.upper()} ({fpath}) ===\n{preview}")
            except Exception as e:
                result.append(f"=== {name.upper()} ({fpath}) ===\nRead error: {e}")
    return "\n\n".join(result)


@mcp.tool()
def claude_manage_mcp_servers(
    action: str = "list",
    server_name: str = "",
    command: str = "",
    args_json: str = "[]",
    env_json: str = "{}"
) -> str:
    """Inspect or update MCP servers configured specifically inside Claude Code (~/.claude/mcp.json).
    
    Args:
        action: 'list', 'add', or 'remove'.
        server_name: Identifier for the server.
        command: Command to execute (for 'add').
        args_json: JSON list of string arguments (for 'add').
        env_json: JSON object of environment variables (for 'add').
    """
    config_file = os.path.join(CLAUDE_HOME, "mcp.json")
    act = action.strip().lower()

    if not os.path.exists(config_file):
        data = {"mcpServers": {}}
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return f"Error loading {config_file}: {e}"

    if "mcpServers" not in data:
        data["mcpServers"] = {}

    if act == "list":
        return json.dumps(data.get("mcpServers", {}), indent=2)

    elif act == "remove":
        if not server_name:
            return "Error: server_name is required for 'remove'."
        if server_name in data["mcpServers"]:
            del data["mcpServers"][server_name]
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return f"Server '{server_name}' successfully removed from Claude Code MCP configuration."
        return f"Server '{server_name}' not found in Claude Code MCP configuration."

    elif act == "add":
        if not server_name or not command:
            return "Error: server_name and command are required for 'add'."
        try:
            parsed_args = json.loads(args_json) if args_json.strip() else []
            parsed_env = json.loads(env_json) if env_json.strip() else {}
        except Exception as e:
            return f"Invalid JSON in args or env: {e}"

        entry = {"command": command, "args": parsed_args}
        if parsed_env:
            entry["env"] = parsed_env

        data["mcpServers"][server_name] = entry
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return f"Server '{server_name}' successfully configured in Claude Code."

    return f"Unknown action: '{action}'. Permitted actions: list, add, remove."


@mcp.tool()
def claude_get_architecture_knowledge() -> str:
    """Return exhaustive architectural reference, operational guidelines, and CLI patterns for Claude Code."""
    return """Claude Code Architecture & Knowledge Base:

1. Runtime & Environment:
   * Binary: /home/idrees/.local/bin/claude (v2.1.275+)
   * Local Proxy: LiteLLM running on port 4000 (http://127.0.0.1:4000)
   * Auth Bridge: ANTHROPIC_BASE_URL="http://127.0.0.1:4000", ANTHROPIC_API_KEY="dummy"
   * Model Routing: Inbound Claude requests (Opus 5, Sonnet 5) route to a 9-account rotating pool of Gemini 2.5/Flash-Lite keys, preventing quota exhaustion.

2. CLI Execution Patterns:
   * Non-interactive execution: claude -p "<prompt>" --dangerously-skip-permissions
   * Session resumption: claude -r [session_id]
   * Background agents: claude agents, claude attach <id>, claude stop <id>, claude rm <id>
   * System health check: claude doctor
   * Worktrees: claude -w <branch_name>

3. Configuration Hierarchy:
   * User Global Settings: ~/.claude/settings.json (Theme, workflows, auto permission modes)
   * User Global MCP: ~/.claude/mcp.json (MCP servers accessible to Claude Code)
   * User Global Directives: ~/.claude/CLAUDE.md
   * State & History: ~/.claude.json (Machine ID, project permissions, allowedTools)
   * Project Local Overrides: .claude/settings.local.json
   * Installed Skills: ~/.claude/skills/

4. Permission System:
   * Modes: acceptEdits, auto, bypassPermissions, manual, dontAsk, plan
   * Standard CLI Flag for Autonomous Mode: --dangerously-skip-permissions
   * Config File Allow Rules: Bash, Edit, Write, Read, Glob, Grep, WebFetch, WebSearch, mcp__*
"""

if __name__ == "__main__":
    mcp.run()
