---
name: code-review
description: |
  Review code for quality, bugs, security issues, and best practices.
  Use this skill when the user asks for code review, code analysis, or wants feedback on their code.
arguments:
  - name: language
    description: Programming language of the code
    required: false
    default: python
---

# Code Review Skill

This skill helps you perform thorough code reviews.

## Guidelines

When reviewing code, check for:
1. **Correctness** - Does the code do what it's supposed to?
2. **Security** - Are there any vulnerabilities?
3. **Performance** - Are there obvious inefficiencies?
4. **Readability** - Is the code clear and maintainable?
5. **Best Practices** - Does it follow language conventions?

## Available Tools

- `analyze_complexity`: Analyze code complexity metrics
- `check_style`: Check code style issues

## Usage

1. Call `analyze_complexity` to get metrics
2. Call `check_style` for style issues
3. Provide comprehensive feedback based on the results
