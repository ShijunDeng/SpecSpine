from __future__ import annotations

from .proposer_criteria_ears_patterns import BEHAVIOR_PATTERNS

__all__ = [
    "_make_basic_criteria",
    "_make_fallback_criteria",
]


def _make_basic_criteria(
    counter: int,
    action_base: str,
    action_gerund: str,
    target: str,
) -> tuple[list[dict], int]:
    criteria: list[dict] = []

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["event-driven"].format(
                behavior=f"allow the user to {action_base} the {target}",
                condition=f"the user requests to {action_base} the {target}",
            ),
            "pattern": "event-driven",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["simple"].format(
                behavior=f"validate all inputs before {action_gerund} the {target}",
            ),
            "pattern": "simple",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["ubiquitous"].format(
                behavior=f"handle errors gracefully when {action_gerund} fails",
                context=f"any error occurs during the operation",
            ),
            "pattern": "ubiquitous",
        }
    )
    counter += 1

    return criteria, counter


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
