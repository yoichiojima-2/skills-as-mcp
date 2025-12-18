# skills-as-mcp

MCP server that provides Claude Skills-like lazy-loading functionality via the Model Context Protocol.

## Concept

Claude Skills uses a three-tier progressive disclosure model:
1. **Metadata** (always loaded) - skill names and descriptions
2. **Instructions** (on-demand) - full SKILL.md content
3. **Tools** (on-demand) - bundled executable functions

MCP has prompts in its protocol, but they're user-driven. This project adds a **bridge layer** that exposes skills as MCP tools (`list_skills`, `load_skill`), enabling LLM-driven invocation.

## Installation

```bash
uv sync
```

## Usage

Run the server:
```bash
uv run skills-as-mcp
```

## Creating Skills

Create a directory in `skills/` with a `SKILL.md` file:

```yaml
---
name: my-skill
description: When and why to use this skill
---

# My Skill

Instructions for Claude when this skill is loaded.
```

Optional: Add `tools.py` to bundle executable functions.

## Architecture

```
MCP Client (Claude)
        │
        ▼
┌─────────────────────────────────┐
│     skills-as-mcp Server        │
├─────────────────────────────────┤
│  Bridge Layer (MCP Tools)       │
│  ├── list_skills()              │
│  └── load_skill(name)           │
├─────────────────────────────────┤
│  Skill Registry                 │
│  └── discover & cache skills    │
└─────────────────────────────────┘
        │
        ▼
    skills/
    ├── hello-world/SKILL.md
    └── ...
```
