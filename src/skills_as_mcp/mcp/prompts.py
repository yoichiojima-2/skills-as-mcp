"""MCP prompts protocol handlers."""

from mcp.server.fastmcp import FastMCP

from skills_as_mcp.core.registry import SkillRegistry


def setup_prompts(mcp: FastMCP, registry: SkillRegistry) -> None:
    """Register MCP prompts from skills."""
    for metadata in registry.list_skills():

        @mcp.prompt(name=metadata.name, description=metadata.description)
        def skill_prompt(name: str = metadata.name) -> str:
            """Return skill content as a prompt."""
            skill = registry.get_skill(name)
            if skill and skill.content:
                return skill.content.instructions
            return f"Skill '{name}' not found or has no content."
