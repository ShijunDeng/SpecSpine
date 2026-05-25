from __future__ import annotations

__all__ = [
    "EARS_PATTERNS",
    "BEHAVIOR_PATTERNS",
]

EARS_PATTERNS = (
    "event-driven",
    "conditional",
    "simple",
    "ubiquitous",
)

BEHAVIOR_PATTERNS = {
    "event-driven": "The system SHALL {behavior} when {condition}",
    "conditional": "The system SHALL {behavior} if {precondition}",
    "simple": "The system SHALL {behavior}",
    "ubiquitous": "The system SHALL {behavior} where {context}",
}
