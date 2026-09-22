"""
_root.py: Workspace root anchor and canonical path resolver.
Import this in any script to resolve paths to workspace root,
regardless of which directory the script lives in or what CWD is set.
"""
from pathlib import Path

# Resolves to Agentic Workflows root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Core DOE architecture paths
DIRECTIVES_DIR = ROOT_DIR / "directives"
ORCHESTRATION_DIR = ROOT_DIR / "orchestration"
EXECUTION_DIR = ROOT_DIR / "execution"
HARNESS_DIR = ROOT_DIR / "harness"
LEGACY_DIR = ROOT_DIR / "legacy_archive"
TMP_DIR = ROOT_DIR / ".tmp"

# Data and client archive resolution with legacy fallback
DATA_DIR = ROOT_DIR / "data" if (ROOT_DIR / "data").exists() else (LEGACY_DIR / "data")
DATA_LEADS_DIR = DATA_DIR / "leads"
DATA_DOSSIERS_DIR = DATA_DIR / "dossiers"
DATA_WORKFLOWS_DIR = DATA_DIR / "workflows"
ARCHIVE_DIR = ROOT_DIR / "archive" if (ROOT_DIR / "archive").exists() else (LEGACY_DIR / "archive")

# Auth and config files at root
ENV_FILE = ROOT_DIR / ".env"
CREDENTIALS_FILE = ROOT_DIR / "credentials.json" if (ROOT_DIR / "credentials.json").exists() else (LEGACY_DIR / "credentials.json")
TOKEN_FILE = ROOT_DIR / "token.json" if (ROOT_DIR / "token.json").exists() else (LEGACY_DIR / "token.json")

# External client work paths
MAK_DIR = Path("/home/idrees/MAK")
MSK_DOCS_DIR = Path("/home/idrees/Documents/MSK")
CLIENT_PROJECTS_DIR = ARCHIVE_DIR / "client-projects"
