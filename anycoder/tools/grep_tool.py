"""Search file contents with regex."""

import os
import re
import glob as globlib
from anycoder.tools.base import BaseTool


class GrepTool(BaseTool):
    name = "grep"
    description = (
        "Search for a regex pattern in file contents. "
        "Returns matching lines with file paths and line numbers."
    )
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex pattern to search for",
            },
            "path": {
                "type": "string",
                "description": "File or directory to search in (default: cwd)",
                "default": ".",
            },
            "file_pattern": {
                "type": "string",
                "description": "Glob pattern to filter files, e.g. '*.py' (default: all files)",
                "default": "**/*",
            },
        },
        "required": ["pattern"],
    }

    def execute(
        self, pattern: str, path: str = ".", file_pattern: str = "**/*", **kwargs
    ) -> str:
        base = os.path.expanduser(path)

        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"[error] Invalid regex: {e}"

        # single file
        if os.path.isfile(base):
            return self._search_file(base, regex)

        # directory search
        full_glob = os.path.join(base, file_pattern)
        files = sorted(globlib.glob(full_glob, recursive=True))
        files = [f for f in files if os.path.isfile(f)]

        results = []
        match_count = 0
        for fpath in files:
            if match_count >= 500:
                results.append("\n... stopping at 500 matches")
                break
            file_result = self._search_file(fpath, regex)
            if file_result:
                results.append(file_result)
                match_count += file_result.count("\n") + 1

        if not results:
            return f"No matches for: {pattern}"
        return "\n\n".join(results)

    def _search_file(self, fpath: str, regex) -> str | None:
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except (PermissionError, IsADirectoryError, OSError):
            return None

        matches = []
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                matches.append(f"  {i}: {line.rstrip()}")

        if not matches:
            return None
        return f"{fpath}\n" + "\n".join(matches)
