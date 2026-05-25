from __future__ import annotations


def _generate_why(parsed: dict, intent: str) -> str:
    action = parsed["action"]
    target = parsed["target"]
    return (
        f"This feature enables users to {action} the {target}, "
        f"improving the overall system usability and functionality. "
        f"The intent is: {intent}"
    )


def _generate_scope(parsed: dict) -> str:
    action = parsed["action"]
    target = parsed["target"]
    return f"Implement the ability to {action} the {target} with proper validation and error handling"


def _generate_edge_cases(parsed: dict) -> str:
    action = parsed["action"]
    target = parsed["target"]
    lines = [
        f"- Behavior when {action}ing the {target} fails due to missing prerequisites",
        f"- Handling of concurrent {action} requests for the same {target}",
        f"- Recovery from partial failures during {action} operations",
        f"- Validation of {target} state before and after {action}",
    ]
    if parsed["modifiers"]:
        lines.append(
            f"- Edge cases specific to the constraint: {parsed['modifiers'][0]}"
        )
    return "\n".join(lines)


def _generate_constraints(parsed: dict) -> str:
    target = parsed["target"]
    return "\n".join([
        f"- The {target} must maintain backward compatibility with existing configurations",
        "- Performance impact must be negligible under normal load",
        "- All changes must be auditable and reversible",
    ])


__all__ = [
    "_generate_constraints",
    "_generate_edge_cases",
    "_generate_scope",
    "_generate_why",
]
