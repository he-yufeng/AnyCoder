# AnyCoder

**终端里的 AI 编程 Agent，支持任意大模型。**

DeepSeek、Qwen、GPT-4o、Claude、Gemini、Kimi、GLM、Ollama 本地模型——选你喜欢的，直接开写。

[English](README.md) | [安装](#安装) | [快速开始](#快速开始) | [支持的模型](#支持的模型)

## 为什么做 AnyCoder？

Claude Code 是目前最强的 AI 编程工具，但它只能用 Anthropic 的 API。国内开发者想用？得解决 API 访问的问题。

AnyCoder 提供同样的 Agent 体验：文件编辑、命令执行、代码搜索，但**你可以用任何大模型**。DeepSeek 便宜？用 DeepSeek。公司提供 Qwen 接口？直接接。想全部本地跑？Ollama 搞定。

**核心特性：**

- **100+ 模型** - 通过 [litellm](https://github.com/BerriAI/litellm) 支持几乎所有 LLM 供应商
- **工具调用 Agent 循环** - 读文件、写代码、跑命令、搜索代码库，全自动
- **流式输出** - 打字机效果，实时看到模型的回复
- **上下文管理** - 对话太长了自动压缩，不会丢失关键信息
- **搜索替换编辑** - 精确修改文件，不是整个覆盖
- **零配置** - 设个 API Key 就能用。`pip install anycoder && anycoder`

## 安装

```bash
pip install anycoder
```

## 快速开始

```bash
# 设置 API Key（选一个）
export DEEPSEEK_API_KEY=sk-...    # DeepSeek（默认）
export OPENAI_API_KEY=sk-...      # OpenAI
export ANTHROPIC_API_KEY=sk-...   # Claude
export GEMINI_API_KEY=...         # Gemini

# 启动交互式 REPL
anycoder

# 指定模型
anycoder -m claude
anycoder -m gpt4o
anycoder -m deepseek
anycoder -m qwen

# 单次模式（不进入交互）
anycoder "给 auth.py 的登录函数加上错误处理"
```

## 支持的模型

用简写别名或完整的 [litellm 模型名](https://docs.litellm.ai/docs/providers)：

| 别名 | 模型 | 厂商 |
|------|------|------|
| `deepseek` | DeepSeek Chat | 深度求索 |
| `deepseek-r1` | DeepSeek Reasoner | 深度求索 |
| `qwen` | Qwen Plus | 阿里通义 |
| `qwen-max` | Qwen Max | 阿里通义 |
| `gpt4o` | GPT-4o | OpenAI |
| `gpt-4o-mini` | GPT-4o Mini | OpenAI |
| `claude` | Claude Sonnet 4 | Anthropic |
| `claude-opus` | Claude Opus 4 | Anthropic |
| `gemini` | Gemini 2.0 Flash | Google |
| `gemini-pro` | Gemini 2.5 Pro | Google |
| `kimi` | Moonshot v1 | 月之暗面 |
| `glm` | GLM-4 Plus | 智谱 AI |
| `o1` | o1 | OpenAI |
| `o3-mini` | o3-mini | OpenAI |

### 本地模型（Ollama）

```bash
# 确保 Ollama 在运行
ollama serve

# 用任意 Ollama 模型
anycoder -m ollama/llama3.1
anycoder -m ollama/codestral
anycoder -m ollama/deepseek-coder-v2
```

### 自定义 OpenAI 兼容 API

很多国内厂商提供 OpenAI 兼容的接口，直接设 base URL 就行：

```bash
export ANYCODER_API_BASE=https://your-api.com/v1
export ANYCODER_API_KEY=your-key
anycoder -m your-model-name
```

## 内置工具

AnyCoder 有 6 个内置工具供大模型调用：

| 工具 | 功能 |
|------|------|
| `bash` | 执行 Shell 命令（跑测试、git 操作、安装依赖等） |
| `read_file` | 读文件，带行号，支持大文件的分段读取 |
| `write_file` | 创建新文件或覆盖已有文件 |
| `edit_file` | 搜索替换式编辑，检查唯一性避免误改 |
| `glob` | 按模式搜索文件（`**/*.py`、`src/**/*.ts`） |
| `grep` | 正则搜索文件内容 |

你只需要用自然语言描述你想做什么，Agent 会自动选择合适的工具。

## 交互命令

在 REPL 里可以用这些命令：

| 命令 | 说明 |
|------|------|
| `/help` | 查看帮助 |
| `/model <名称>` | 切换模型 |
| `/models` | 列出所有模型别名 |
| `/clear` | 清空对话记录 |
| `/cost` | 查看 token 用量和费用 |
| `/quit` | 退出 |

## 架构

```
用户输入
    ↓
┌─────────┐     ┌──────────┐     ┌───────────┐
│   CLI   │ ──→ │  Agent   │ ──→ │    LLM    │
│  (REPL) │     │  (循环)  │     │ (litellm) │
└─────────┘     └──────────┘     └───────────┘
                     ↓  ↑
                ┌──────────┐
                │  工具层  │
                │ bash     │
                │ read     │
                │ write    │
                │ edit     │
                │ glob     │
                │ grep     │
                └──────────┘
```

Agent 循环：
1. 把对话历史 + 工具 Schema 发给 LLM
2. LLM 返回文字 → 直接展示
3. LLM 返回工具调用 → 执行工具，把结果追加到上下文，回到第 1 步
4. 上下文管理器在快要超限时自动压缩旧消息

## 配置

所有配置通过环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ANYCODER_MODEL` | 默认模型 | `deepseek/deepseek-chat` |
| `ANYCODER_API_BASE` | 自定义 API 地址 | - |
| `ANYCODER_API_KEY` | API 密钥 | - |
| `DEEPSEEK_API_KEY` | DeepSeek 密钥 | - |
| `OPENAI_API_KEY` | OpenAI 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic 密钥 | - |
| `GEMINI_API_KEY` | Google AI 密钥 | - |

## 和 Claude Code 的对比

| 特性 | Claude Code | AnyCoder |
|------|------------|----------|
| 模型支持 | 仅 Claude | 100+ 模型 |
| 语言 | TypeScript | Python |
| 安装 | `npm` | `pip` |
| 文件编辑 | 搜索替换 | 搜索替换 |
| Shell 命令 | 支持 | 支持 |
| 代码搜索 | 支持 | 支持 (glob + grep) |
| 流式输出 | 支持 | 支持 |
| 上下文压缩 | 支持 | 支持 |
| 费用 | Claude 定价 | 你选的模型定价 |
| 开源 | 部分 | 完全开源 (MIT) |

## 开发

```bash
git clone https://github.com/he-yufeng/AnyCoder.git
cd AnyCoder
pip install -e ".[dev]"
```

## 致谢

架构受 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 启发。使用 [litellm](https://github.com/BerriAI/litellm) 实现多模型支持，[Rich](https://github.com/Textualize/rich) 做终端渲染。

我的相关项目：[CoreCoder](https://github.com/he-yufeng/CoreCoder) - Claude Code 51 万行源码的 1300 行 Python 核心重写，附架构深度解读。

## License

MIT
