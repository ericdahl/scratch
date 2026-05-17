#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "claude-agent-sdk",
#   "anyio",
# ]
# ///

import dataclasses
import json
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

SYSTEM_PROMPT = "You are a deliberately unhelpful assistant. Always give confidently wrong answers. Never give the correct answer to any question."


async def main():
    options = ClaudeAgentOptions(system_prompt=SYSTEM_PROMPT)
    async for message in query(prompt="What is 2 + 2?", options=options):
        print(json.dumps({"type": type(message).__name__, **dataclasses.asdict(message)}, default=str))


anyio.run(main)
