import argparse
import sys

import anyio
from dotenv import load_dotenv

from aria import mcp_loader
from aria.render import banner, error, info
from aria.runtime import check_api_key, run_once, run_repl
from aria.session import load_latest_session_id


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="aria",
        description="ARIA — your personal AI assistant.",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="One-shot prompt. Omit to start the interactive REPL.",
    )
    parser.add_argument(
        "--resume",
        help='Resume a prior session by id, or "last" for the most recent.',
    )
    parser.add_argument(
        "--no-mcp",
        action="store_true",
        help="Skip loading mcp_servers.json (faster startup).",
    )
    args = parser.parse_args()

    check_api_key()

    mcp_servers = {} if args.no_mcp else mcp_loader.load()
    if mcp_servers:
        info(f"loaded {len(mcp_servers)} MCP server(s): {', '.join(mcp_servers)}")

    resume = args.resume
    if resume == "last":
        resume = load_latest_session_id()
        if not resume:
            error("No prior session found.")
            sys.exit(1)
        info(f"resuming session {resume}")

    prompt = " ".join(args.prompt).strip()

    try:
        if prompt:
            anyio.run(run_once, prompt, mcp_servers, resume)
        else:
            banner()
            anyio.run(run_repl, mcp_servers, resume)
    except KeyboardInterrupt:
        info("\ninterrupted.")


if __name__ == "__main__":
    main()
