import os
import shutil
import glob
import subprocess
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PCMaster")

HOME_DIR = "/home/idrees"

@mcp.tool()
def read_system_file(file_path: str, max_lines: int = 200) -> str:
    """Read the contents of any file on your computer."""
    try:
        path = os.path.expanduser(file_path)
        if not os.path.exists(path):
            return f"File does not exist: {path}"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            return "".join(lines)
    except Exception as e:
        return f"Error reading file {file_path}: {e}"

@mcp.tool()
def write_system_file(file_path: str, content: str) -> str:
    """Create or overwrite any file on your computer with the specified content."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully written to: {path}"
    except Exception as e:
        return f"Error writing file {file_path}: {e}"

@mcp.tool()
def search_pc_files(folder: str = "/home/idrees", pattern: str = "*", max_results: int = 25) -> str:
    """Search for files and directories matching a pattern anywhere on your PC."""
    try:
        base = os.path.expanduser(folder)
        matches = []
        for root, dirs, files in os.walk(base):
            for name in files + dirs:
                if pattern.lower() in name.lower() or pattern == "*":
                    matches.append(os.path.join(root, name))
                    if len(matches) >= max_results:
                        break
            if len(matches) >= max_results:
                break
        return "\n".join(matches) if matches else f"No files matching '{pattern}' in {folder}"
    except Exception as e:
        return f"File search error: {e}"

@mcp.tool()
def get_system_health() -> str:
    """Check real time CPU, RAM, Disk space, and system uptime of your computer."""
    try:
        total, used, free = shutil.disk_usage(HOME_DIR)
        disk_gb = f"Disk Used: {used // (2**30)} GB / {total // (2**30)} GB (Free: {free // (2**30)} GB)"
        
        mem_info = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout
        uptime_info = subprocess.run(["uptime", "-p"], capture_output=True, text=True).stdout.strip()
        
        output = [
            "=== PC System Health ===",
            f"Uptime: {uptime_info}",
            f"{disk_gb}",
            "Memory:\n" + mem_info.strip()
        ]
        return "\n".join(output)
    except Exception as e:
        return f"System health error: {e}"

if __name__ == "__main__":
    mcp.run()
