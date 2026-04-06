"""Configuration management."""

import os
from dataclasses import dataclass, field


# popular model shortcuts so users don't have to remember full provider paths
MODEL_ALIASES = {
    "deepseek": "deepseek/deepseek-chat",
    "deepseek-r1": "deepseek/deepseek-reasoner",
    "qwen": "openai/qwen-plus",
    "qwen-max": "openai/qwen-max",
    "gpt4o": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "claude": "claude-sonnet-4-20250514",
    "claude-opus": "claude-opus-4-20250514",
    "gemini": "gemini/gemini-2.0-flash",
    "gemini-pro": "gemini/gemini-2.5-pro-preview-05-06",
    "kimi": "openai/moonshot-v1-auto",
    "glm": "openai/glm-4-plus",
    "o1": "o1",
    "o3-mini": "o3-mini",
}


@dataclass
class Config:
    model: str = "deepseek/deepseek-chat"
    api_base: str | None = None
    api_key: str | None = None
    max_tokens: int = 128000  # context window size
    compress_threshold: float = 0.7  # compress when context hits 70%
    max_iterations: int = 50  # safety limit per user turn

    @classmethod
    def from_env(cls) -> "Config":
        """Build config from environment variables and sensible defaults."""
        model = os.environ.get("ANYCODER_MODEL", "deepseek/deepseek-chat")
        # resolve aliases
        model = MODEL_ALIASES.get(model, model)

        # for Chinese providers that use OpenAI-compatible APIs,
        # user can set base URL + key
        api_base = os.environ.get("ANYCODER_API_BASE") or os.environ.get("OPENAI_API_BASE")
        api_key = os.environ.get("ANYCODER_API_KEY") or os.environ.get("OPENAI_API_KEY")

        return cls(
            model=model,
            api_base=api_base,
            api_key=api_key,
        )

    def resolve_model(self, model_arg: str | None) -> str:
        """Resolve a model name from CLI arg, handling aliases."""
        if model_arg:
            resolved = MODEL_ALIASES.get(model_arg, model_arg)
            self.model = resolved
        return self.model
