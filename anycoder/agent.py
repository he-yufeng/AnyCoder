"""Core agent loop - the brain that ties LLM, tools, and context together."""

import json
from typing import Generator

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from anycoder.llm import LLMClient
from anycoder.context import ContextManager
from anycoder.config import Config
from anycoder.tools import TOOL_MAP, get_tool_schemas
from anycoder.prompts.system import build_system_prompt


console = Console()


class Agent:
    """The agentic loop: user message -> LLM -> tool calls -> repeat."""

    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(
            model=config.model,
            api_base=config.api_base,
            api_key=config.api_key,
        )
        self.ctx = ContextManager(
            llm=self.llm,
            max_tokens=config.max_tokens,
            compress_threshold=config.compress_threshold,
        )
        # init with system prompt
        self.ctx.add({"role": "system", "content": build_system_prompt()})
        self.tool_schemas = get_tool_schemas()

    def run(self, user_input: str):
        """Process one user turn - may involve multiple LLM calls for tool use."""
        self.ctx.add({"role": "user", "content": user_input})

        for iteration in range(self.config.max_iterations):
            # check if we need to compress
            if self.ctx.needs_compression():
                console.print("[dim]Compressing context...[/dim]")
                self.ctx.compress()

            # call the LLM
            response_text = ""
            tool_calls = []

            try:
                for chunk in self.llm.chat(
                    messages=self.ctx.get_messages(),
                    tools=self.tool_schemas,
                    stream=True,
                ):
                    if chunk["type"] == "text":
                        # stream text to terminal
                        console.print(chunk["content"], end="", highlight=False)
                        response_text += chunk["content"]
                    elif chunk["type"] == "tool_call":
                        tool_calls = chunk["calls"]
            except Exception as e:
                console.print(f"\n[red]LLM error: {e}[/red]")
                # still record what we got
                if response_text:
                    self.ctx.add({"role": "assistant", "content": response_text})
                return

            # finish the text output with a newline
            if response_text:
                console.print()

            if not tool_calls:
                # pure text response, we're done
                self.ctx.add({"role": "assistant", "content": response_text})
                return

            # record assistant message with tool calls
            assistant_msg = {"role": "assistant", "content": response_text or None}
            assistant_msg["tool_calls"] = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"]),
                    },
                }
                for tc in tool_calls
            ]
            self.ctx.add(assistant_msg)

            # execute each tool
            for tc in tool_calls:
                self._execute_tool(tc)

        console.print(f"[yellow]Hit iteration limit ({self.config.max_iterations})[/yellow]")

    def _execute_tool(self, tool_call: dict):
        """Run a single tool call and add the result to context."""
        name = tool_call["name"]
        args = tool_call["arguments"]
        call_id = tool_call["id"]

        tool = TOOL_MAP.get(name)
        if not tool:
            result = f"[error] Unknown tool: {name}"
            console.print(f"[red]Unknown tool: {name}[/red]")
        else:
            # show what we're about to do
            self._print_tool_header(name, args)
            try:
                result = tool.execute(**args)
            except Exception as e:
                result = f"[error] Tool execution failed: {e}"

            self._print_tool_result(name, result)

        self.ctx.add({
            "role": "tool",
            "tool_call_id": call_id,
            "content": result,
        })

    def _print_tool_header(self, name: str, args: dict):
        """Show a compact header for the tool being executed."""
        if name == "bash":
            cmd = args.get("command", "")
            console.print(f"\n[bold cyan]$ {cmd}[/bold cyan]")
        elif name == "read_file":
            console.print(f"\n[bold cyan]Reading {args.get('file_path', '')}[/bold cyan]")
        elif name == "write_file":
            console.print(f"\n[bold cyan]Writing {args.get('file_path', '')}[/bold cyan]")
        elif name == "edit_file":
            console.print(f"\n[bold cyan]Editing {args.get('file_path', '')}[/bold cyan]")
        elif name == "glob":
            console.print(f"\n[bold cyan]Searching: {args.get('pattern', '')}[/bold cyan]")
        elif name == "grep":
            console.print(f"\n[bold cyan]Grep: {args.get('pattern', '')}[/bold cyan]")
        else:
            console.print(f"\n[bold cyan]{name}({args})[/bold cyan]")

    def _print_tool_result(self, name: str, result: str):
        """Print tool output, truncated for display."""
        lines = result.split("\n")
        if len(lines) > 30:
            display = "\n".join(lines[:15]) + f"\n... ({len(lines) - 30} lines hidden) ...\n" + "\n".join(lines[-15:])
        else:
            display = result
        console.print(Panel(display, border_style="dim", expand=False))
