#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "claude-agent-sdk",
#   "anyio",
# ]
# ///

import anyio
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)


anyio.run(main)
