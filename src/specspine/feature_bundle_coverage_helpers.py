from __future__ import annotations

__all__ = [
    "_strip_markdown_code",
    "_test_coverage_target_path",
]


def _strip_markdown_code(text: str) -> str:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped.startswith("`") and stripped.endswith("`"):
        return stripped[1:-1].strip()
    return stripped


def _test_coverage_target_path(target: str) -> str:
    return _strip_markdown_code(target).split("::", 1)[0].strip()
