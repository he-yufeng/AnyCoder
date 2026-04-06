# AnyCoder

**终端里的 AI 编程 Agent，支持任意大模型。**

[![PyPI](https://img.shields.io/pypi/v/anycoder)](https://pypi.org/project/anycoder/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/he-yufeng/AnyCoder/actions/workflows/ci.yml/badge.svg)](https://github.com/he-yufeng/AnyCoder/actions)

[English](README.md) | [中文](README_CN.md) | [安装](#安装) | [快速开始](#快速开始)

DeepSeek、Qwen、GPT-5、Claude、Gemini、Kimi、GLM、Ollama 本地模型，选你喜欢的就能开写。

---

```
$ anycoder -m deepseek

> 读一下 main.py，修掉拼错的 import

  Reading main.py
  ╭──────────────────────────────────────╮
  │ [6 lines total]                      │
  │      1  from utils import halper     │
  │      ...                             │
  ╰──────────────────────────────────────╯

  Editing main.py
  ╭──────────────────────────────────────╮
  │ Replaced 1 occurrence(s) in main.py  │
  ╰──────────────────────────────────────╯

修好了：halper → helper。

  deepseek-chat | tokens: 1,247 | cost: $0.0004
```

## 为什么做 AnyCoder？

Claude Code 是目前最强的 AI 编程工具，但它只能用 Anthropic 的模型。想用 DeepSeek（便宜好用）？想用 Qwen（阿里的）？想在本地跑 Ollama？不行。

AnyCoder 提供同样的体验：文件编辑、命令执行、代码搜索、上下文管理，但你**可以用任何大模型**。

**它能做什么：**

- **100+ 模型** - 通过 [litellm](https://github.com/BerriAI/litellm) 支持几乎所有 LLM 供应商
- **Agent 工具调用循环** - 自动读文件、写代码、跑命令、搜索代码库
- **流式输出** - 一个字一个字实时打出来
- **上下文压缩** - 对话太长自动压缩（先截工具输出，再摘要旧消息）
- **搜索替换编辑** - 精确修改文件，唯一性校验，不会误改
- **会话持久化** - `/save` 保存，`--resume` 恢复
- **`.env` 支持** - 项目根目录放个 `.env` 就行
- **~1,300 行 Python** - 可以看完，可以改，可以拿去造自己的

## 安装

```bash
pip install anycoder
```

## 快速开始

```bash
# 设置 API Key（选一个）
export DEEPSEEK_API_KEY=sk-...    # DeepSeek（默认模型）
export OPENAI_API_KEY=sk-...      # OpenAI
export ANTHROPIC_API_KEY=sk-...   # Claude
export GEMINI_API_KEY=...         # Gemini

# 启动
anycoder

# 指定模型
anycoder -m claude
anycoder -m gpt5
anycoder -m deepseek
anycoder -m qwen

# 单次模式
anycoder "给 auth.py 的登录函数加上错误处理"
anycoder -p "找出所有 TODO 注释"

# 恢复已保存的会话
anycoder --resume session_1712345678
```

也可以在项目根目录放 `.env` 文件：

```bash
# .env
DEEPSEEK_API_KEY=sk-...
ANYCODER_MODEL=deepseek
```

## 支持的模型

用简写别名或完整的 [litellm 模型名](https://docs.litellm.ai/docs/providers)：

| 别名 | 模型 | 厂商 |
|------|------|------|
| `deepseek` | DeepSeek Chat (V3) | 深度求索 |
| `deepseek-r1` | DeepSeek Reasoner (R1) | 深度求索 |
| `gpt5` / `gpt-5` | GPT-5.4 | OpenAI |
| `gpt4o` | GPT-4o | OpenAI |
| `o4-mini` | o4-mini | OpenAI |
| `claude` | Claude Sonnet 4.6 | Anthropic |
| `claude-opus` | Claude Opus 4.6 | Anthropic |
| `claude-haiku` | Claude Haiku 4.5 | Anthropic |
| `gemini` | Gemini 2.5 Flash | Google |
| `gemini-pro` | Gemini 2.5 Pro | Google |
| `qwen` | Qwen Plus | 阿里通义 |
| `qwen-max` | Qwen Max | 阿里通义 |
| `kimi` | Kimi K2.5 | 月之暗面 |
| `glm` | GLM-4 Plus | 智谱 AI |

### 本地模型（Ollama）

```bash
ollama serve
anycoder -m ollama/llama3.1
anycoder -m ollama/codestral
anycoder -m ollama/qwen3:32b
```

### 自定义 OpenAI 兼容 API

国内很多厂商都提供 OpenAI 兼容接口，设个 base URL 就行：

```bash
export ANYCODER_API_BASE=https://your-api.com/v1
export ANYCODER_API_KEY=your-key
anycoder -m your-model-name
```

## 内置工具

AnyCoder 有 6 个内置工具，大模型会自动调用：

| 工具 | 功能 |
|------|------|
| `bash` | 执行 Shell 命令（跑测试、git、安装依赖等） |
| `read_file` | 读文件，带行号，支持大文件分段读取 |
| `write_file` | 创建新文件或覆盖已有文件 |
| `edit_file` | 搜索替换编辑，唯一性校验避免误改 |
| `glob` | 按模式搜索文件（`**/*.py`、`src/**/*.ts`） |
| `grep` | 正则搜索文件内容 |

你用自然语言说需求就行，Agent 会自动选工具。

## 交互命令

| 命令 | 说明 |
|------|------|
| `/model` | 查看当前模型 |
| `/model <名称>` | 切换模型 |
| `/models` | 列出所有模型别名 |
| `/tokens` | Token 用量和费用估算 |
| `/diff` | 查看本次会话修改的文件 |
| `/compact` | 手动压缩上下文 |
| `/save [名称]` | 保存会话 |
| `/sessions` | 列出已保存的会话 |
| `/clear` | 清空对话记录 |
| `/help` | 查看帮助 |
| `/quit` | 退出 |

**输入方式：** Enter 发送，Esc+Enter 换行（多行输入），Ctrl+C 取消，Ctrl+D 退出。

## 架构

一共 ~1,300 行，全看完也就一两个小时的事：

```
anycoder/
├── cli.py            REPL + 命令                   258 行
├── llm.py            litellm 流式封装              185 行
├── agent.py          Agent 循环 + 工具执行         151 行
├── context.py        两阶段上下文压缩               92 行
├── config.py         环境变量 + .env + 别名         86 行
├── session.py        会话保存/恢复                   60 行
├── prompts/system.py 系统提示词                      50 行
└── tools/
    ├── bash.py       Shell 执行                     56 行
    ├── edit_file.py  搜索替换 + 变更追踪            81 行
    ├── grep_tool.py  正则内容搜索                   84 行
    ├── read_file.py  文件读取                       58 行
    ├── glob_tool.py  文件模式搜索                   48 行
    └── write_file.py 文件写入 + 变更追踪            39 行
```

**Agent 循环的工作流程：**

1. 用户消息加入对话历史
2. 历史 + 工具 Schema 发给 LLM（流式）
3. LLM 返回文字 → 直接打到终端
4. LLM 返回工具调用 → 执行工具，结果追加到历史
5. 回到第 2 步，直到 LLM 只返回文字（不再调工具）
6. 快超限时，上下文管理器自动压缩

**两阶段压缩**（参考 Claude Code 的做法）：
- 第一阶段：截断过长的工具输出（保留对话结构）
- 第二阶段：如果还超，摘要替换旧的对话轮次

## 配置

环境变量或 `.env` 文件：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ANYCODER_MODEL` | 默认模型 | `deepseek/deepseek-chat` |
| `ANYCODER_API_BASE` | 自定义 API 地址 | - |
| `ANYCODER_API_KEY` | API 密钥 | - |
| `DEEPSEEK_API_KEY` | DeepSeek 密钥 | - |
| `OPENAI_API_KEY` | OpenAI 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic 密钥 | - |
| `GEMINI_API_KEY` | Google AI 密钥 | - |

## 当库用

```python
from anycoder import Agent, Config

config = Config(model="deepseek/deepseek-chat", api_key="sk-...")
agent = Agent(config)
agent.run("找出项目里所有 TODO 注释并列出来")
```

## 对比

| 特性 | Claude Code | Cline | Aider | **AnyCoder** |
|------|-------------|-------|-------|-------------|
| 模型支持 | 仅 Claude | 多模型 | 多模型 | **100+ 通过 litellm** |
| 语言 | TypeScript（闭源） | TypeScript | Python | **Python (MIT)** |
| 安装 | `npm` | VS Code 插件 | `pip` | **`pip`** |
| 文件编辑 | 搜索替换 | Diff | Diff | **搜索替换** |
| 上下文压缩 | 支持 | 不支持 | 支持 | **支持（两阶段）** |
| 流式输出 | 支持 | 支持 | 支持 | **支持** |
| 会话持久化 | 支持 | 不支持 | 支持 | **支持** |
| 代码量 | 51 万行 | 10 万+ | 5 万+ | **~1,300 行** |
| 适合 | 直接用 | 直接用 | 直接用 | **用 + 读源码** |

## 开发

```bash
git clone https://github.com/he-yufeng/AnyCoder.git
cd AnyCoder
pip install -e ".[dev]"
pytest tests/ -v
```

## 相关项目

- [CoreCoder](https://github.com/he-yufeng/CoreCoder) - 我的另一个项目：Claude Code 51 万行源码浓缩成 ~1,400 行 Python，附 7 篇架构深度解读。AnyCoder 基于同样的思路，但更注重实用（litellm 多模型、会话持久化、.env 支持），而非教学。

## License

MIT。拿去用，拿去改，造更好的东西。

---

作者 **[何宇峰](https://github.com/he-yufeng)** · Agentic AI Researcher @ Moonshot AI (Kimi)
