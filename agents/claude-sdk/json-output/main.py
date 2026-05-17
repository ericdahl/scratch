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
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(json.dumps({"type": type(message).__name__, **dataclasses.asdict(message)}, default=str))


anyio.run(main)
