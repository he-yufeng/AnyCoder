"""Configuration management."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# load .env from cwd first, then from ~/.anycoder/
load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(Path.home() / ".anycoder" / ".env", override=False)


# shortcuts so users don't have to type litellm provider prefixes
MODEL_ALIASES = {
    # DeepSeek
    "deepseek": "deepseek/deepseek-chat",
    "deepseek-r1": "deepseek/deepseek-reasoner",
    # Alibaba Qwen
    "qwen": "openai/qwen-plus",
    "qwen-max": "openai/qwen-max",
    "qwen3": "openai/qwen3-235b-a22b",
    # OpenAI
    "gpt5": "gpt-5.4",
    "gpt-5": "gpt-5.4",
    "gpt-5.4": "gpt-5.4",
    "gpt4o": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "o4-mini": "o4-mini",
    # Anthropic
    "claude": "claude-sonnet-4-6-20250514",
    "claude-opus": "claude-opus-4-6-20250514",
    "claude-haiku": "claude-haiku-4-5-20251001",
    # Google
    "gemini": "gemini/gemini-2.5-flash",
    "gemini-pro": "gemini/gemini-2.5-pro",
    # Moonshot Kimi
    "kimi": "openai/kimi-k2.5",
    # Zhipu
    "glm": "openai/glm-4-plus",
}

# rough context window sizes for compression heuristics
_CTX_SIZES = {
    "deepseek/deepseek-chat": 128_000,
    "deepseek/deepseek-reasoner": 128_000,
    "gpt-5.4": 128_000,
    "gpt-4o": 128_000,
    "o4-mini": 200_000,
    "claude-sonnet-4-6-20250514": 200_000,
    "claude-opus-4-6-20250514": 200_000,
    "gemini/gemini-2.5-flash": 1_000_000,
    "gemini/gemini-2.5-pro": 1_000_000,
}


@dataclass
class Config:
    model: str = "deepseek/deepseek-chat"
    api_base: str | None = None
    api_key: str | None = None
    max_tokens: int = 128_000
    compress_threshold: float = 0.7
    max_iterations: int = 50

    @classmethod
    def from_env(cls) -> "Config":
        """Build config from environment variables."""
        model = os.environ.get("ANYCODER_MODEL", "deepseek/deepseek-chat")
        model = MODEL_ALIASES.get(model, model)

        api_base = os.environ.get("ANYCODER_API_BASE") or os.environ.get("OPENAI_API_BASE")
        api_key = os.environ.get("ANYCODER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        max_tokens = _CTX_SIZES.get(model, 128_000)

        return cls(model=model, api_base=api_base, api_key=api_key, max_tokens=max_tokens)

    def resolve_model(self, model_arg: str | None) -> str:
        """Resolve a model name from CLI arg, handling aliases."""
        if model_arg:
            resolved = MODEL_ALIASES.get(model_arg, model_arg)
            self.model = resolved
            self.max_tokens = _CTX_SIZES.get(resolved, 128_000)
        return self.model
