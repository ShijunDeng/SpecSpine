from __future__ import annotations


def feature_title(slug: str, title: str | None = None) -> str:
    if title and title.strip():
        return title.strip()
    return slug.replace("-", " ").title()


__all__ = [
    "feature_title",
]
