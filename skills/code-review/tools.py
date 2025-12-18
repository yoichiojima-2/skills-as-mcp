"""Tools for code review skill."""


def analyze_complexity(code: str, language: str = "python") -> dict:
    """Analyze code complexity metrics.

    Args:
        code: The source code to analyze
        language: Programming language (default: python)

    Returns:
        Dictionary with complexity metrics
    """
    lines = code.strip().split("\n")
    non_empty = [l for l in lines if l.strip()]

    # Simple metrics
    metrics = {
        "total_lines": len(lines),
        "code_lines": len(non_empty),
        "blank_lines": len(lines) - len(non_empty),
        "language": language,
    }

    # Count basic structures (simplified)
    if language == "python":
        metrics["functions"] = sum(1 for l in lines if l.strip().startswith("def "))
        metrics["classes"] = sum(1 for l in lines if l.strip().startswith("class "))
        metrics["imports"] = sum(1 for l in lines if l.strip().startswith(("import ", "from ")))

    return metrics


def check_style(code: str, language: str = "python") -> list[dict]:
    """Check code for style issues.

    Args:
        code: The source code to check
        language: Programming language (default: python)

    Returns:
        List of style issues found
    """
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        # Check line length
        if len(line) > 120:
            issues.append({"line": i, "issue": "line_too_long", "message": f"Line exceeds 120 characters ({len(line)})"})

        # Check trailing whitespace
        if line != line.rstrip():
            issues.append({"line": i, "issue": "trailing_whitespace", "message": "Trailing whitespace"})

        # Python-specific checks
        if language == "python":
            # Check for tabs
            if "\t" in line:
                issues.append({"line": i, "issue": "tabs", "message": "Use spaces instead of tabs"})

    return issues
