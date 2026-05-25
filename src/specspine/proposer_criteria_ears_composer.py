from __future__ import annotations

from .proposer_criteria_ears_conditional import _make_conditional_criteria
from .proposer_criteria_ears_basic import _make_basic_criteria, _make_fallback_criteria
from .proposer_verbs import _get_action_verb_form

__all__ = [
    "generate_ears_criteria",
]


def generate_ears_criteria(parsed_intent: dict) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    modifiers = parsed_intent["modifiers"]
    components = parsed_intent["components"]
    is_complex = parsed_intent["is_complex"]

    action_base = _get_action_verb_form(action, "base")
    action_gerund = _get_action_verb_form(action, "gerund")
    action_past = _get_action_verb_form(action, "past")

    criteria: list[dict] = []
    counter = 1

    conditional, counter = _make_conditional_criteria(counter, action_base, target, modifiers)
    if conditional:
        criteria.append(conditional)

    basic, counter = _make_basic_criteria(counter, action_base, action_gerund, target)
    criteria.extend(basic)

    if is_complex and len(components) > 1:
        from .proposer_criteria_ears_patterns import BEHAVIOR_PATTERNS
        for component in components[1:3]:
            criteria.append(
                {
                    "id": f"AC{counter:03d}",
                    "text": BEHAVIOR_PATTERNS["simple"].format(
                        behavior=f"support {component} as part of the overall feature",
                    ),
                    "pattern": "simple",
                }
            )
            counter += 1

    if len(criteria) < 3:
        fallback = _make_fallback_criteria(counter, action_gerund, target, 3 - len(criteria))
        criteria.extend(fallback)

    return criteria[:8]
