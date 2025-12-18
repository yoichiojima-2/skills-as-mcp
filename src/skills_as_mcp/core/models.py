"""Data models for skills."""

from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field


class SkillArgument(BaseModel):
    """Optional argument for skill parameterization."""

    name: str
    description: str
    required: bool = False
    default: Any = None


class SkillMetadata(BaseModel):
    """Lightweight metadata for skill discovery (always loaded)."""

    name: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=64)
    description: str = Field(..., max_length=1024)
    has_tools: bool = False
    source: Literal["builtin", "user", "project"] = "project"
    path: Path

    model_config = {"frozen": True}


class SkillContent(BaseModel):
    """Full skill content (loaded on-demand)."""

    instructions: str
    base_path: Path
    arguments: list[SkillArgument] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)


class SkillTool(BaseModel):
    """Tool bundled with a skill."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    callable: Callable[..., Any] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}


class Skill(BaseModel):
    """Complete skill representation."""

    metadata: SkillMetadata
    content: SkillContent | None = None
    tools: list[SkillTool] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
