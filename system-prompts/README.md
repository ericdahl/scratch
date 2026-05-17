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
├── pi/                 Pi coding agent (badlogic/pi-mono)
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
| `pi/pi-coding-agent.md` | Pi coding agent (badlogic) — dynamically constructed prompt |
| `pi/system-prompt.ts` | Pi `buildSystemPrompt()` TypeScript source |
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

---

## Comparison

A deep dive into the six major terminal coding agents: **Claude Code**, **GitHub Copilot CLI**, **Gemini CLI**, **Codex CLI**, **OpenCode**, and **Pi**. All data sourced directly from the prompt files in this repo.

### Prompt size

| Agent | Raw size | Notes |
|-------|----------|-------|
| GitHub Copilot CLI | ~73 KB | Largest — includes full YAML for 7 sub-agent definitions inline |
| Claude Code | ~59 KB | Includes all tool schemas and detailed memory system |
| Codex CLI (GPT-5.5) | ~32 KB | Includes memory layout and rich frontend design rules |
| Gemini CLI | ~29 KB | Leaner core; sub-agent details not embedded |
| OpenCode | ~16 KB | Mid-size; no memory or sub-agents, but includes worked workflow examples |
| Pi | ~2 KB | The smallest by far — deliberately minimal, built dynamically at runtime |

Pi is the outlier: its "prompt" is actually a TypeScript function (`buildSystemPrompt()`) that assembles the final string from whichever tools are active. With only the core four tools enabled, it emits roughly 400 words.

Claude Code's prompt contains the full JSON schemas for every tool it exposes — Bash, Edit, Read, Grep, Glob, Agent, Skill, etc. — making it a self-contained spec rather than just a persona document.

GitHub Copilot CLI embeds complete YAML files for each of its 7 sub-agents *inside* the main system prompt, which is why it's the biggest. Claude Code publishes its sub-agent prompts as separate files (see `anthropic/claude-code-subagents/`).

---

### Sub-agents

| Agent | Sub-agents |
|-------|-----------|
| GitHub Copilot CLI | 7: `code-review`, `explore`, `rem-agent`, `research`, `rubber-duck`, `task`, `subconscious`, `github-context` |
| Gemini CLI | 4: `codebase_investigator`, `cli_help`, `generalist`, `browser_agent` |
| Claude Code | 4: `Explore`, `general-purpose`, `Plan`, `statusline-setup` |
| Codex CLI | 0 visible (no sub-agent system in the prompt) |
| OpenCode | 0 |
| Pi | 0 (intentionally — extensibility is via the SDK, not prompt-embedded agents) |

Copilot CLI's sub-agent lineup is the most opinionated. The **rubber-duck** agent is a devil's advocate critic you're supposed to call *before* implementing — it reads your plan and tells you what could go wrong. The **rem-agent** ("REM" as in sleep) consolidates session history into long-term memory in the background, explicitly inspired by how the brain consolidates memories during REM sleep. The **subconscious** sidekick silently reads a "context board" on every user turn and forwards anything relevant to the main agent's inbox before it starts responding — like a background pre-fetch.

Gemini CLI's **browser_agent** is the only one in this group with a dedicated full browser automation sub-agent (not just `curl`-style fetching) — useful for JS-heavy pages, form filling, multi-step flows.

---

### Memory systems

| Agent | Approach | Scope |
|-------|----------|-------|
| Codex CLI | File-based (`MEMORY.md` index + `rollout_summaries/` JSONL + `skills/`) with `<oai-mem-citation>` blocks in responses | Per-user, persistent across sessions |
| Claude Code | File-based (4 typed categories: `user`, `feedback`, `project`, `reference`; indexed via `MEMORY.md`) | Per-project directory |
| GitHub Copilot CLI | SQLite database (`session_store`) with FTS5 full-text search + dynamic `context_board` | Per-repo, cross-session queryable |
| Gemini CLI | `save_memory` tool with `global` and `project` scope; stored in `GEMINI.md` | Two scopes: global preferences vs per-project |
| OpenCode | None | — |
| Pi | None | — |

Claude Code has the most prescriptive memory taxonomy. It defines exactly four memory types, each with when to write it, how to structure the body, and what *not* to save. It explicitly prohibits saving code patterns, git history, or ephemeral task details — the reasoning being these should be derived from live sources rather than recalled from potentially stale notes.

Codex CLI's memory is the most structured for retrieval: every memory fact that was used in a response must be cited with a `<oai-mem-citation>` XML block naming the exact files and line ranges that informed the answer, plus rollout IDs for tracking. It's essentially a citation system embedded in a chat interface.

Copilot CLI takes a different angle: SQL. You can query your full session history with `SELECT * FROM turns JOIN sessions` and it even has FTS5 full-text search. The prompt gives several example queries including one for "what bugs did I fix?" that expands to `WHERE search_index MATCH 'bug OR fix OR error OR crash OR regression'`.

---

### Project context files

Each agent has a named file it looks for in the project root (and sometimes parent directories) to inject project-specific instructions:

| Agent | File |
|-------|------|
| Claude Code | `CLAUDE.md` |
| Gemini CLI | `GEMINI.md` |
| Codex CLI | `AGENTS.md` |
| GitHub Copilot CLI | `plan.md` (session artifact, not committed) |
| OpenCode | None mentioned |
| Pi | Any file configured via `contextFiles` option |

These files serve the same purpose — per-repo standing instructions — but the naming reveals each company's branding instincts. Notably, Gemini CLI specifies a three-level hierarchy: `<global_context>` < `<extension_context>` < `<project_context>`, with project context always winning conflicts. Claude Code handles the same via CLAUDE.md precedence rules documented in the harness.

---

### Commit authorship

| Agent | Co-author trailer |
|-------|------------------|
| Claude Code | `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` |
| GitHub Copilot CLI | `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` (real GitHub user ID: 223556219) |
| Gemini CLI | None |
| Codex CLI | None |
| OpenCode | None |
| Pi | None |

Copilot's co-author trailer uses a real GitHub account (user ID 223556219), which means its contributions show up on GitHub's contribution graphs and can be filtered in `git log`. Claude Code uses a `noreply@` address — valid git authorship but no GitHub profile attached.

---

### Modes and autonomy

| Agent | Named modes |
|-------|-------------|
| GitHub Copilot CLI | Autopilot, Fleet, Plan, Non-Interactive, Research Orchestrator, Sandboxed |
| Codex CLI | Default, Plan (via `collaboration_mode`) |
| Gemini CLI | Autonomous (YOLO), normal |
| Claude Code | Plan mode (via `EnterPlanMode` tool) |
| OpenCode | None |
| Pi | None — fully driven by tool selection and `customPrompt` |

Copilot CLI's **Fleet mode** is the most distinctive: it reads the SQL todo list, dispatches multiple sub-agents in parallel to handle independent todos, and coordinates results — functioning as an orchestrator over a pool of workers. Gemini CLI explicitly calls its autonomous mode "YOLO" in the prompt text.

---

### Personality and tone

| Agent | Persona |
|-------|---------|
| Codex CLI | Pluggable: `{{ personality }}` placeholder filled with `personality_friendly` or `personality_pragmatic` at runtime |
| Gemini CLI | "A senior software engineer and collaborative peer programmer" |
| GitHub Copilot CLI | Neutral / task-focused; no named persona |
| Claude Code | No explicit persona — the voice comes through style rules: "Brief is good — silent is not" |
| OpenCode | No persona — workmanlike CLI focus; "fewer than 3 lines of text per response" |
| Pi | No persona — defers entirely to the LLM's default character |

Codex CLI is the only agent that treats personality as a first-class, swappable module. The `{{ personality }}` token in the base prompt is replaced at runtime with a different block depending on whether the user has selected the "friendly" or "pragmatic" persona — the rest of the instructions remain identical.

Codex also contains one of the most memorable rules in any of these prompts: *"Never talk about goblins, gremlins, raccoons, trolls, ogres, pigeons, or other animals or creatures unless it is absolutely and unambiguously relevant to the user's query."* No other agent has anything like it.

---

### Shell safety and security

| Agent | Explicit shell security rules |
|-------|-------------------------------|
| GitHub Copilot CLI | Yes — explicit prompt-injection defense: detects and refuses `${var@P}` parameter transformation operator and `eval`-like constructs that dynamically build commands from variable contents |
| Claude Code | Yes — destructive git command blocklist; never `--no-verify`; parallel tool calls require independent operations |
| Gemini CLI | Yes — explains modifying commands before running; no `ask_user` for permission |
| Codex CLI | Yes — never `git reset --hard` without explicit request; ASCII-only file edits by default |
| OpenCode | Minimal — explain modifying commands before running; no further defenses |
| Pi | Minimal — "Explain commands that modify the file system" |

Copilot CLI's shell injection section is the most technical: it names the specific bash expansion syntax being defended against (`${var@P}`) and explains why it's dangerous. This is the only prompt that explicitly addresses prompt-injection-via-shell as a distinct threat category.

---

### What's unique to each

**Claude Code** is the only agent with a *typed* memory taxonomy (user / feedback / project / reference), with detailed rules for what each type should and shouldn't contain. It's also the only one that embeds billing metadata (`cc_version`, `cc_entrypoint`) directly in the system prompt header — a sign that the prompt is assembled server-side with per-request context.

**GitHub Copilot CLI** is the most feature-complete multi-agent harness of the group. The REM agent (background memory consolidation), rubber-duck critic, subconscious sidekick, and fleet orchestration are ideas you don't see in the others. It also has the only SQLite-backed session history — you can literally write SQL against your past conversations.

**Gemini CLI** is the only one with a formal **Directive vs. Inquiry** distinction: if you say "there's a bug in the auth module," that's an Inquiry — Gemini will analyze and propose a fix but won't touch a file until you issue a Directive. It's also the only one that explicitly forbids TailwindCSS by default when building new apps ("prefer Vanilla CSS"), which will either delight or infuriate you.

**Codex CLI** has the richest frontend / UI guidance of any agent here — two full pages covering icon libraries (lucide), border radius limits (8px or less), hero layouts, gradient restrictions, font scaling, palette monotony detection, and more. It also has the only explicit `{{ personality }}` pluggability system and the only dual-channel response model (commentary updates during work, final message when done).

**OpenCode** is the only agent that includes **worked conversation examples** directly in the system prompt — a short dialogue log showing how the model should handle specific user inputs. The examples go from trivially terse (`"1 + 2" → "3"`, `"is 13 a prime number?" → "true"`) to a full multi-step refactoring walkthrough with tool calls annotated inline. No other agent teaches by example like this. OpenCode also shares the most DNA with Gemini CLI: both follow a Research → Plan → Implement → Verify loop, both cap text output at 3 lines per response, and both avoid the sub-agent / memory complexity of Claude Code and Copilot CLI. The difference is that Gemini CLI is much more verbose about the reasoning behind each rule, while OpenCode states mandates flatly and trusts the examples to fill in the gaps.

**Pi** is the only fully open-source agent in this group (MIT license, source on GitHub). Its core prompt is intentionally thin — the philosophy is that complexity belongs in extensions and skills, not in a massive hardcoded string. The prompt itself has no memory, no modes, no sub-agents; everything is assembled programmatically from whatever tools and context files are active. It's the most hackable of the five — and uniquely, Pi is also a *framework*: **OpenClaw** (Peter Steinberger's viral agent harness, formerly ClawdBot/MoltBot) is built directly on Pi's npm packages (`@earendil-works/pi-coding-agent`, `@earendil-works/pi-ai`, `@earendil-works/pi-tui`). OpenClaw connects Pi to communication channels (Slack, Discord, etc.) and runs it as a persistent 24/7 service. It was this usage pattern — Claude subscription credentials powering always-on OpenClaw instances — that triggered Anthropic's April 2026 ban on third-party OAuth auth and ultimately led to the Agent SDK credits system. Pi the coding agent became Pi the SDK almost by accident.

---

### Feature matrix

| Feature | Claude Code | Copilot CLI | Gemini CLI | Codex CLI | OpenCode | Pi |
|---------|:-----------:|:-----------:|:----------:|:---------:|:--------:|:--:|
| Sub-agents | ✓ | ✓ | ✓ | — | — | — |
| Persistent memory | ✓ | ✓ | ✓ | ✓ | — | — |
| SQL session history | — | ✓ | — | — | — | — |
| Pluggable personality | — | — | — | ✓ | — | — |
| Named modes (autopilot etc.) | partial | ✓ | ✓ | ✓ | — | — |
| Prompt injection defense | ✓ | ✓ | partial | partial | — | — |
| Git commit co-author | ✓ | ✓ | — | — | — | — |
| Browser automation agent | — | — | ✓ | — | — | — |
| Open source / embeddable SDK | — | — | — | — | — | ✓ |
| Project context file | CLAUDE.md | plan.md | GEMINI.md | AGENTS.md | — | configurable |
| Skills / slash commands | ✓ | — | ✓ | — | /help /bug | ✓ |
| Topic progress updates | — | — | ✓ | via commentary | — | — |
| Worked examples in prompt | — | — | — | — | ✓ | — |

---

## Sources

Prompts were sourced from these public repositories:

- [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) — ChatGPT, Claude, Gemini, Grok, Perplexity, and more
- [x1xhlol/system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) — Cursor, Windsurf, Devin, Replit, Lovable, v0, Manus, Augment Code
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — Claude Code sub-agent prompts, extracted from Claude Code source
- [badlogic/pi-mono](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) — Pi coding agent open-source TypeScript source
- [openclaw/openclaw](https://github.com/openclaw/openclaw) — OpenClaw, built on Pi's SDK packages (context for the Pi-as-framework story)
- [lucumr.pocoo.org — Pi: The Minimal Agent Within OpenClaw](https://lucumr.pocoo.org/2026/1/31/pi/) — Armin Ronacher's writeup explaining the Pi/OpenClaw relationship

## Disclaimer

These prompts are collected from public sources for research and educational purposes. All trademarks belong to their respective owners.
