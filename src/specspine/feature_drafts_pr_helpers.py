from __future__ import annotations

__all__ = [
    "_recommended_pr_commands",
    "_pull_request_title",
]


def _recommended_pr_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature pr {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _pull_request_title(base_title: str) -> str:
    title = base_title.strip() or "Feature"
    if title.lower().startswith("implement "):
        return title
    return f"Implement {title}"
