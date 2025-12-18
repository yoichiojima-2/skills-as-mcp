"""Main MCP server entry point."""

import logging

from mcp.server.fastmcp import FastMCP

from skills_as_mcp.config import load_config
from skills_as_mcp.core.registry import SkillRegistry
from skills_as_mcp.mcp.bridge import setup_bridge_tools
from skills_as_mcp.mcp.prompts import setup_prompts


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    config = load_config()

    logging.basicConfig(level=config.log_level)

    mcp = FastMCP("skills-as-mcp")

    registry = SkillRegistry(config.skill_paths)
    registry.discover()

    setup_bridge_tools(mcp, registry)
    setup_prompts(mcp, registry)

    return mcp


def main():
    """Entry point for the server."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
