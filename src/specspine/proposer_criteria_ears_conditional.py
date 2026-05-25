from __future__ import annotations

from .proposer_criteria_ears_patterns import BEHAVIOR_PATTERNS

__all__ = [
    "_make_conditional_criteria",
]


def _make_conditional_criteria(
    counter: int,
    action_base: str,
    target: str,
    modifiers: list[str],
) -> tuple[dict, int]:
    if not modifiers:
        return {}, counter

    from .proposer_intent import _normalize_modifier

    first_mod = modifiers[0]
    normalized_mod = _normalize_modifier(first_mod)
    return (
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["conditional"].format(
                behavior=f"allow users to {action_base} the {target}",
                precondition=normalized_mod,
            ),
            "pattern": "conditional",
        },
        counter + 1,
    )
