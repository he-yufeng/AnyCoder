# AnyCoder

**AI coding agent in your terminal. Works with any LLM.**

DeepSeek, Qwen, GPT-4o, Claude, Gemini, Kimi, GLM, Ollama local models - pick your favorite and start coding.

[中文文档](README_CN.md) | [Installation](#installation) | [Quick Start](#quick-start) | [Supported Models](#supported-models)

## Why AnyCoder?

Claude Code is powerful but locked to Anthropic's API. Most AI coding tools force you into one provider.

AnyCoder gives you the same agent experience - file editing, shell commands, codebase search - with **whatever LLM you want**. Got cheap DeepSeek credits? Use those. Company provides Qwen access? Works too. Want everything local with Ollama? Go ahead.

**Key features:**

- **100+ LLM providers** via [litellm](https://github.com/BerriAI/litellm) - one interface, any model
- **Tool-use agent loop** - reads files, writes code, runs commands, searches codebases
- **Streaming output** - see responses as they generate
- **Context management** - automatic compression when conversations get long
- **Search & replace editing** - precise file modifications, not blind overwrites
- **Zero config** - set an API key and go. `pip install anycoder && anycoder`

## Installation

```bash
pip install anycoder
```

## Quick Start

```bash
# Set your API key (pick one)
export DEEPSEEK_API_KEY=sk-...    # DeepSeek (default)
export OPENAI_API_KEY=sk-...      # OpenAI
export ANTHROPIC_API_KEY=sk-...   # Claude
export GEMINI_API_KEY=...         # Gemini

# Start the REPL
anycoder

# Or specify a model
anycoder -m claude
anycoder -m gpt4o
anycoder -m deepseek

# One-shot mode
anycoder "add error handling to the login function in auth.py"
```

## Supported Models

Use short aliases or full [litellm model names](https://docs.litellm.ai/docs/providers):

| Alias | Model | Provider |
|-------|-------|----------|
| `deepseek` | DeepSeek Chat | DeepSeek |
| `deepseek-r1` | DeepSeek Reasoner | DeepSeek |
| `qwen` | Qwen Plus | Alibaba |
| `qwen-max` | Qwen Max | Alibaba |
| `gpt4o` | GPT-4o | OpenAI |
| `gpt-4o-mini` | GPT-4o Mini | OpenAI |
| `claude` | Claude Sonnet 4 | Anthropic |
| `claude-opus` | Claude Opus 4 | Anthropic |
| `gemini` | Gemini 2.0 Flash | Google |
| `gemini-pro` | Gemini 2.5 Pro | Google |
| `kimi` | Moonshot v1 | Moonshot AI |
| `glm` | GLM-4 Plus | Zhipu AI |
| `o1` | o1 | OpenAI |
| `o3-mini` | o3-mini | OpenAI |

### Local Models (Ollama)

```bash
# Make sure Ollama is running
ollama serve

# Use any Ollama model
anycoder -m ollama/llama3.1
anycoder -m ollama/codestral
anycoder -m ollama/deepseek-coder-v2
```

### Custom OpenAI-Compatible APIs

```bash
# Any provider with an OpenAI-compatible endpoint
export ANYCODER_API_BASE=https://your-api.com/v1
export ANYCODER_API_KEY=your-key
anycoder -m your-model-name
```

## Tools

AnyCoder has 6 built-in tools that the LLM can use:

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands (tests, git, installs, builds) |
| `read_file` | Read files with line numbers, supports offset/limit for large files |
| `write_file` | Create new files or overwrite existing ones |
| `edit_file` | Search-and-replace edits with uniqueness checking |
| `glob` | Find files by pattern (`**/*.py`, `src/**/*.ts`) |
| `grep` | Search file contents with regex |

The agent decides which tools to use based on your request. You just describe what you want in natural language.

## Commands

Inside the REPL:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/model <name>` | Switch model mid-conversation |
| `/models` | List all model aliases |
| `/clear` | Clear conversation history |
| `/cost` | Show token usage and estimated cost |
| `/quit` | Exit |

## Architecture

```
User Input
    ↓
┌─────────┐     ┌──────────┐     ┌───────────┐
│   CLI   │ ──→ │  Agent   │ ──→ │    LLM    │
│  (REPL) │     │  (Loop)  │     │ (litellm) │
└─────────┘     └──────────┘     └───────────┘
                     ↓  ↑
                ┌──────────┐
                │  Tools   │
                │ bash     │
                │ read     │
                │ write    │
                │ edit     │
                │ glob     │
                │ grep     │
                └──────────┘
```

The agent loop:
1. Send conversation history + tool schemas to LLM
2. If LLM returns text → display to user
3. If LLM returns tool calls → execute tools, append results, go to step 1
4. Context manager compresses old messages when approaching token limit

## Configuration

All configuration via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANYCODER_MODEL` | Default model | `deepseek/deepseek-chat` |
| `ANYCODER_API_BASE` | Custom API base URL | - |
| `ANYCODER_API_KEY` | API key | - |
| `DEEPSEEK_API_KEY` | DeepSeek API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `GEMINI_API_KEY` | Google AI API key | - |

## Comparison with Claude Code

| Feature | Claude Code | AnyCoder |
|---------|------------|----------|
| LLM Support | Claude only | 100+ models |
| Language | TypeScript | Python |
| Install | `npm` | `pip` |
| File editing | Search & replace | Search & replace |
| Shell commands | Yes | Yes |
| Codebase search | Yes | Yes (glob + grep) |
| Streaming | Yes | Yes |
| Context compression | Yes | Yes |
| Cost | Claude API pricing | Your choice |
| Open source | Partially | Fully (MIT) |

## Development

```bash
git clone https://github.com/he-yufeng/AnyCoder.git
cd AnyCoder
pip install -e ".[dev]"
```

## Acknowledgements

Inspired by [Claude Code](https://docs.anthropic.com/en/docs/claude-code)'s architecture. Built with [litellm](https://github.com/BerriAI/litellm) for universal LLM support and [Rich](https://github.com/Textualize/rich) for terminal rendering.

Also check out my other project [CoreCoder](https://github.com/he-yufeng/CoreCoder) - a 1,300-line Python distillation of Claude Code's 510K-line source, with architecture deep dives.

## License

MIT
