# Intercepting Coding-Agent Traffic

Capture the exact payloads `claude` (Claude Code) and `pi` send to their model providers,
using mitmproxy as a MITM proxy. Built 2026-09-07 on macOS with mitmproxy 12.2.3.

```
proxy/
├── run-proxy.sh       # start mitmweb with the right flags + addon
├── proxy-env.sh       # env vars to source in the agent's shell
├── dump_llm.py        # mitmproxy addon: writes payloads to dumps/
├── check-proxy.mjs    # preflight: does the proxy + CA actually work?
├── render_payload.py  # turn a captured request.json into a browsable HTML page
└── template.html      # the page render_payload.py fills in
```

## Minimal version

If you just want to eyeball a request, you don't need anything in this directory:

```sh
mitmweb                                     # terminal A (8080 proxy, 8081 UI — both defaults)
```
```sh
export HTTPS_PROXY=http://127.0.0.1:8080    # terminal B
export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem
claude                                      # or: pi
```

That is the whole requirement. `NODE_EXTRA_CA_CERTS` is the one non-obvious part and it is
**mandatory** — Node ships its own CA bundle and ignores the macOS keychain, so the usual
"install the mitmproxy CA system-wide" advice does nothing for these agents. Both `claude`
and `pi` are Node.

## Full setup

The scripts here add on-disk captures and a clean flow list. Nothing below is required:

```sh
# Terminal A — the proxy
./run-proxy.sh
# note the URL it prints: http://127.0.0.1:8081/?token=...

# Terminal B — the agent
source proxy-env.sh
node check-proxy.mjs     # optional preflight, should print 3x OK
claude                   # or: pi
```

What each addition buys you:

| | why |
|---|---|
| `-s dump_llm.py` | payloads on disk — greppable, diffable, and the only way to read WebSocket frames outside the browser |
| `--allow-hosts` | without it you MITM *everything*; Node survives via `NODE_EXTRA_CA_CERTS`, but `git`, `brew` and `curl` start failing cert checks mid-session |
| `--store-streamed-bodies` | needed *only* because the addon tees `flow.response.stream`; without the addon, mitmproxy buffers and shows bodies anyway |
| `--set view_filter` / `-w` | convenience |

Captures land in `dumps/NNNN-<time>-<client>-<host>/`:

| file | contents |
|---|---|
| `SUMMARY.txt` | model, system size, tool names, per-message roles |
| `request.json` | the request body, pretty-printed |
| `request.headers` | method, path, all headers (**includes live auth tokens**) |
| `response.sse` | raw SSE stream — **gzipped**, read with `gzip.open()` |
| `websocket.jsonl` | every WebSocket frame, both directions (pi only) |
| `ws-NNN-c2s.json` | each client→server frame, pretty-printed (pi only) |

Prereqs: `brew install mitmproxy`, then run it once to generate
`~/.mitmproxy/mitmproxy-ca-cert.pem`.

---

## Gotchas

Each of these cost real time. They are the reason this README exists.

**Never set `SSL_CERT_FILE`.** It *replaces* Node's CA bundle; `NODE_EXTRA_CA_CERTS`
*appends* to it. With `SSL_CERT_FILE` set, any host mitmproxy blind-tunnels presents its
real cert, which then has no issuer to chain to — surfacing as a bare `Error: fetch failed`
with cause `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`. Only `NODE_EXTRA_CA_CERTS` belongs in
`proxy-env.sh`.

**mitmweb mints a new auth token per process.** Restart the proxy and your open browser tab
silently 403s — the flow list just sits there empty, no error shown. Always reopen the
`?token=...` URL that Terminal A printed. There is no CLI flag to pin the token.

**`--allow-hosts` is required.** Without it mitmproxy intercepts *everything* the agent
touches (github, npm, telemetry) and you get cert failures plus unusable noise. The script
restricts TLS interception to model-provider hosts; everything else blind-tunnels through
untouched. Add hosts to that regex when switching providers.

**pi's `openai-codex` provider uses WebSockets, not HTTP.** It connects to
`chatgpt.com/backend-api/codex/responses` with `Upgrade: websocket`. The flow shows as a
`101` with a **zero-byte body** — Request and Response panes are empty by design. Click
mitmweb's **WebSocket** tab. `dump_llm.py` handles this via a `websocket_message` hook.

**Unknown addon hook names fail silently.** mitmproxy will not warn you. The real names are
`websocket_start` / `websocket_message` / `websocket_end`.

**Streaming vs. storage.** The addon tees `flow.response.stream` so bodies hit disk *and*
pass through live (otherwise mitmproxy buffers the whole SSE response and the agent's UI
appears frozen). Consequence: streamed bodies are not stored for mitmweb's UI, so
`run-proxy.sh` passes `--store-streamed-bodies` to get them back in the browser too.

**`flows.mitm` stays 0 bytes while a WebSocket is open.** `-w` only writes a flow on
completion, and pi holds its socket for the whole session. Use `dumps/`, which is written live.

**`dumps/` contains live credentials** — the `authorization` bearer, `x-api-key`, plus your
CLAUDE.md contents and local paths. Gitignored here. Scrub before sharing:

```sh
grep -rl -iE '^(authorization|x-api-key|cookie):' dumps/ | \
  xargs sed -i '' -E 's/^(authorization|x-api-key|cookie): .*/\1: [REDACTED]/I'
```

---

## Reading a big payload

Claude Code's main request is ~144 KB of JSON — effectively unreadable in mitmweb.

```sh
python3 render_payload.py dumps/<capture>/request.json payload.html
open payload.html
```

Produces a self-contained page: a byte-budget bar, then filterable expandable rows for every
tool schema, system block, and message. Redacts `metadata.user_id` and the billing header
before embedding. Edit `template.html` to restyle.

(A rendered example was published as a private Claude artifact; the link is deliberately
kept out of this public repo, since the page embeds a full system prompt and CLAUDE.md.)

---

## What the captures showed

Worth preserving, because it is the reason the setup is interesting.

### The two agents differ architecturally

| | pi + `gpt-5.6-luna` | Claude Code + Haiku |
|---|---|---|
| Transport | WebSocket | HTTP POST + SSE |
| Prior turns on the wire | **no** — `previous_response_id` | **yes** — full replay every turn |
| Where context lives | provider's servers | your machine, resent each turn |
| Caching | requested, 0 hits | 36,290 / 36,713 tokens read from cache (98.8%) |
| Turn-2 payload | ~600 bytes | 156 KB |

pi sends `store: false` yet still chains by `previous_response_id`, and never echoes the
server's `x-codex-turn-state` header back — so the conversation genuinely lives server-side.
Two different answers to the same problem: pi minimizes **bytes on the wire**, Claude Code
keeps the wire fat and minimizes **cost per token**.

Caveat for auditing: pi has two modes. Within a live socket it chains by id; after a
reconnect it replays the transcript inline with `reasoning.encrypted_content` blocks. So pi
is only *conditionally* observable through a proxy, and its reasoning is encrypted either
way. Claude Code is complete by construction.

### Where Claude Code's 144 KB goes

```
tool schemas   86,111 B   59.9%   ← Artifact alone is 38,040 B
system prompt  29,735 B   20.7%
messages       27,467 B   19.1%
envelope          398 B    0.3%
```

Only 14 tool schemas are sent eagerly; the rest are deferred behind `ToolSearch` and
referenced by name only. 3 `cache_control` breakpoints, `ttl: 1h`.

### One prompt fans out to 7 requests

2 × `quota` probe (`max_tokens: 1`), 2 × session titling (Haiku, duplicated — same input,
same output, stored twice), 2 × main agent loop, 1 × status-line summarizer. Only two do
real work.

The session-titling call names the session for `claude --resume`; its output is stored as
an `ai-title` record in `~/.claude/projects/<dir>/<session-uuid>.jsonl`.

### Aside: cross-session messaging is not proxyable

Claude Code sessions message each other over Unix domain sockets at `/tmp/cc-socks/<pid>.sock`
(mode `0600` in a `0700` dir). No network, so a proxy never sees it; the security boundary is
filesystem permissions.
