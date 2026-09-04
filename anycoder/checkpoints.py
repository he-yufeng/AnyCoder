"""Session-scoped undo for file mutations.

edit_file and write_file record a checkpoint before touching a file; /undo
pops the latest one and restores the previous bytes (or removes the file if
it did not exist). In-memory only: undo history dies with the process, and
bash side effects are not tracked, only the two file-writing tools.
"""

import os

# (path, prior bytes or None if the file did not exist)
_stack: list[tuple[str, bytes | None]] = []


def record(path: str) -> None:
    """Capture the pre-mutation state of path. Call right before writing."""
    prior = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            prior = f.read()
    _stack.append((path, prior))


def undo() -> str:
    """Restore the most recent checkpoint."""
    if not _stack:
        return "Nothing to undo."
    path, prior = _stack.pop()
    if prior is None:
        if os.path.exists(path):
            os.remove(path)
        return f"Removed {path} (created this session)."
    with open(path, "wb") as f:
        f.write(prior)
    return f"Restored {path}."


def pending() -> int:
    return len(_stack)


def clear() -> None:
    _stack.clear()
