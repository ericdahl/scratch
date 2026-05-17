# AI System Prompts Collection

A curated collection of extracted/leaked system prompts from major AI agents, coding tools, and chat products. Organized by vendor.

> **Note:** These prompts were sourced from public GitHub repositories that collect and document AI system prompts. They represent snapshots in time and may not reflect the current production versions.

## Directory Structure

```
system-prompts/
├── anthropic/          Claude models and Claude Code
│   └── claude-code-subagents/  Claude Code's internal sub-agent prompts
├── openai/             ChatGPT / GPT models
├── google/             Gemini models and Gemini CLI
├── xai/                Grok models
├── cursor/             Cursor IDE agent
├── windsurf/           Windsurf (Codeium) IDE agent
├── opencode/           OpenCode terminal agent
├── augment-code/       Augment Code agent
├── devin/              Devin AI agent
├── manus/              Manus AI agent
├── replit/             Replit AI agent
├── lovable/            Lovable (app builder)
├── v0/                 Vercel v0 (UI builder)
├── perplexity/         Perplexity AI & Kagi
└── misc/               Other tools (Warp, Zed, Amp, Meta AI, GitHub Copilot, etc.)
```

## Files

### Anthropic — Claude

| File | Description |
|------|-------------|
| `anthropic/claude-code.md` | Claude Code CLI full system prompt |
| `anthropic/claude-sonnet-4.6.md` | Claude Sonnet 4.6 (claude.ai) |
| `anthropic/claude-opus-4.7.md` | Claude Opus 4.7 |
| `anthropic/claude.ai.md` | Claude.ai web app (human-readable) |
| `anthropic/claude-mobile-ios.md` | Claude iOS app |
| `anthropic/claude-code-subagents/explore-agent.md` | Claude Code Explore sub-agent |
| `anthropic/claude-code-subagents/plan-mode.md` | Claude Code Plan mode |
| `anthropic/claude-code-subagents/general-purpose-agent.md` | Claude Code general sub-agent |
| `anthropic/claude-code-subagents/security-review.md` | Claude Code security review skill |

### OpenAI — ChatGPT

| File | Description |
|------|-------------|
| `openai/gpt-5.5-thinking.md` | GPT-5.5 with extended thinking |
| `openai/gpt-5.5-api.md` | GPT-5.5 API variant |
| `openai/gpt-5.4-thinking.md` | GPT-5.4 with extended thinking |
| `openai/o3.md` | OpenAI o3 reasoning model |
| `openai/o4-mini.md` | OpenAI o4-mini reasoning model |
| `openai/chatgpt-atlas.md` | ChatGPT Atlas (enterprise) |

### Google — Gemini

| File | Description |
|------|-------------|
| `google/gemini-cli.md` | Gemini CLI agent |
| `google/gemini-3.1-pro.md` | Gemini 3.1 Pro (web) |
| `google/gemini-3.1-pro-api.md` | Gemini 3.1 Pro (API) |
| `google/gemini-3-flash.md` | Gemini 3 Flash |
| `google/jules.md` | Google Jules (async coding agent) |

### xAI — Grok

| File | Description |
|------|-------------|
| `xai/grok-4.3-beta.md` | Grok 4.3 Beta |
| `xai/grok-4.md` | Grok 4 |
| `xai/grok-3.md` | Grok 3 |

### AI Coding Agents

| File | Description |
|------|-------------|
| `cursor/cursor.md` | Cursor IDE agent |
| `cursor/cursor-agent-2025-09-03.txt` | Cursor agent prompt (Sep 2025) |
| `cursor/cursor-chat.txt` | Cursor chat prompt |
| `windsurf/windsurf-wave11.txt` | Windsurf (Codeium) Wave 11 agent |
| `opencode/opencode.md` | OpenCode terminal agent |
| `augment-code/augment-claude-agent.txt` | Augment Code (Claude backend) |
| `augment-code/augment-gpt5-agent.txt` | Augment Code (GPT-5 backend) |
| `devin/devin.txt` | Devin AI software engineer agent |
| `manus/manus.txt` | Manus agent system prompt |
| `manus/manus-agent-loop.txt` | Manus agent loop instructions |
| `replit/replit.txt` | Replit AI agent |

### App Builders

| File | Description |
|------|-------------|
| `lovable/lovable.txt` | Lovable full-stack app builder |
| `v0/v0.txt` | Vercel v0 UI builder |

### Other Tools

| File | Description |
|------|-------------|
| `perplexity/perplexity.txt` | Perplexity AI assistant |
| `perplexity/kagi-assistant.md` | Kagi AI assistant |
| `misc/amp-code.md` | Amp (Sourcegraph) coding agent |
| `misc/github-copilot-cli.md` | GitHub Copilot CLI |
| `misc/warp-2.0-agent.md` | Warp 2.0 terminal AI agent |
| `misc/zed.md` | Zed editor AI assistant |
| `misc/meta-ai.md` | Meta AI |
| `misc/notion-ai.md` | Notion AI |
| `misc/mistral-le-chat.md` | Mistral Le Chat |
| `misc/raycast-ai.md` | Raycast AI |
| `misc/character-ai.md` | Character.AI |

## Sources

Prompts were sourced from these public repositories:

- [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) — ChatGPT, Claude, Gemini, Grok, Perplexity, and more
- [x1xhlol/system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) — Cursor, Windsurf, Devin, Replit, Lovable, v0, Manus, Augment Code
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — Claude Code sub-agent prompts, extracted from Claude Code source

## Notes on Pi (Inflection AI)

Pi's system prompt has not been publicly leaked/extracted. Inflection AI has not published it, and it does not appear in any of the major collections above.

## Disclaimer

These prompts are collected from public sources for research and educational purposes. All trademarks belong to their respective owners.
