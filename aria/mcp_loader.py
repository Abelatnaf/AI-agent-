import json
from pathlib import Path

from aria.config import MCP_CONFIG_PATH


def load(path: Path | None = None) -> dict:
    """Load MCP server config from JSON. Returns empty dict if missing."""
    path = path or MCP_CONFIG_PATH
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {path}: {e}")

    # Support both `{...}` and `{"mcpServers": {...}}` shapes
    if "mcpServers" in data and isinstance(data["mcpServers"], dict):
        return data["mcpServers"]
    return data
