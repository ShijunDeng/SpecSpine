from __future__ import annotations

from .feature_bundle import FEATURE_TRANSITIONS, _transition_payload

__all__ = [
    "_allowed_transitions",
    "_replace_or_insert_status_line",
]


def _allowed_transitions(from_status: str) -> tuple[str, ...]:
    return FEATURE_TRANSITIONS.get(from_status, ())


def _replace_or_insert_status_line(content: str, status: str) -> str:
    lines = content.splitlines(keepends=True)
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "status":
            newline = "\n" if raw_line.endswith("\n") else ""
            lines[index] = f"Status: {status}{newline}"
            return "".join(lines)

    insert_at = 0
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "feature id":
            insert_at = index + 1
            break

    lines.insert(insert_at, f"Status: {status}\n")
    return "".join(lines)
