"""Anchored patch editing: several exact-match replacements in one atomic call.

The search-and-replace editor handles one hunk at a time; multi-hunk edits
through it either take several round trips or risk a half-applied series when
a later hunk fails to match. ``apply_patch`` takes a list of anchored blocks,
checks every anchor up front, and writes only when all of them match exactly
once — no partial patches on disk.

Block format (Aider-style, easy for the model to produce reliably):

    <<<<<<< SEARCH
    text to find
    =======
    replacement text
    >>>>>>> REPLACE
"""

import os
from typing import ClassVar

from anycoder.checkpoints import record as _record_checkpoint
from anycoder.tools.base import BaseTool
from anycoder.tools.edit_file import _unified_diff

_MARK_SEARCH = "<<<<<<< SEARCH"
_MARK_DIVIDE = "======="
_MARK_REPLACE = ">>>>>>> REPLACE"


def _parse_blocks(patch: str) -> list[tuple[str, str]] | str:
    """Split the patch text into (old, new) blocks, or return an error string."""
    blocks: list[tuple[str, str]] = []
    lines = patch.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip() != _MARK_SEARCH:
            i += 1
            continue
        try:
            divide = lines.index(_MARK_DIVIDE, i + 1)
            end = lines.index(_MARK_REPLACE, divide + 1)
        except ValueError:
            return "[error] unterminated SEARCH block; every block needs ======= and >>>>>>> REPLACE"
        old = "\n".join(lines[i + 1 : divide])
        new = "\n".join(lines[divide + 1 : end])
        blocks.append((old, new))
        i = end + 1
    if not blocks:
        return "[error] no SEARCH blocks found in the patch"
    return blocks


class ApplyPatchTool(BaseTool):
    name = "apply_patch"
    description = (
        "Apply several exact-match replacements to one file atomically. "
        "Every SEARCH anchor must appear exactly once or the whole patch is "
        "rejected and nothing is written. Prefer this for multi-hunk edits."
    )
    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file to patch"},
            "patch": {
                "type": "string",
                "description": "Blocks of <<<<<<< SEARCH / ======= / >>>>>>> REPLACE",
            },
        },
        "required": ["file_path", "patch"],
    }

    def execute(self, file_path: str, patch: str, **kwargs) -> str:
        path = os.path.expanduser(file_path)
        if not os.path.exists(path):
            return f"[error] File not found: {file_path}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:  # noqa: BLE001
            return f"[error] {e}"

        blocks = _parse_blocks(patch)
        if isinstance(blocks, str):
            return blocks

        # check every anchor before writing anything: exact-once, and no two
        # blocks may overlap the same span
        spans: list[tuple[int, int]] = []
        for old, _new in blocks:
            count = content.count(old)
            if count == 0:
                return f"[error] SEARCH block not found in {file_path}:\n{old[:200]}"
            if count > 1:
                return f"[error] SEARCH block matches {count} times in {file_path}:\n{old[:200]}"
            start = content.index(old)
            spans.append((start, start + len(old)))
        for (a0, a1), (b0, b1) in zip(sorted(spans), sorted(spans)[1:]):
            if b0 < a1:
                return "[error] SEARCH blocks overlap; split them into separate patches"

        new_content = content
        for old, new in blocks:
            new_content = new_content.replace(old, new, 1)

        try:
            _record_checkpoint(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:  # noqa: BLE001
            return f"[error] {e}"

        diff = _unified_diff(content, new_content, file_path)
        return f"Patched {file_path} ({len(blocks)} blocks)\n{diff}"
