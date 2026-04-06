"""Execute shell commands."""

import subprocess
from anycoder.tools.base import BaseTool


class BashTool(BaseTool):
    name = "bash"
    description = (
        "Execute a shell command and return its output. "
        "Use for running tests, installing packages, git operations, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default 120)",
                "default": 120,
            },
        },
        "required": ["command"],
    }

    def execute(self, command: str, timeout: int = 120, **kwargs) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=None,  # uses the process cwd
            )
            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout)
            if result.stderr:
                output_parts.append(f"[stderr]\n{result.stderr}")
            if result.returncode != 0:
                output_parts.append(f"[exit code: {result.returncode}]")

            output = "\n".join(output_parts) if output_parts else "(no output)"
            # don't flood the context with huge outputs
            if len(output) > 50000:
                output = output[:25000] + "\n\n... (truncated) ...\n\n" + output[-25000:]
            return output

        except subprocess.TimeoutExpired:
            return f"[error] Command timed out after {timeout}s"
        except Exception as e:
            return f"[error] {e}"
