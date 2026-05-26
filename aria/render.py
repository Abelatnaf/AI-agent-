from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

console = Console()


def render_message(message: Any) -> None:
    """Render a Claude Agent SDK message to the terminal."""
    # Lazy import so the SDK isn't required at module import time (helps tests)
    from claude_agent_sdk import (
        AssistantMessage,
        ResultMessage,
        SystemMessage,
        UserMessage,
    )

    if isinstance(message, AssistantMessage):
        _render_assistant(message)
    elif isinstance(message, UserMessage):
        _render_user(message)
    elif isinstance(message, ResultMessage):
        _render_result(message)
    elif isinstance(message, SystemMessage):
        pass  # quiet — system events go to the log only


def _render_assistant(message: Any) -> None:
    from claude_agent_sdk import TextBlock, ThinkingBlock, ToolUseBlock

    for block in getattr(message, "content", []) or []:
        if isinstance(block, TextBlock):
            text = (block.text or "").strip()
            if text:
                console.print(Markdown(text))
                console.print()
        elif isinstance(block, ToolUseBlock):
            preview = _format_tool_input(block.input)
            console.print(Panel(
                preview,
                title=f"[dim]→ {block.name}[/dim]",
                border_style="cyan",
                padding=(0, 1),
            ))
        elif isinstance(block, ThinkingBlock):
            pass  # don't surface thinking by default


def _render_user(message: Any) -> None:
    from claude_agent_sdk import ToolResultBlock

    for block in getattr(message, "content", []) or []:
        if isinstance(block, ToolResultBlock):
            content = block.content
            if isinstance(content, list):
                content = "".join(
                    getattr(c, "text", "") if not isinstance(c, dict) else c.get("text", "")
                    for c in content
                )
            content = str(content or "").strip()
            if content:
                short = content if len(content) < 600 else content[:600] + "…"
                style = "red" if block.is_error else "dim"
                console.print(Text(short, style=style))
                console.print()


def _render_result(message: Any) -> None:
    cost = getattr(message, "total_cost_usd", None)
    sid = getattr(message, "session_id", None)
    parts = []
    if cost is not None:
        parts.append(f"cost ${cost:.4f}")
    if sid:
        parts.append(f"session {sid}")
    if parts:
        console.print(Text("  ".join(parts), style="dim"))


def _format_tool_input(payload: Any) -> str:
    if not payload:
        return ""
    if isinstance(payload, dict):
        items = []
        for k, v in payload.items():
            val = str(v)
            if len(val) > 200:
                val = val[:200] + "…"
            items.append(f"[bold]{k}[/bold]: {val}")
        return "\n".join(items)
    return str(payload)


def banner() -> None:
    console.print(Panel(
        Text.from_markup(
            "[bold]ARIA[/bold] — Adaptive Resource & Intelligence Agent\n"
            "[dim]/exit  /reset  /resume <id>[/dim]"
        ),
        border_style="magenta",
    ))


def info(msg: str) -> None:
    console.print(Text(msg, style="dim"))


def error(msg: str) -> None:
    console.print(Text(msg, style="bold red"))
