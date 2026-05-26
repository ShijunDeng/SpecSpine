from __future__ import annotations

__all__ = [
    "_content_scalar",
    "_content_has_scalar",
    "_content_has_feature_id",
]


def _content_scalar(content: str, key: str) -> str | None:
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, current_value = stripped.split(":", 1)
        if current_key.strip().lower() != key.lower():
            continue
        value = current_value.strip()
        if value:
            return value

    return None


def _content_has_scalar(content: str, key: str, expected_value: str) -> bool:
    value = _content_scalar(content, key)
    return bool(value and value.lower() == expected_value.lower())


def _content_has_feature_id(content: str, slug: str) -> bool:
    return _content_has_scalar(content, "Feature ID", slug) or _content_has_scalar(
        content,
        "feature",
        slug,
    )
