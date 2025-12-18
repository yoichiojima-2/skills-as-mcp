"""Configuration management."""

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration for skills-as-mcp server."""

    user_skills_dir: Path = Field(default_factory=lambda: Path.home() / ".skills-as-mcp" / "skills")
    project_skills_dir: Path = Field(default_factory=lambda: Path.cwd() / "skills")
    log_level: str = "INFO"

    @property
    def skill_paths(self) -> list[Path]:
        """Return skill paths in priority order (later overrides earlier)."""
        return [self.user_skills_dir, self.project_skills_dir]


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        user_skills_dir=Path(os.getenv("SKILLS_AS_MCP_USER_DIR", str(Path.home() / ".skills-as-mcp" / "skills"))),
        project_skills_dir=Path(os.getenv("SKILLS_AS_MCP_PROJECT_DIR", str(Path.cwd() / "skills"))),
        log_level=os.getenv("SKILLS_AS_MCP_LOG_LEVEL", "INFO"),
    )
