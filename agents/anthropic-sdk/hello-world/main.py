#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "anthropic",
#   "httpx",
# ]
# ///

import json
import httpx
import anthropic


def log_request(request: httpx.Request) -> None:
    body = json.loads(request.content)
    print(json.dumps({
        "direction": "REQUEST",
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body,
    }, indent=2))


def log_response(response: httpx.Response) -> None:
    response.read()
    body = json.loads(response.content)
    print(json.dumps({
        "direction": "RESPONSE",
        "status": response.status_code,
        "headers": dict(response.headers),
        "body": body,
    }, indent=2))


client = anthropic.Anthropic(
    http_client=httpx.Client(
        event_hooks={"request": [log_request], "response": [log_response]}
    )
)

client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is 2 + 2?"}],
)
