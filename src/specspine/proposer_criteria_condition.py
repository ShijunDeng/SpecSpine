from __future__ import annotations

__all__ = [
    "_make_meaningful_condition",
]


def _make_meaningful_condition(phrase: str, prep: str) -> str:
    """Transform a noun phrase into a more meaningful condition based on the preposition."""
    condition_templates = {
        "for": [
            "multi-tenant", "all users", "admin users", "guest users",
            "external users", "internal users", "premium users", "free users",
        ],
        "when": [
            "payment fails", "error occurs", "timeout", "connection lost",
            "user logs in", "user logs out", "data changes", "status updates",
        ],
        "if": [
            "user is authenticated", "user has permission", "data is valid",
            "feature is enabled", "service is available",
        ],
        "with": [
            "analytics", "persistence", "real-time updates", "caching",
            "logging enabled", "error handling", "retry logic",
        ],
        "without": [
            "interrupting the user", "data loss", "downtime",
        ],
        "during": [
            "peak hours", "maintenance window", "migration",
        ],
        "after": [
            "user confirmation", "validation passes", "approval",
        ],
        "before": [
            "deployment", "release", "user action",
        ],
    }
    phrase_lower = phrase.lower()
    for template in condition_templates.get(prep, []):
        if template in phrase_lower:
            if prep == "for":
                return f"the feature is needed {prep} {phrase}"
            elif prep == "when":
                return f"{phrase}"
            elif prep == "if":
                return f"{phrase}"
            elif prep == "with":
                return f"{prep} {phrase} enabled"
            else:
                return f"{prep} {phrase}"
    if len(phrase.split()) <= 2:
        return f"the requirement {prep} {phrase} applies"
    return f"{prep} {phrase}"
