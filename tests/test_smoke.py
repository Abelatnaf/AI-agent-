"""Smoke tests that don't hit the Anthropic API."""

import json
from pathlib import Path

import pytest


def test_system_prompt_loads():
    from aria.runtime import load_system_prompt

    text = load_system_prompt()
    assert "ARIA" in text
    assert "Adaptive Resource & Intelligence Agent" in text
    assert len(text) > 500


def test_mcp_loader_missing_file_returns_empty(tmp_path: Path):
    from aria import mcp_loader

    assert mcp_loader.load(tmp_path / "nope.json") == {}


def test_mcp_loader_reads_flat_dict(tmp_path: Path):
    from aria import mcp_loader

    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({
        "calendar": {"type": "stdio", "command": "echo", "args": ["hi"]},
    }))
    result = mcp_loader.load(cfg)
    assert "calendar" in result
    assert result["calendar"]["command"] == "echo"


def test_mcp_loader_reads_mcpservers_wrapper(tmp_path: Path):
    from aria import mcp_loader

    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({
        "mcpServers": {
            "notion": {"type": "stdio", "command": "npx", "args": []},
        }
    }))
    result = mcp_loader.load(cfg)
    assert "notion" in result


def test_build_options_has_aria_prompt(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    from aria.runtime import build_options

    opts = build_options(mcp_servers={})
    assert "ARIA" in opts.system_prompt
    assert "Bash" in opts.allowed_tools
    assert "WebSearch" in opts.allowed_tools
    assert opts.permission_mode == "acceptEdits"


def test_cli_errors_without_api_key(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from aria.runtime import check_api_key

    with pytest.raises(SystemExit):
        check_api_key()
