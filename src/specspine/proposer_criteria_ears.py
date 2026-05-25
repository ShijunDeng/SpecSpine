from __future__ import annotations

from .proposer_intent import _normalize_modifier
from .proposer_verbs import _get_action_verb_form
from .proposer_criteria_condition import _make_meaningful_condition

__all__ = [
    "EARS_PATTERNS",
    "BEHAVIOR_PATTERNS",
    "generate_ears_criteria",
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

    if modifiers:
        first_mod = modifiers[0]
        normalized_mod = _normalize_modifier(first_mod)
        criteria.append(
            {
                "id": f"AC{counter:03d}",
                "text": BEHAVIOR_PATTERNS["conditional"].format(
                    behavior=f"allow users to {action_base} the {target}",
                    precondition=normalized_mod,
                ),
                "pattern": "conditional",
            }
        )
        counter += 1

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

    if is_complex and len(components) > 1:
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
        while len(criteria) < 3:
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

    return criteria[:8]
