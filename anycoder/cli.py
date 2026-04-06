"""CLI interface - the REPL that users interact with."""

import argparse
import os
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from anycoder import __version__
from anycoder.config import Config, MODEL_ALIASES
from anycoder.agent import Agent


console = Console()

BANNER = f"""[bold green]
  ╔═══════════════════════════════════════╗
  ║   AnyCoder v{__version__:<26s}║
  ║   AI Coding Agent · Any LLM          ║
  ╚═══════════════════════════════════════╝
[/bold green]"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AnyCoder - AI coding agent for any LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  anycoder                          # Start with default model (DeepSeek)
  anycoder -m claude                # Use Claude
  anycoder -m gpt4o                 # Use GPT-4o
  anycoder -m deepseek              # Use DeepSeek
  anycoder -m qwen                  # Use Qwen
  anycoder -m gemini                # Use Gemini
  anycoder -m ollama/llama3.1       # Use local Ollama model
  anycoder "fix the bug in main.py" # One-shot mode
        """,
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="Model to use (e.g., deepseek, claude, gpt4o, qwen, or full litellm model name)",
    )
    parser.add_argument(
        "--api-base",
        type=str,
        default=None,
        help="Custom API base URL (for OpenAI-compatible providers)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key (can also set via env vars)",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="One-shot prompt (skip interactive mode)",
    )
    return parser.parse_args()


def print_status_bar(config: Config, agent: Agent):
    """Show model and token usage in a dim status line."""
    model_display = config.model.split("/")[-1] if "/" in config.model else config.model
    usage = agent.llm.usage_summary
    console.print(f"[dim]{model_display} · {usage}[/dim]")


def main():
    args = parse_args()

    config = Config.from_env()

    # CLI args override env
    if args.model:
        config.resolve_model(args.model)
    if args.api_base:
        config.api_base = args.api_base
    if args.api_key:
        config.api_key = args.api_key

    agent = Agent(config)

    # one-shot mode
    if args.prompt:
        prompt_text = " ".join(args.prompt)
        agent.run(prompt_text)
        return

    # interactive REPL
    console.print(BANNER)

    model_name = config.model.split("/")[-1] if "/" in config.model else config.model
    console.print(f"  Model: [bold]{model_name}[/bold]")
    console.print(f"  cwd:   [bold]{os.getcwd()}[/bold]")
    console.print(f"\n  Type [bold]/help[/bold] for commands, [bold]Ctrl+C[/bold] to cancel, [bold]Ctrl+D[/bold] to exit.\n")

    # persistent history
    history_dir = os.path.expanduser("~/.anycoder")
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, "history")

    session = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
        multiline=False,
    )

    while True:
        try:
            user_input = session.prompt(
                "\n❯ ",
            ).strip()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted[/dim]")
            continue
        except EOFError:
            console.print("\n[dim]Bye![/dim]")
            break

        if not user_input:
            continue

        # built-in commands
        if user_input.startswith("/"):
            if handle_command(user_input, config, agent):
                continue

        # run the agent
        try:
            agent.run(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")

        print_status_bar(config, agent)


def handle_command(cmd: str, config: Config, agent: Agent) -> bool:
    """Handle slash commands. Returns True if handled."""
    parts = cmd.split(None, 1)
    command = parts[0].lower()

    if command in ("/help", "/h"):
        console.print("""
[bold]Commands:[/bold]
  /help           Show this help
  /model <name>   Switch model (e.g., /model claude, /model deepseek)
  /models         List model aliases
  /clear          Clear conversation history
  /cost           Show token usage and cost
  /quit           Exit
        """)
        return True

    elif command == "/model":
        if len(parts) < 2:
            current = config.model.split("/")[-1] if "/" in config.model else config.model
            console.print(f"Current model: [bold]{current}[/bold]")
            return True
        new_model = parts[1].strip()
        config.resolve_model(new_model)
        agent.llm.model = config.model
        display = config.model.split("/")[-1] if "/" in config.model else config.model
        console.print(f"Switched to [bold]{display}[/bold]")
        return True

    elif command == "/models":
        console.print("[bold]Model aliases:[/bold]")
        for alias, full in sorted(MODEL_ALIASES.items()):
            console.print(f"  {alias:<16s} → {full}")
        console.print("\n[dim]You can also use any litellm model name directly.[/dim]")
        return True

    elif command == "/clear":
        agent.ctx.reset()
        console.print("[dim]Conversation cleared[/dim]")
        return True

    elif command == "/cost":
        llm = agent.llm
        console.print(f"""
[bold]Usage:[/bold]
  Input tokens:  {llm.total_input_tokens:,}
  Output tokens: {llm.total_output_tokens:,}
  Total tokens:  {llm.total_input_tokens + llm.total_output_tokens:,}
  Est. cost:     ${llm.total_cost:.4f}
        """)
        return True

    elif command in ("/quit", "/exit", "/q"):
        raise EOFError()

    return False


if __name__ == "__main__":
    main()
