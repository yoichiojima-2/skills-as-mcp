"""Bridge layer exposing skills as MCP tools."""

from mcp.server.fastmcp import FastMCP

from skills_as_mcp.core.registry import SkillRegistry


def setup_bridge_tools(mcp: FastMCP, registry: SkillRegistry) -> None:
    """Register bridge tools on the MCP server."""

    @mcp.tool()
    def list_skills() -> list[dict]:
        """List all available skills with their metadata.

        Returns a list of skills, each with:
        - name: Unique skill identifier
        - description: When and why to use this skill
        - has_tools: Whether the skill provides executable tools

        Use this to discover what skills are available before loading one.
        """
        skills = registry.list_skills()
        return [
            {
                "name": metadata.name,
                "description": metadata.description,
                "has_tools": metadata.has_tools,
            }
            for metadata in skills
        ]

    @mcp.tool()
    def load_skill(name: str) -> dict:
        """Load a skill's full instructions and make its tools available.

        Args:
            name: The skill name from list_skills()

        Returns:
            - instructions: The skill's markdown instructions
            - base_path: Path for resolving relative file references
            - available_tools: List of tool names now available to call

        Call this when you determine a skill matches the user's request.
        """
        skill = registry.get_skill(name)
        if skill is None:
            return {"error": f"Skill '{name}' not found"}

        if skill.content is None:
            return {"error": f"Skill '{name}' has no content"}

        tool_names = [t.name for t in skill.tools]

        for skill_tool in skill.tools:
            _register_skill_tool(mcp, skill_tool)

        return {
            "instructions": skill.content.instructions,
            "base_path": str(skill.content.base_path),
            "available_tools": tool_names,
            "resources": skill.content.resources,
        }


def _register_skill_tool(mcp: FastMCP, skill_tool) -> None:
    """Register a skill's tool on the MCP server."""

    @mcp.tool(name=skill_tool.name, description=skill_tool.description)
    def tool_wrapper(**kwargs):
        return skill_tool.callable(**kwargs)
