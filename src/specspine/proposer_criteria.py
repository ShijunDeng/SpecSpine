from __future__ import annotations

from .proposer_intent import _normalize_modifier
from .proposer_verbs import _get_action_verb_form

__all__ = [
    "EARS_PATTERNS",
    "BEHAVIOR_PATTERNS",
    "generate_ears_criteria",
    "generate_tasks",
    "generate_quality_checks",
    "_make_meaningful_condition",
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


def generate_tasks(parsed_intent: dict, criteria: list[dict]) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    tasks: list[dict] = []

    tasks.append(
        {
            "id": "T001",
            "text": f"Set up file structure and module scaffolding for {action} {target}",
            "boundary": f"Project structure and module creation for {target}",
            "depends": "none",
        }
    )

    for criterion in criteria[:3]:
        criterion_text = criterion["text"].replace("The system SHALL ", "")
        tasks.append(
            {
                "id": f"T{len(tasks) + 1:03d}",
                "text": f"Implement core logic: {criterion_text}",
                "boundary": f"Core behavior for {criterion['pattern']} criterion {criterion['id']}",
                "depends": "T001",
            }
        )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Wire CLI interface and validate {action} {target} integration",
            "boundary": f"CLI integration and validation for {target}",
            "depends": ", ".join(t["id"] for t in tasks[1:]),
        }
    )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Add unit tests, integration tests, and documentation for {action} {target}",
            "boundary": f"Test suite and documentation for {target}",
            "depends": tasks[-1]["id"],
        }
    )

    return tasks


def generate_quality_checks(criteria: list[dict]) -> list[str]:
    checks: list[str] = []
    for criterion in criteria:
        checks.append(
            f"Verify {criterion['id']}: {criterion['text']}"
        )
    return checks
