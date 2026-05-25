from __future__ import annotations

from typing import Any


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _dedupe_strings(values: object) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()

    deduped: list[str] = []
    for value in values:
        normalized = str(value).strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


__all__ = [
    "_clean_scalar",
    "_dedupe_strings",
]
