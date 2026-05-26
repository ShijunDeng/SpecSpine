from __future__ import annotations

__all__ = [
    "_render_header",
]


def _render_header(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    lines.append(f"Dependency graph for {result['root']}")
    if result["feature_filter"]:
        lines.append(f"Feature filter: {result['feature_filter']}")
    lines.append("")
    return lines
