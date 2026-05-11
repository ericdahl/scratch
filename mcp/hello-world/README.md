# hello-world MCP

A minimal MCP server with two tools, implemented in pure Python (stdlib only).

**Tools:**
- `get_time` — returns current UTC time as ISO 8601
- `run_shell` — runs a shell command, returns stdout/stderr

## Transports

Two implementations of the same server, one per transport generation:

| Directory | Transport | MCP spec | Status |
|-----------|-----------|----------|--------|
| [`http/`](http/) | Streamable HTTP | 2025-03-26 | Current — use this |
| [`sse/`](sse/) | HTTP+SSE | 2024-11-05 | Legacy — educational reference |

## Which to use?

Use `http/` unless you have a specific reason to need the older protocol. Claude Code 2.1+ uses the Streamable HTTP transport.

The SSE version is useful for understanding how the older two-channel protocol worked: a persistent SSE connection carries responses back to the client, while POSTs carry requests to the server.

## stdio alternative

Both implementations support only the HTTP transports shown. For a stdio transport (where Claude Code forks the process directly), the dispatch logic is identical — swap the transport layer for a stdin/stdout read loop.
