#!/usr/bin/env python3
"""
Entry point for running the Tachikoma MCP Server.
"""

import asyncio
from src.tachikoma_mcp.server import TachikomaMCPServer


def main():
    """Main entry point."""
    server = TachikomaMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
