#!/bin/sh
# mitmweb UI on http://127.0.0.1:8081 ; proxy on 8080.
# --allow-hosts: only TLS-intercept model providers; everything else blind-tunnels
# through untouched (no cert errors for github, telemetry, npm, etc).
cd "$(dirname "$0")"
exec mitmweb \
  --listen-port 8080 \
  --store-streamed-bodies \
  --web-port 8081 \
  --allow-hosts '^(api\.anthropic\.com|api\.openai\.com|chatgpt\.com|openrouter\.ai|generativelanguage\.googleapis\.com|api\.mistral\.ai|bedrock-runtime\..*\.amazonaws\.com):443$' \
  --set view_filter='~u /v1/messages | ~u /chat/completions | ~u /v1/responses | ~u /codex/responses' \
  -w flows.mitm \
  -s dump_llm.py "$@"
