#!/usr/bin/env python3
"""
Orchestrator MCP Server entry point
"""

from .main import main
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)

def orchestrator_main():
    """Main entry point for the orchestrator CLI command."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    orchestrator_main()