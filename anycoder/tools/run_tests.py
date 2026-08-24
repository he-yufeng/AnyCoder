"""Run the project's tests and feed the failures back to the agent."""

import json
import os
import subprocess
from anycoder.tools.base import BaseTool


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def _detect_command(path: str) -> str | None:
    """Pick a test command for the project at path, None if nothing is recognizable."""
    # Python first: pytest signs in any config file settle it
    pyproject = _read(os.path.join(path, "pyproject.toml"))
    setup_cfg = _read(os.path.join(path, "setup.cfg"))
    if (
        os.path.isfile(os.path.join(path, "pytest.ini"))
        or "pytest" in pyproject
        or "pytest" in setup_cfg
    ):
        return "pytest -q"
    # Python project without pytest hints: probe once, let the output speak
    if (
        pyproject
        or setup_cfg
        or os.path.isfile(os.path.join(path, "setup.py"))
        or os.path.isdir(os.path.join(path, "tests"))
        or os.path.isdir(os.path.join(path, "test"))
    ):
        return "python -m pytest -q"
    # Node: scripts.test, but the default "no test specified" placeholder doesn't count
    pkg_file = os.path.join(path, "package.json")
    if os.path.isfile(pkg_file):
        try:
            pkg = json.loads(_read(pkg_file))
        except json.JSONDecodeError:
            pkg = {}
        script = pkg.get("scripts", {}).get("test", "")
        if script and "no test specified" not in script:
            if os.path.isfile(os.path.join(path, "pnpm-lock.yaml")):
                return "pnpm test"
            if os.path.isfile(os.path.join(path, "yarn.lock")):
                return "yarn test"
            return "npm test"
    return None


class RunTestsTool(BaseTool):
    name = "run_tests"
    description = (
        "Run the project's test suite and report the outcome, failures included. "
        "Detects pytest (Python) or npm/pnpm/yarn test (Node) automatically. "
        "Use after changing code: if anything fails, fix it and re-run until green."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project directory whose tests to run (default: cwd)",
                "default": ".",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default 300)",
                "default": 300,
            },
        },
        "required": [],
    }

    def execute(self, path: str = ".", timeout: int = 300, **kwargs) -> str:
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.isdir(path):
            return f"[error] Not a directory: {path}"

        cmd = _detect_command(path)
        if cmd is None:
            return (
                "Could not detect a test setup here (no pytest config, Python project "
                "files, or package.json scripts.test). Run the tests via bash instead."
            )

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=path,
            )
        except subprocess.TimeoutExpired:
            return f"[error] Tests timed out after {timeout}s (`{cmd}`)"
        except Exception as e:
            return f"[error] {e}"

        out = result.stdout or ""
        if result.stderr:
            out += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            out += f"\n[exit code: {result.returncode}]"

        # failure details pile up at the tail, so keep more of it than the head
        if len(out) > 15_000:
            out = (
                out[:4000]
                + f"\n\n... truncated ({len(out)} chars total) ...\n\n"
                + out[-8000:]
            )
        return f"$ {cmd}\n" + (out.strip() or "(no output)")
