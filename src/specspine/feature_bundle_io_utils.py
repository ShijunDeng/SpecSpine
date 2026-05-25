from __future__ import annotations

__all__ = [
    "_transition_payload",
    "_trace_gap",
]


def _transition_payload(
    *,
    from_status: str | None,
    to_status: str,
    enforced: bool,
    allowed: bool,
    reason: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "allowed": allowed,
        "enforced": enforced,
        "from": from_status,
        "to": to_status,
    }
    if reason:
        payload["reason"] = reason
    return payload


def _trace_gap(gap_id: str, source_file: str, message: str) -> dict[str, str]:
    return {
        "id": gap_id,
        "message": message,
        "source_file": source_file,
    }
