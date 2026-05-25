from __future__ import annotations

from .proposer_criteria_ears_patterns import BEHAVIOR_PATTERNS

__all__ = [
    "_make_fallback_criteria",
]


def _make_fallback_criteria(
    counter: int,
    action_gerund: str,
    target: str,
    count: int = 1,
) -> list[dict]:
    criteria: list[dict] = []
    for _ in range(count):
        criteria.append(
            {
                "id": f"AC{counter:03d}",
                "text": BEHAVIOR_PATTERNS["simple"].format(
                    behavior=f"handle edge cases related to {action_gerund} the {target}",
                ),
                "pattern": "simple",
            }
        )
        counter += 1
    return criteria
