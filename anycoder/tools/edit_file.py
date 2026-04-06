"""Search-and-replace editing, inspired by Claude Code's approach."""

import os
from anycoder.tools.base import BaseTool


class EditFileTool(BaseTool):
    name = "edit_file"
    description = (
        "Make targeted edits to a file by replacing exact string matches. "
        "The old_string must appear exactly once in the file (unless replace_all is true). "
        "Prefer this over write_file for modifying existing files."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to edit",
            },
            "old_string": {
                "type": "string",
                "description": "Exact text to search for",
            },
            "new_string": {
                "type": "string",
                "description": "Replacement text",
            },
            "replace_all": {
                "type": "boolean",
                "description": "Replace all occurrences instead of just one (default false)",
                "default": False,
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    }

    def execute(
        self, file_path: str, old_string: str, new_string: str,
        replace_all: bool = False, **kwargs
    ) -> str:
        path = os.path.expanduser(file_path)
        if not os.path.exists(path):
            return f"[error] File not found: {file_path}"

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"[error] {e}"

        count = content.count(old_string)
        if count == 0:
            return (
                f"[error] old_string not found in {file_path}. "
                "Make sure the string matches exactly, including whitespace and indentation."
            )

        if not replace_all and count > 1:
            return (
                f"[error] old_string appears {count} times in {file_path}. "
                "Provide more surrounding context to make it unique, "
                "or set replace_all=true to replace all occurrences."
            )

        new_content = content.replace(old_string, new_string) if replace_all else content.replace(
            old_string, new_string, 1
        )

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            return f"[error] {e}"

        replacements = count if replace_all else 1
        return f"Replaced {replacements} occurrence(s) in {file_path}"
