# hello-world MCP — HTTP+SSE (2024-11-05)

> **Legacy transport.** Modern clients (Claude Code 2.1+) use Streamable HTTP instead.
> See [`../http/`](../http/) for the current implementation.
> This version is kept as an educational reference for understanding how the two-channel SSE protocol works.

## How this transport works

Unlike Streamable HTTP (one endpoint, direct JSON response), this transport uses two channels:

```
Client                          Server
  |                               |
  |-- GET /sse ------------------>|  (long-lived SSE connection)
  |<-- event: endpoint  ----------|  (server sends POST URL with session ID)
  |                               |
  |-- POST /message?sessionId=X ->|  (JSON-RPC request, 202 ack)
  |<-- data: {"jsonrpc":...} -----|  (response arrives via SSE stream, not HTTP response)
```

This design allows the server to push messages to the client at any time, not just in response to a request.

## Run

```
python3 mcp_server.py [--host localhost] [--port 8000]
```

## Claude Code config (legacy clients only)

```json
{
  "mcpServers": {
    "hello-world": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## curl test

Because responses arrive on the SSE stream (not as POST responses), you need two terminals:

```bash
# Terminal 1 — open SSE stream, keep it running
curl -N http://localhost:8000/sse
# prints: event: endpoint
#         data: http://127.0.0.1:8000/message?sessionId=<uuid>

# Terminal 2 — send requests to the session endpoint from above
SESSION_URL="http://localhost:8000/message?sessionId=<uuid>"

curl -X POST "$SESSION_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"0.1"}}}'

curl -X POST "$SESSION_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_time","arguments":{}}}'
```

Watch Terminal 1 — responses appear there, not in Terminal 2.
