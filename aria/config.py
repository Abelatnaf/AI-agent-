from pathlib import Path

import os

MODEL = os.environ.get("ARIA_MODEL", "claude-opus-4-5")
FALLBACK_MODEL = "claude-sonnet-4-5"

SESSIONS_DIR = Path.home() / ".aria" / "sessions"
LATEST_SESSION_FILE = Path.home() / ".aria" / "latest.json"

MCP_CONFIG_PATH = Path("mcp_servers.json")

ALLOWED_TOOLS = [
    "Bash",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "WebSearch",
    "WebFetch",
]

PERMISSION_MODE = "acceptEdits"
