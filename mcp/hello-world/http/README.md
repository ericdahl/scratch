# hello-world MCP — Streamable HTTP (2025-03-26)

Single-endpoint HTTP server. Claude POSTs JSON-RPC, server responds with JSON.
No SSE session dance, no session IDs.

## Run

```
python3 mcp_server.py [--host localhost] [--port 8000]
```

## Claude Code config

Add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "hello-world": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## curl test

```bash
# initialize
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"curl","version":"0.1"}}}'

# list tools
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# call get_time
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_time","arguments":{}}}'

# call run_shell
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"run_shell","arguments":{"command":"echo hello world"}}}'
```

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/mcp` | POST | JSON-RPC requests and notifications |
| `/mcp` | GET | SSE stream for server-initiated messages (keepalive only for this server) |
| `/.well-known/oauth-protected-resource` | GET | OAuth metadata — tells clients no auth is required |

## Adding tools

1. Add an entry to the `TOOLS` list (name, description, inputSchema)
2. Add a branch in `call_tool()` that handles the new name and returns a string
