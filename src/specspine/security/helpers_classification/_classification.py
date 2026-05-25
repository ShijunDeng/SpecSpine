from __future__ import annotations

__all__ = [
    "_classify_changed_file",
]


def _classify_changed_file(path: str) -> str:
    if path.startswith("src/specspine/") and path.endswith(".py"):
        return "source"
    if path.startswith("tests/test_") and path.endswith(".py"):
        return "test"
    if path.startswith("specs/features/") and path.endswith(".md"):
        return "feature-spec"
    if path.startswith("execution/features/") and path.endswith(".md"):
        return "feature-execution"
    if path.startswith("quality/features/") and path.endswith(".md"):
        return "feature-quality"
    if (
        path in {"README.md", "AGENTS.md"}
        or path.startswith("docs/")
        or path
        in {
            "execution/plan.md",
            "quality/review.md",
            "specs/architecture.md",
            "specs/product.md",
        }
    ):
        return "project-doc"
    if path == "pyproject.toml" or path.startswith(".github/") or path.startswith(
        ".specspine/"
    ):
        return "config"
    return "other"
