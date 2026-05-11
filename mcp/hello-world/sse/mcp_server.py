#!/usr/bin/env python3
"""
Minimal MCP server — HTTP+SSE transport (MCP spec 2024-11-05).
stdlib only, no external dependencies.

NOTE: This transport is superseded by Streamable HTTP (2025-03-26).
      Modern clients (Claude Code 2.1+) use the HTTP transport instead.
      This implementation is kept for educational purposes and for clients
      that still speak the older protocol.

How it works:
  1. Client opens a long-lived GET /sse connection — server sends an "endpoint" event
     with a session-specific POST URL.
  2. Client POSTs JSON-RPC messages to that URL.
  3. Server sends responses back over the SSE stream (not as HTTP responses to the POST).

Usage:
  python3 mcp_server.py [--host localhost] [--port 8000]

Claude Code config (.mcp.json) — older clients only:
  {
    "mcpServers": {
      "my-mcp": {
        "type": "sse",
        "url": "http://localhost:8000/sse"
      }
    }
  }

curl test:
  # Terminal 1 — open SSE stream, note the endpoint URL printed
  curl -N http://localhost:8000/sse

  # Terminal 2 — send messages to the session endpoint
  curl -X POST "http://localhost:8000/message?sessionId=<id>" \\
    -H "Content-Type: application/json" \\
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"0.1"}}}'
"""

import argparse
import json
import logging
import queue
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mcp")

# ── Tools ──────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_time",
        "description": "Returns the current UTC time as ISO 8601",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_shell",
        "description": "Runs a shell command and returns stdout/stderr. Personal use only — do not expose publicly.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
            },
            "required": ["command"],
        },
    },
]


def call_tool(name, args):
    if name == "get_time":
        result = datetime.now(timezone.utc).isoformat()
        log.debug("tool get_time → %s", result)
        return result

    if name == "run_shell":
        command = args["command"]
        log.info("tool run_shell: %s", command)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            out = result.stdout
            if result.stderr:
                out += f"\nstderr: {result.stderr}"
            if result.returncode != 0:
                out += f"\nexit code: {result.returncode}"
                log.warning("run_shell exit %d: %s", result.returncode, command)
            else:
                log.debug("run_shell ok, %d bytes output", len(out))
            return out or "(no output)"
        except subprocess.TimeoutExpired:
            log.error("run_shell timed out: %s", command)
            return "error: command timed out after 30s"

    return None


# ── JSON-RPC dispatch ──────────────────────────────────────────────────────────

def handle_message(msg, session_id=""):
    """Returns a response dict, or None for notifications that need no reply."""
    method = msg.get("method", "")
    req_id = msg.get("id")
    params = msg.get("params", {})
    prefix = f"[{session_id[:8]}] " if session_id else ""

    if method == "initialize":
        client = params.get("clientInfo", {})
        log.info("%sinitialize — client: %s %s, protocol: %s",
                 prefix, client.get("name", "?"), client.get("version", ""),
                 params.get("protocolVersion", "?"))
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hello-world-mcp", "version": "0.1.0"},
            },
        }

    if method == "notifications/initialized":
        log.info("%sclient ready", prefix)
        return None

    if method == "tools/list":
        log.debug("%stools/list → %d tools", prefix, len(TOOLS))
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        log.info("%stools/call %s args=%s", prefix, name, arguments)
        result = call_tool(name, arguments)
        if result is None:
            log.warning("%sunknown tool: %s", prefix, name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"},
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": result}],
                "isError": False,
            },
        }

    if method == "ping":
        log.debug("%sping", prefix)
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if req_id is not None:
        log.warning("%sunknown method: %s", prefix, method)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
        }

    log.debug("%sunhandled notification: %s", prefix, method)
    return None


# ── HTTP+SSE handler ───────────────────────────────────────────────────────────

_sessions: dict[str, queue.Queue] = {}
_sessions_lock = threading.Lock()


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # handled manually

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/sse"):
            log.warning("GET %s — not found", self.path)
            self.send_error(404)
            return

        session_id = str(uuid.uuid4())
        short_id = session_id[:8]
        q: queue.Queue = queue.Queue()

        with _sessions_lock:
            _sessions[session_id] = q
            active = len(_sessions)

        log.info("SSE connect  session=%s  client=%s  active=%d",
                 short_id, self.client_address[0], active)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._cors()
        self.end_headers()

        host, port = self.server.server_address
        post_url = f"http://{host}:{port}/message?sessionId={session_id}"
        self._sse(f"event: endpoint\ndata: {post_url}\n\n")
        log.debug("SSE session=%s  endpoint sent: %s", short_id, post_url)

        keepalives = 0
        try:
            while True:
                try:
                    msg = q.get(timeout=30)
                    if msg is None:
                        break
                    self._sse(f"data: {json.dumps(msg)}\n\n")
                    log.debug("SSE session=%s  sent id=%s", short_id, msg.get("id"))
                except queue.Empty:
                    keepalives += 1
                    self._sse(": keepalive\n\n")
                    log.debug("SSE session=%s  keepalive #%d", short_id, keepalives)
        except (BrokenPipeError, ConnectionResetError):
            log.info("SSE session=%s  client disconnected", short_id)
        finally:
            with _sessions_lock:
                _sessions.pop(session_id, None)
                remaining = len(_sessions)
            log.info("SSE session=%s  cleaned up  active=%d", short_id, remaining)

    def do_POST(self):
        qs = parse_qs(urlparse(self.path).query)
        session_id = qs.get("sessionId", [None])[0]
        short_id = (session_id or "")[:8] or "unknown"

        with _sessions_lock:
            q = _sessions.get(session_id)

        if q is None:
            log.warning("POST — unknown session %s", short_id)
            self.send_error(404, "Unknown session")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # Acknowledge immediately — response will arrive via SSE
        self.send_response(202)
        self.send_header("Content-Length", "0")
        self._cors()
        self.end_headers()

        try:
            msg = json.loads(body)
        except json.JSONDecodeError as e:
            log.error("POST session=%s  JSON parse error: %s", short_id, e)
            return

        log.info("POST session=%s  method=%s id=%s", short_id, msg.get("method", "?"), msg.get("id"))

        response = handle_message(msg, session_id=session_id)
        if response:
            q.put(response)
            log.debug("POST session=%s  queued response id=%s", short_id, response.get("id"))

    def _sse(self, text: str):
        self.wfile.write(text.encode())
        self.wfile.flush()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP hello-world server (HTTP+SSE)")
    parser.add_argument("--host", default="localhost", help="Bind address")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MCPHandler)
    log.info("HTTP+SSE MCP server on http://%s:%d/sse", args.host, args.port)
    log.info("POST endpoint: http://%s:%d/message?sessionId=<id>", args.host, args.port)
    server.serve_forever()
