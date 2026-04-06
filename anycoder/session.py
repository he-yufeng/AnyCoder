"""Session persistence - save and resume conversations."""

import json
import time
from pathlib import Path

SESSIONS_DIR = Path.home() / ".anycoder" / "sessions"


def save_session(
    messages: list[dict],
    model: str,
    session_id: str | None = None,
) -> str:
    """Save conversation to disk. Returns the session id."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if not session_id:
        session_id = f"session_{int(time.time())}"

    data = {
        "model": model,
        "messages": messages,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return session_id


def load_session(session_id: str) -> tuple[list[dict], str] | None:
    """Load a session. Returns (messages, model) or None."""
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None

    data = json.loads(path.read_text())
    return data["messages"], data["model"]


def list_sessions() -> list[dict]:
    """List saved sessions with metadata."""
    if not SESSIONS_DIR.exists():
        return []

    sessions = []
    for p in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text())
            msg_count = len(data.get("messages", []))
            sessions.append({
                "id": p.stem,
                "model": data.get("model", "?"),
                "messages": msg_count,
                "saved_at": data.get("saved_at", "?"),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions
