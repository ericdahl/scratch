# Claude Agent SDK Demos

Experiments comparing the `claude-agent-sdk` (Claude Code wrapper) against the `anthropic` SDK (direct API).

## Directory Structure

```
agents/
├── anthropic-sdk/
│   ├── hello-world/      # full HTTP req/response logging via httpx hooks
│   ├── prompt-caching/   # demonstrates cache hit/miss latency and cost savings
│   └── quick-start/      # minimal direct API call
└── claude-sdk/
    ├── json-output/          # all 4 SDK message types as JSON
    ├── quick-start/          # bare minimum
    └── unhelpful-assistant/  # custom system prompt demo
```

All scripts use `uv` inline dependencies and are directly executable (`./main.py`).

---

## SDK Comparison

| | `anthropic` | `claude-agent-sdk` |
|---|---|---|
| What it is | Direct HTTP client to `api.anthropic.com` | Spawns a `claude` CLI subprocess, communicates via control protocol |
| Auth | `ANTHROPIC_API_KEY` | `CLAUDE_CODE_OAUTH_TOKEN` |
| Tools | You define them | Full Claude Code toolset (Bash, Read, Edit, MCP, …) |
| System prompt | Yours only | Claude Code injects its own context on top |
| Use case | Build apps on the Claude API | Automate Claude Code agents |

---

## Token Overhead Analysis

Testing with `query(prompt="What is 2 + 2?")` across different `ClaudeAgentOptions` configurations:

### `claude-agent-sdk`

| Configuration | Input tokens | What's injected |
|---|---|---|
| Default | ~13,500 | Tool defs (~11k) + Claude Code system prompt + CLAUDE.md + MCP server instructions |
| `tools=[]` | ~2,100 | Custom prompt + CLAUDE.md + MCP instructions + SDK boilerplate |
| `tools=[], setting_sources=[]` | ~158 | Custom prompt + hardwired SDK prefix only |

**Hardwired SDK prefix** (cannot be removed without forking the CLI):
```
You are a Claude agent, built on Anthropic's Claude Agent SDK. <your system_prompt here>
```

**What `setting_sources=[]` strips:** CLAUDE.md content, MCP server instructions, user/project/local settings.

**What lives in the ~11k tool-definition tokens:** every Claude Code built-in tool (Bash, Read, Edit, Glob, Grep, …) plus MCP tool schemas. These are always injected regardless of `system_prompt` — only `tools=[]` removes them.

**What `--system-prompt <str>` actually does:** replaces the Claude Code *instructions* portion only. Tool definitions are injected separately and survive the replacement. Use `tools=[]` to remove those.

### `anthropic` SDK (direct)

| Configuration | Input tokens |
|---|---|
| No system prompt | ~16 |
| With system prompt | 16 + system prompt tokens |

Nothing is injected. You own 100% of the context.

---

## API Response Time

Both approaches showed ~2.9s API response time for this trivial query. That's expected — response time has two components:

1. **Time to first token (TTFT):** server receives request → KV cache prefill → first output token
2. **Generation time:** each additional output token (~20–80ms each)

For a one-token answer ("4"), generation time is essentially zero, so both cases measure pure TTFT. TTFT doesn't differ meaningfully between 16 and 13,000 input tokens because:

- Transformers prefill input tokens **in parallel** — 13k tokens isn't 800× slower than 16
- The ~13k tokens were **cache hits** (`cache_read_input_tokens`), making prefill even faster
- At ~2.9s, server scheduling + network RTT dominates over actual compute

Response time *would* diverge at:
- Long outputs (generation time scales linearly per token)
- Very large uncached inputs (100k+ where prefill starts to dominate)
- Server load differences

### `claude -p` timing

```sh
claude -p "..." --output-format json | jq '{duration_ms, duration_api_ms}'
```

- `duration_ms` — total wall time including CLI startup (~5s)
- `duration_api_ms` — just the API call (~2.9s)
- CLI startup overhead: ~2s (Node.js boot, settings load, MCP server connections)

The direct `anthropic` SDK eliminates this: total wall time was 2.9s, matching the API time alone.

---

## Prompt Caching (`anthropic-sdk/prompt-caching`)

Demo: three sequential requests using an ~8,600-token synthetic API reference doc as the system prompt.

1. **Baseline** — no `cache_control`, cold every time
2. **Cache create** — `cache_control: {type: ephemeral}` added, first call writes cache
3. **Cache hit** — identical request, reads from cache

```
                              baseline (no cache)    cache create       cache hit
------------------------------------------------------------------------------
ttft_ms                                    817             813             711
total_ms                                  1356            1391            1368
input                                     8615               3               3
cache_creation                               0            8612              12
cache_read                                   0               0            8600
output                                      37              39              39
cost_usd                                0.0264          0.0329          0.0032
```

### Findings

**Cost**: Cache hit ($0.0032) is ~8× cheaper than baseline ($0.0264). Scales linearly with request volume — a shared 8k-token system prompt sent 1,000×/day costs ~$26/day uncached vs ~$3.20/day with caching.

**TTFT**: 106ms faster on cache hit (817ms → 711ms, ~13% improvement). Modest here because generation time (~575ms for 38 output tokens at ~15ms/token) dominates total latency. TTFT savings matter more with larger documents and shorter outputs.

**Token accounting**: On cache runs, `input` drops to just 3 tokens (the user message). The system prompt tokens are reclassified entirely as `cache_creation` or `cache_read` — they don't appear in regular `input` at all. This is how billing works: pay the creation rate ($3.75/MTok) once, then the read rate ($0.30/MTok) on every hit.

**Cache boundary**: The tiny `cache_creation: 12` on the cache hit run is the user message and request framing just outside the cached prefix boundary — normal behaviour.

### Sonnet 4.6 pricing used

| Token type | Price/MTok |
|---|---|
| Input (uncached) | $3.00 |
| Cache creation | $3.75 |
| Cache read | $0.30 |
| Output | $15.00 |

Cache read is **10% of normal input cost**. Cache creation is a one-time 25% premium over normal input, amortised across all subsequent hits.
