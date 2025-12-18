"""Skill loading and parsing utilities."""

import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Any, Callable

import frontmatter

from skills_as_mcp.core.models import (
    Skill,
    SkillArgument,
    SkillContent,
    SkillMetadata,
    SkillTool,
)

logger = logging.getLogger(__name__)


class SkillLoadError(Exception):
    """Error loading a skill."""


class SkillLoader:
    """Loads and parses skill definitions."""

    SKILL_FILE = "SKILL.md"
    TOOLS_FILE = "tools.py"
    RESOURCES_DIR = "resources"

    def load_metadata(self, skill_path: Path, source: str = "project") -> SkillMetadata | None:
        """Load only the metadata from a skill directory.

        Args:
            skill_path: Path to skill directory
            source: Source type (builtin, user, project)

        Returns:
            SkillMetadata if valid skill, None otherwise
        """
        skill_file = skill_path / self.SKILL_FILE
        if not skill_file.exists():
            return None

        try:
            post = frontmatter.load(skill_file)
            name = post.get("name")
            description = post.get("description")

            if not name or not description:
                logger.warning(f"Skill at {skill_path} missing name or description")
                return None

            has_tools = (skill_path / self.TOOLS_FILE).exists()

            return SkillMetadata(
                name=name,
                description=description,
                has_tools=has_tools,
                source=source,
                path=skill_path.resolve(),
            )
        except Exception as e:
            logger.warning(f"Error loading skill metadata from {skill_path}: {e}")
            return None

    def load_content(self, skill_path: Path) -> SkillContent:
        """Load the full content of a skill.

        Args:
            skill_path: Path to skill directory

        Returns:
            SkillContent with instructions and resources
        """
        skill_file = skill_path / self.SKILL_FILE
        post = frontmatter.load(skill_file)

        arguments = []
        if "arguments" in post.metadata:
            for arg in post.metadata["arguments"]:
                arguments.append(
                    SkillArgument(
                        name=arg["name"],
                        description=arg.get("description", ""),
                        required=arg.get("required", False),
                        default=arg.get("default"),
                    )
                )

        resources = self._discover_resources(skill_path)

        return SkillContent(
            instructions=post.content,
            base_path=skill_path.resolve(),
            arguments=arguments,
            resources=resources,
        )

    def load_tools(self, skill_path: Path, skill_name: str) -> list[SkillTool]:
        """Load tools from a skill's tools.py.

        Args:
            skill_path: Path to skill directory
            skill_name: Name of the skill (for namespacing)

        Returns:
            List of SkillTool definitions
        """
        tools_file = skill_path / self.TOOLS_FILE
        if not tools_file.exists():
            return []

        try:
            module = self._load_module(tools_file, f"skill_{skill_name}_tools")
            return self._extract_tools(module, skill_name)
        except Exception as e:
            logger.error(f"Error loading tools from {tools_file}: {e}")
            return []

    def load_skill(self, skill_path: Path, source: str = "project", load_content: bool = True) -> Skill | None:
        """Load a complete skill from a directory.

        Args:
            skill_path: Path to skill directory
            source: Source type (builtin, user, project)
            load_content: Whether to load full content (lazy loading if False)

        Returns:
            Skill if valid, None otherwise
        """
        metadata = self.load_metadata(skill_path, source)
        if metadata is None:
            return None

        content = None
        tools = []

        if load_content:
            content = self.load_content(skill_path)
            if metadata.has_tools:
                tools = self.load_tools(skill_path, metadata.name)

        return Skill(metadata=metadata, content=content, tools=tools)

    def _discover_resources(self, skill_path: Path) -> list[str]:
        """Discover resource files in the resources directory."""
        resources_dir = skill_path / self.RESOURCES_DIR
        if not resources_dir.exists():
            return []

        resources = []
        for path in resources_dir.rglob("*"):
            if path.is_file():
                resources.append(str(path.relative_to(skill_path)))
        return sorted(resources)

    def _load_module(self, path: Path, module_name: str):
        """Dynamically load a Python module from a file."""
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise SkillLoadError(f"Could not load module from {path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _extract_tools(self, module, skill_name: str) -> list[SkillTool]:
        """Extract tool definitions from a loaded module.

        Looks for functions decorated with @tool or having a _tool_metadata attribute,
        or all public functions if no decorators are found.
        """
        tools = []

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_"):
                continue

            if hasattr(obj, "_tool_metadata"):
                metadata = obj._tool_metadata
                tools.append(
                    SkillTool(
                        name=f"{skill_name}__{name}",
                        description=metadata.get("description", obj.__doc__ or ""),
                        parameters=metadata.get("parameters", {}),
                        callable=obj,
                    )
                )
            elif obj.__doc__:
                tools.append(
                    SkillTool(
                        name=f"{skill_name}__{name}",
                        description=obj.__doc__,
                        parameters=self._infer_parameters(obj),
                        callable=obj,
                    )
                )

        return tools

    def _infer_parameters(self, func: Callable[..., Any]) -> dict[str, Any]:
        """Infer JSON Schema parameters from function signature."""
        sig = inspect.signature(func)
        hints = getattr(func, "__annotations__", {})

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = hints.get(param_name, str)
            json_type = self._python_type_to_json(param_type)

            properties[param_name] = {"type": json_type}

            if param.default is inspect.Parameter.empty:
                required.append(param_name)
            else:
                properties[param_name]["default"] = param.default

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def _python_type_to_json(self, python_type: type) -> str:
        """Convert Python type to JSON Schema type."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_map.get(python_type, "string")


def tool(description: str | None = None, parameters: dict | None = None):
    """Decorator to mark a function as a skill tool.

    Usage:
        @tool(description="Analyze code for issues")
        def analyze(code: str) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        func._tool_metadata = {
            "description": description or func.__doc__ or "",
            "parameters": parameters or {},
        }
        return func

    return decorator
