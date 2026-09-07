# scratch

Throwaway experiments and notes, mostly around LLM agent tooling. Nothing here is a
maintained project — each directory is a self-contained thing I built to understand how
something works, kept in case it's useful to someone else.

## [`agents/`](agents/)

Comparison of the `claude-agent-sdk` (which drives the Claude Code CLI as a subprocess)
against the `anthropic` SDK (direct API calls), with measurements rather than guesses:

- **Token overhead** — a default `claude-agent-sdk` query costs ~13,500 input tokens
  before your prompt; `tools=[]` cuts it to ~2,100 and `setting_sources=[]` to ~158.
  Breaks down where each chunk comes from and which knobs actually remove it.
- **Prompt caching** — cache hit/miss latency and cost.
- **Request logging** — full HTTP request/response capture via `httpx` hooks, for
  seeing exactly what gets sent.

Scripts use `uv` inline dependencies and are directly executable.

## [`mcp/`](mcp/)

Minimal MCP servers written against the raw protocol — stdlib only, no SDK — to see
what the transports actually do on the wire. The same two-tool server implemented in
both Streamable HTTP (2025-03-26) and the legacy HTTP+SSE (2024-11-05) transports,
with a comparison of when you'd pick each.

## [`system-prompts/`](system-prompts/)

Reference material, not my own work: a collection of extracted/leaked system prompts
from ~25 AI coding agents and chat products, gathered from public repositories and
organized by vendor. Useful for seeing how different products structure agent
instructions. These are snapshots and go stale quickly.
