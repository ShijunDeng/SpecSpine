from __future__ import annotations

__all__ = [
    "InvalidProposalIntent",
]


class InvalidProposalIntent(ValueError):
    """Raised when natural-language proposal text is empty or not meaningful."""
