"""mitmproxy addon: dump exact LLM API request/response payloads to disk.

Usage:  mitmweb -s dump_llm.py --allow-hosts '...'
Files land in ./dumps/NNNN-<client>-<host><path>/{request.json,request.headers,response.sse,response.headers}
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from mitmproxy import http

OUT = Path(__file__).parent / "dumps"

# Paths that carry a model-inference payload. Everything else is ignored.
INFERENCE_PATH = re.compile(
    r"/(v1/messages|v1/complete|v1/responses|chat/completions|"
    r"generateContent|streamGenerateContent|codex/responses|converse|invoke-with-response-stream)"
)


def _client(flow: http.HTTPFlow) -> str:
    ua = flow.request.headers.get("user-agent", "")
    xapp = flow.request.headers.get("x-app", "")
    if "claude-cli" in ua or xapp == "cli":
        return "claude"
    if "pi" in ua.split("/")[0].lower():
        return "pi"
    return re.sub(r"[^A-Za-z0-9._-]", "_", ua.split("/")[0])[:24] or "unknown"


class DumpLLM:
    def __init__(self) -> None:
        self.n = 0

    def _match(self, flow: http.HTTPFlow) -> bool:
        return bool(INFERENCE_PATH.search(flow.request.path))

    def request(self, flow: http.HTTPFlow) -> None:
        if not self._match(flow):
            return
        self.n += 1
        stamp = datetime.now().strftime("%H%M%S")
        d = OUT / f"{self.n:04d}-{stamp}-{_client(flow)}-{flow.request.host}"
        d.mkdir(parents=True, exist_ok=True)
        flow.metadata["dumpdir"] = d

        hdrs = "\n".join(f"{k}: {v}" for k, v in flow.request.headers.items())
        (d / "request.headers").write_text(
            f"{flow.request.method} {flow.request.path} {flow.request.http_version}\n{hdrs}\n"
        )

        raw = flow.request.get_content(strict=False) or b""
        try:
            body = json.loads(raw)
            (d / "request.json").write_text(json.dumps(body, indent=2, ensure_ascii=False))
            self._summarize(d, body)
        except Exception:
            (d / "request.body").write_bytes(raw)

    def _summarize(self, d: Path, body: dict) -> None:
        msgs = body.get("messages") or body.get("input") or []
        sysblk = body.get("system") or body.get("instructions")
        sys_len = len(json.dumps(sysblk)) if sysblk else 0
        tools = body.get("tools") or []
        lines = [
            f"model:        {body.get('model')}",
            f"stream:       {body.get('stream')}",
            f"max_tokens:   {body.get('max_tokens')}",
            f"system chars: {sys_len}",
            f"tools:        {len(tools)}  {[t.get('name') or (t.get('function') or {}).get('name') for t in tools]}",
            f"messages:     {len(msgs)}",
        ]
        for i, m in enumerate(msgs if isinstance(msgs, list) else []):
            c = m.get("content")
            if isinstance(c, list):
                kinds = [b.get("type") for b in c if isinstance(b, dict)]
                desc = f"{len(c)} block(s) {kinds}"
            else:
                desc = f"{len(str(c))} chars"
            # Multi-turn Responses API input mixes message items (role) with
            # reasoning items (no role, only type) - neither is guaranteed present.
            label = m.get("role") or m.get("type") or "?"
            lines.append(f"  [{i:>2}] {label:<9} {desc}")
        (d / "SUMMARY.txt").write_text("\n".join(lines) + "\n")
        logging.info(f"[dump_llm] {d.name}  model={body.get('model')} msgs={len(msgs)} tools={len(tools)}")

    # --- WebSocket transports (pi's openai-codex provider uses one) ---------
    # There is no HTTP body on these flows; the model payload rides in frames.

    def websocket_message(self, flow: http.HTTPFlow) -> None:
        d = flow.metadata.get("dumpdir")
        if d is None:
            return
        m = flow.websocket.messages[-1]
        direction = "c2s" if m.from_client else "s2c"
        try:
            text = m.content.decode("utf-8")
        except UnicodeDecodeError:
            text = None

        with (d / "websocket.jsonl").open("a") as fh:
            fh.write(json.dumps({
                "ts": m.timestamp,
                "dir": direction,
                "type": "text" if text is not None else "binary",
                "data": text if text is not None else m.content.hex(),
            }) + "\n")

        if text is None:
            return
        try:
            body = json.loads(text)
        except ValueError:
            return

        # Client frames carry the outbound request; dump each one readably.
        if m.from_client:
            n = flow.metadata["wsn"] = flow.metadata.get("wsn", 0) + 1
            (d / f"ws-{n:03d}-c2s.json").write_text(json.dumps(body, indent=2, ensure_ascii=False))
            payload = body.get("response") or body.get("session") or body
            if any(k in payload for k in ("model", "instructions", "input", "messages", "tools")):
                self._summarize(d, payload)

    def responseheaders(self, flow: http.HTTPFlow) -> None:
        """Tee the response to disk while streaming it through, so the agent's
        UI stays live instead of stalling until the full SSE body is buffered."""
        if not self._match(flow) or "dumpdir" not in flow.metadata:
            return
        d: Path = flow.metadata["dumpdir"]
        hdrs = "\n".join(f"{k}: {v}" for k, v in flow.response.headers.items())
        (d / "response.headers").write_text(
            f"{flow.response.status_code} {flow.response.reason}\n{hdrs}\n"
        )
        fh = (d / "response.sse").open("wb")

        def tee(chunk: bytes) -> bytes:
            if chunk:
                fh.write(chunk)
                fh.flush()
            else:
                fh.close()
            return chunk

        flow.response.stream = tee


addons = [DumpLLM()]
