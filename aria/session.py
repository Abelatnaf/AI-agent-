import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from aria.config import LATEST_SESSION_FILE, SESSIONS_DIR


class SessionLog:
    """Append-only JSONL log for one ARIA session."""

    def __init__(self, directory: Path = SESSIONS_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.path = directory / f"{ts}.jsonl"
        self.session_id: str | None = None

    def append(self, event: dict[str, Any]) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(event, default=_to_jsonable) + "\n")

    def record_message(self, kind: str, message: Any) -> None:
        self.append({
            "ts": datetime.now().isoformat(),
            "kind": kind,
            "message": _to_jsonable(message),
        })

    def set_session_id(self, session_id: str) -> None:
        if session_id and session_id != self.session_id:
            self.session_id = session_id
            LATEST_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            LATEST_SESSION_FILE.write_text(json.dumps({
                "session_id": session_id,
                "log": str(self.path),
                "updated": datetime.now().isoformat(),
            }))


def load_latest_session_id() -> str | None:
    if not LATEST_SESSION_FILE.exists():
        return None
    try:
        return json.loads(LATEST_SESSION_FILE.read_text()).get("session_id")
    except (json.JSONDecodeError, OSError):
        return None


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in asdict(obj).items()}
    if hasattr(obj, "__dict__"):
        return {k: _to_jsonable(v) for k, v in vars(obj).items() if not k.startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return repr(obj)
