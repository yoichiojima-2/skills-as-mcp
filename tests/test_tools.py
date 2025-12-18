"""Tests for tool bundling."""

from pathlib import Path

import pytest

from skills_as_mcp.core.loader import SkillLoader


@pytest.fixture
def loader():
    return SkillLoader()


@pytest.fixture
def skills_dir():
    return Path(__file__).parent.parent / "skills"


def test_load_skill_with_tools(loader: SkillLoader, skills_dir: Path):
    """Test loading a skill with bundled tools."""
    skill_path = skills_dir / "code-review"
    skill = loader.load_skill(skill_path)

    assert skill is not None
    assert skill.metadata.has_tools is True
    assert len(skill.tools) == 2

    tool_names = [t.name for t in skill.tools]
    assert "code-review__analyze_complexity" in tool_names
    assert "code-review__check_style" in tool_names


def test_tool_execution(loader: SkillLoader, skills_dir: Path):
    """Test executing bundled tools."""
    skill_path = skills_dir / "code-review"
    skill = loader.load_skill(skill_path)

    # Find analyze_complexity tool
    analyze_tool = next(t for t in skill.tools if "analyze_complexity" in t.name)

    result = analyze_tool.callable(code="def foo(): pass", language="python")
    assert "total_lines" in result
    assert "functions" in result
    assert result["functions"] == 1


def test_tool_has_description(loader: SkillLoader, skills_dir: Path):
    """Test that tools have descriptions."""
    skill_path = skills_dir / "code-review"
    skill = loader.load_skill(skill_path)

    for tool in skill.tools:
        assert tool.description, f"Tool {tool.name} should have a description"
