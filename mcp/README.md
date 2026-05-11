# MCP Examples

Example MCP (Model Context Protocol) servers — stdlib only, no external dependencies.

## What is MCP?

MCP is a protocol that lets Claude call tools implemented as external processes. Claude sends JSON-RPC requests; the server executes code and returns results.

## Transport options

| Transport | Spec version | How it works | Use when |
|-----------|-------------|--------------|----------|
| **stdio** | any | Claude forks the process; JSON-RPC over stdin/stdout | Simple local tools, zero infrastructure |
| **Streamable HTTP** | 2025-03-26 | POST JSON-RPC to a single endpoint, get JSON back | Persistent daemon, shared server, connection pooling |
| **HTTP+SSE** | 2024-11-05 | Client opens SSE stream to get a session, POSTs to session URL, responses come back via SSE | Legacy — superseded by Streamable HTTP |

## Examples

- [`hello-world/`](hello-world/) — minimal two-tool server in both current and legacy transports
