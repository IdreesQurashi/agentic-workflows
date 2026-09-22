"""
_root.py: Workspace root anchor and canonical path resolver.
Import this in any script to resolve paths to workspace root,
regardless of which directory the script lives in or what CWD is set.
"""
from pathlib import Path

# Resolves to Agentic Workflows root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Data directory trees
DATA_DIR = ROOT_DIR / "data"
DATA_LEADS_DIR = DATA_DIR / "leads"
DATA_DOSSIERS_DIR = DATA_DIR / "dossiers"
DATA_WORKFLOWS_DIR = DATA_DIR / "workflows"

# Harness and temp directories
HARNESS_DIR = ROOT_DIR / "harness"
TMP_DIR = ROOT_DIR / ".tmp"
ARCHIVE_DIR = ROOT_DIR / "archive"

# Auth and config files at root
ENV_FILE = ROOT_DIR / ".env"
CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
TOKEN_FILE = ROOT_DIR / "token.json"

# Canonical lead data paths
LEADS_100K = DATA_LEADS_DIR / "filtered_leads_100k.csv"
LEADS_100_IG = DATA_LEADS_DIR / "100_instagram_leads.csv"
LEADS_QUALIFIED = DATA_LEADS_DIR / "final_qualified_leads.csv"
LEADS_FILTERED = DATA_LEADS_DIR / "filtered_instagrams.csv"
LEADS_DB = DATA_LEADS_DIR / "instagram_leads.db"
URLS_FILE = DATA_LEADS_DIR / "urls.txt"

# External client work paths
MAK_DIR = Path("/home/idrees/MAK")
MSK_DOCS_DIR = Path("/home/idrees/Documents/MSK")
CLIENT_PROJECTS_DIR = ARCHIVE_DIR / "client-projects"
