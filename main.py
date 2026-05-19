"""Entry point - loads .env before starting MCP server."""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from accurate_mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
