#!/usr/bin/env python3
"""Render a captured Anthropic Messages API request into a browsable HTML page.

    python3 render_payload.py dumps/<capture>/request.json out.html

Identifiers that are not useful for reading the payload (billing header,
device/account/session UUIDs) are redacted before embedding.
"""
import json, sys, html
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("payload.html")
r = json.load(open(src))

def size(o):
    return len(json.dumps(o, separators=(",", ":")))

# --- redact identifiers -------------------------------------------------
if "metadata" in r:
    r["metadata"] = {"user_id": "[redacted: device_id / account_uuid / session_id]"}
for b in (r.get("system") or []):
    if isinstance(b, dict) and b.get("text", "").startswith("x-anthropic-billing-header"):
        b["text"] = "x-anthropic-billing-header: [redacted]"

total = size(r)
seg = {
    "system":   size(r.get("system") or []),
    "tools":    size(r.get("tools") or []),
    "messages": size(r.get("messages") or []),
}
seg["envelope"] = max(total - sum(seg.values()), 0)

def label_for(text):
    """Name a message text block by what it actually is."""
    t = text.strip()
    if t.startswith("<system-reminder>"):
        body = t[len("<system-reminder>"):].strip()
        first = next((l for l in body.splitlines() if l.strip()), "")
        return "system-reminder", first.strip().lstrip("#").strip()[:70] or "(context)"
    return "prompt", t[:70]

system_blocks = []
for i, b in enumerate(r.get("system") or []):
    txt = b.get("text", "") if isinstance(b, dict) else str(b)
    system_blocks.append({
        "idx": i, "chars": len(txt), "bytes": size(b),
        "cache": b.get("cache_control") if isinstance(b, dict) else None,
        "text": txt,
    })

tools = []
for t in (r.get("tools") or []):
    tools.append({
        "name": t.get("name", "?"), "bytes": size(t),
        "desc": t.get("description", ""),
        "schema": json.dumps(t.get("input_schema", {}), indent=2),
    })
tools.sort(key=lambda x: -x["bytes"])

messages = []
for i, m in enumerate(r.get("messages") or []):
    c = m.get("content")
    blocks = []
    if isinstance(c, list):
        for b in c:
            bt = b.get("type")
            if bt == "text":
                kind, lab = label_for(b.get("text", ""))
                body = b.get("text", "")
            elif bt == "tool_use":
                kind, lab = "tool_use", b.get("name", "")
                body = json.dumps(b.get("input", {}), indent=2)
            elif bt == "tool_result":
                kind, lab = "tool_result", b.get("tool_use_id", "")
                body = b.get("content") if isinstance(b.get("content"), str) else json.dumps(b.get("content"), indent=2)
            elif bt == "thinking":
                kind, lab = "thinking", f"signature {len(b.get('signature',''))} chars"
                body = b.get("thinking") or "(empty — encrypted signature only)"
            else:
                kind, lab, body = bt or "?", "", json.dumps(b, indent=2)
            blocks.append({"kind": kind, "label": lab, "bytes": size(b),
                           "cache": b.get("cache_control"), "body": body})
    else:
        blocks.append({"kind": "text", "label": "", "bytes": size(c), "cache": None, "body": str(c)})
    messages.append({"idx": i, "role": m.get("role"), "bytes": size(m), "blocks": blocks})

envelope = {k: v for k, v in r.items() if k not in ("system", "tools", "messages")}

data = {
    "source": src.parent.name, "total": total, "seg": seg,
    "model": r.get("model"), "system": system_blocks, "tools": tools,
    "messages": messages, "envelope": json.dumps(envelope, indent=2),
    "cacheCount": json.dumps(r).count('"cache_control"'),
}
payload = json.dumps(data).replace("</", "<\\/")
tpl = Path(__file__).parent / "template.html"
out.write_text(tpl.read_text().replace("__DATA__", payload))
print(f"wrote {out} ({out.stat().st_size:,} bytes) from {src}")
