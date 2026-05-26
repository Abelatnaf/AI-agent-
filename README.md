# ARIA

**Adaptive Resource & Intelligence Agent** — a personal AI assistant that handles the full spectrum of your day-to-day tasks: writing, research, code, planning, file ops, web lookups, communications. Powered by Claude via the official [`claude-agent-sdk`](https://pypi.org/project/claude-agent-sdk/).

ARIA leads with output, executes immediately rather than describing, and chains tools (Bash, file edits, web search, MCP integrations) to actually finish what you ask for.

## Install

Requires Python 3.10+.

```bash
pip install -e .
```

## Configure

1. Copy the env template and add your Anthropic API key:
   ```bash
   cp .env.example .env
   # then edit .env and set ANTHROPIC_API_KEY=sk-ant-...
   ```

2. (Optional) Wire up MCP integrations — Calendar, Gmail, Notion, etc.:
   ```bash
   cp mcp_servers.json.example mcp_servers.json
   # then edit mcp_servers.json with your credentials
   ```
   Without this file, ARIA still works fine — it just won't have those integrations.

3. (Optional) Override the model:
   ```bash
   export ARIA_MODEL=claude-sonnet-4-5   # default is claude-opus-4-5
   ```

## Use

**One-shot:**
```bash
aria "summarize my calendar for tomorrow and draft a slack message about my schedule"
aria "search the web for the latest Python release and save the answer to notes.txt"
aria "review the diff on the current branch and flag anything risky"
```

**Interactive REPL:**
```bash
aria
```
Slash commands inside the REPL: `/exit`, `/reset`, `/save`, `/resume <session-id>`.

**Resume your last session:**
```bash
aria --resume last
```

## What ARIA can do

Out of the box, ARIA can:

- **Run shell commands** (`Bash`) — for code tasks, git, file operations, anything CLI
- **Read/write/edit files** (`Read`, `Write`, `Edit`, `Glob`, `Grep`)
- **Search and fetch the web** (`WebSearch`, `WebFetch`)
- **Connect to MCP servers** you configure — Google Calendar, Gmail, Notion, Linear, Slack, etc.

All chat sessions are logged as JSONL to `~/.aria/sessions/`, so nothing is lost.

## Tests

```bash
pip install -e .[dev]
pytest
```

## Project layout

```
aria/
├── cli.py            # argparse entry, REPL vs one-shot
├── runtime.py        # builds ClaudeAgentOptions, drives client
├── config.py         # model + paths + tool allowlist
├── mcp_loader.py     # reads mcp_servers.json
├── session.py        # JSONL session log + resume
├── render.py         # rich-based terminal rendering
└── prompts/
    └── system.md     # ARIA role spec
```
