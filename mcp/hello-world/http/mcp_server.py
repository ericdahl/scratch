#!/usr/bin/env python3
"""
Minimal MCP server — Streamable HTTP transport (MCP spec 2025-03-26).
stdlib only, no external dependencies.

Usage:
  python3 mcp_server.py [--host localhost] [--port 8000]

Claude Code config (.mcp.json):
  {
    "mcpServers": {
      "my-mcp": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
"""

import argparse
import json
import logging
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

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

def handle_message(msg):
    """Returns a response dict, or None for notifications that need no reply."""
    method = msg.get("method", "")
    req_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        client = params.get("clientInfo", {})
        log.info("initialize — client: %s %s, protocol: %s",
                 client.get("name", "?"), client.get("version", ""),
                 params.get("protocolVersion", "?"))
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hello-world-mcp", "version": "0.1.0"},
            },
        }

    if method == "notifications/initialized":
        log.info("client ready")
        return None

    if method == "tools/list":
        log.debug("tools/list → %d tools", len(TOOLS))
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        log.info("tools/call %s args=%s", name, arguments)
        result = call_tool(name, arguments)
        if result is None:
            log.warning("unknown tool: %s", name)
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
        log.debug("ping")
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if req_id is not None:
        log.warning("unknown method: %s", method)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
        }

    log.debug("unhandled notification: %s", method)
    return None


# ── HTTP handler ───────────────────────────────────────────────────────────────

_sse_clients: list = []
_sse_lock = threading.Lock()


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # handled manually

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/.well-known/oauth-protected-resource":
            # Tell clients this resource requires no authorization
            host, port = self.server.server_address
            self._json_response(200, {
                "resource": f"http://{host}:{port}",
                "bearer_methods_supported": [],
            })
            log.debug("served oauth metadata")
            return

        if path == "/mcp":
            # SSE stream for server-initiated messages (keepalive only; tools are request/response)
            log.info("SSE stream opened from %s", self.client_address[0])
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self._cors()
            self.end_headers()
            try:
                import time
                while True:
                    time.sleep(30)
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            log.info("SSE stream closed")
            return

        log.warning("GET %s — not found", path)
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/mcp":
            log.warning("POST %s — not found", path)
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            msg = json.loads(body)
        except json.JSONDecodeError as e:
            log.error("JSON parse error: %s", e)
            self.send_error(400, "Invalid JSON")
            return

        log.info("POST /mcp  method=%s id=%s  client=%s",
                 msg.get("method", "?"), msg.get("id"), self.client_address[0])

        response = handle_message(msg)

        if response:
            self._json_response(200, response)
            log.debug("responded id=%s", response.get("id"))
        else:
            self.send_response(202)
            self.send_header("Content-Length", "0")
            self._cors()
            self.end_headers()

    def _json_response(self, status, obj):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP hello-world server (Streamable HTTP)")
    parser.add_argument("--host", default="localhost", help="Bind address")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MCPHandler)
    log.info("Streamable HTTP MCP server on http://%s:%d/mcp", args.host, args.port)
    log.info("OAuth metadata:  http://%s:%d/.well-known/oauth-protected-resource", args.host, args.port)
    server.serve_forever()
