from __future__ import annotations

from .proposer_intent_constants import InvalidProposalIntent, MAX_INTENT_CHARS


def _truncation_warning(original_length: int) -> str:
    return (
        f"Proposal intent exceeded {MAX_INTENT_CHARS} characters and was "
        f"truncated from {original_length} characters."
    )


def normalize_intent(intent: str) -> tuple[str, list[str]]:
    normalized = intent.strip()
    if not normalized:
        raise InvalidProposalIntent("Proposal intent must not be empty.")
    if not any(char.isalnum() for char in normalized):
        raise InvalidProposalIntent(
            "Proposal intent must include meaningful words or numbers."
        )
    if len(normalized) > MAX_INTENT_CHARS:
        return normalized[:MAX_INTENT_CHARS], [_truncation_warning(len(normalized))]
    return normalized, []


def validate_intent(intent: str) -> str:
    normalized, _warnings = normalize_intent(intent)
    return normalized


__all__ = [
    "_truncation_warning",
    "normalize_intent",
    "validate_intent",
]
