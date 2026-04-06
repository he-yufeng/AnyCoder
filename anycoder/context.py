"""Context window management - keeps conversations within token limits."""

from anycoder.llm import LLMClient


class ContextManager:
    """Tracks message history and compresses when approaching the token limit."""

    def __init__(self, llm: LLMClient, max_tokens: int, compress_threshold: float = 0.7):
        self.llm = llm
        self.max_tokens = max_tokens
        self.compress_threshold = compress_threshold
        self.messages: list[dict] = []

    def add(self, message: dict):
        self.messages.append(message)

    def get_messages(self) -> list[dict]:
        return list(self.messages)

    @property
    def token_count(self) -> int:
        return self.llm.count_tokens(self.messages)

    def needs_compression(self) -> bool:
        return self.token_count > int(self.max_tokens * self.compress_threshold)

    def compress(self):
        """
        Compress older messages by summarizing them.
        Keeps the system prompt and recent messages intact.
        """
        if len(self.messages) < 4:
            return

        # always keep: system prompt (index 0) and last few turns
        keep_recent = 6  # last 3 pairs of user/assistant
        system = self.messages[0] if self.messages[0]["role"] == "system" else None
        recent = self.messages[-keep_recent:]
        middle = self.messages[1:-keep_recent] if system else self.messages[:-keep_recent]

        if not middle:
            return

        # build a summary of the middle section
        summary_parts = []
        for msg in middle:
            role = msg["role"]
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                # truncate long content
                preview = content[:200] + "..." if len(content) > 200 else content
                summary_parts.append(f"[{role}]: {preview}")
            elif role == "tool":
                tool_name = msg.get("name", "unknown")
                summary_parts.append(f"[tool result from {tool_name}]")

        summary_text = (
            "[Earlier conversation compressed]\n"
            + "\n".join(summary_parts[-10:])  # keep last 10 items of summary
        )

        compressed = [{"role": "assistant", "content": summary_text}]
        self.messages = ([system] if system else []) + compressed + recent

    def reset(self):
        """Clear everything except the system prompt."""
        system = self.messages[0] if self.messages and self.messages[0]["role"] == "system" else None
        self.messages = [system] if system else []
