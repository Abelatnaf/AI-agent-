import os
from importlib import resources

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    query,
)

from aria import config
from aria.render import error, info, render_message
from aria.session import SessionLog


def load_system_prompt() -> str:
    """Read aria/prompts/system.md from the installed package."""
    return resources.files("aria.prompts").joinpath("system.md").read_text(encoding="utf-8")


def build_options(
    mcp_servers: dict,
    resume: str | None = None,
) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=load_system_prompt(),
        model=config.MODEL,
        allowed_tools=config.ALLOWED_TOOLS,
        permission_mode=config.PERMISSION_MODE,
        mcp_servers=mcp_servers,
        cwd=os.getcwd(),
        resume=resume,
    )


async def run_once(prompt: str, mcp_servers: dict, resume: str | None = None) -> None:
    """Single-shot: send one prompt, stream the response, exit."""
    log = SessionLog()
    options = build_options(mcp_servers, resume=resume)
    log.record_message("user", {"text": prompt})
    async for message in query(prompt=prompt, options=options):
        log.record_message(type(message).__name__, message)
        if isinstance(message, ResultMessage) and message.session_id:
            log.set_session_id(message.session_id)
        render_message(message)


async def run_repl(mcp_servers: dict, resume: str | None = None) -> None:
    """Interactive REPL backed by ClaudeSDKClient (multi-turn session)."""
    from rich.prompt import Prompt

    log = SessionLog()
    options = build_options(mcp_servers, resume=resume)

    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = Prompt.ask("[bold magenta]you[/bold magenta]")
            except (EOFError, KeyboardInterrupt):
                info("\nbye.")
                return

            text = user_input.strip()
            if not text:
                continue

            if text in ("/exit", "/quit"):
                info("bye.")
                return
            if text == "/reset":
                await client.disconnect()
                await client.connect()
                info("session reset.")
                continue
            if text.startswith("/resume "):
                new_id = text.split(maxsplit=1)[1].strip()
                await client.disconnect()
                options = build_options(mcp_servers, resume=new_id)
                # Reconnect with new options
                client._options = options  # type: ignore[attr-defined]
                await client.connect()
                info(f"resumed session {new_id}.")
                continue
            if text == "/save":
                info(f"session log: {log.path}")
                continue

            log.record_message("user", {"text": text})
            await client.query(text)
            async for message in client.receive_response():
                log.record_message(type(message).__name__, message)
                if isinstance(message, ResultMessage) and message.session_id:
                    log.set_session_id(message.session_id)
                render_message(message)


def check_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        error(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your environment or a .env file (see .env.example)."
        )
        raise SystemExit(1)
