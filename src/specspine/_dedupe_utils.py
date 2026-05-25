from __future__ import annotations

from .consistency_models import ConsistencyReference

__all__ = [
    "_dedupe",
    "_dedupe_references",
]


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return tuple(deduped)


def _dedupe_references(
    references: list[ConsistencyReference],
) -> tuple[ConsistencyReference, ...]:
    seen: set[tuple[str, int | None, str, str]] = set()
    deduped: list[ConsistencyReference] = []
    for reference in references:
        key = (reference.path, reference.line, reference.kind, reference.matched)
        if key in seen:
            continue
        deduped.append(reference)
        seen.add(key)
    return tuple(sorted(deduped, key=lambda item: (item.path, item.line or 0, item.kind)))
