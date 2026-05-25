from __future__ import annotations

from .proposer_criteria import generate_ears_criteria

__all__ = [
    "_generate_constraints",
    "_generate_dependencies",
    "_generate_edge_cases",
    "_generate_open_questions",
    "_generate_scope",
    "_generate_test_plan",
    "_generate_traceability_notes",
    "_generate_why",
]


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


def _generate_traceability_notes(slug: str, criteria: list[dict]) -> str:
    lines = [
        f"- Each acceptance criterion (AC001-AC{len(criteria):03d}) maps to one or more implementation tasks",
        f"- Test coverage links in quality/features/{slug}.md prove criterion coverage",
        "- Use `specspine feature trace` to verify end-to-end traceability",
    ]
    for idx, criterion in enumerate(criteria[:3]):
        lines.append(f"- {criterion['id']} -> T00{idx + 2}: core logic implementation")
    return "\n".join(lines)


def _generate_dependencies(parsed: dict) -> str:
    target = parsed["target"]
    lines = [
        f"- Existing {target} infrastructure and configuration",
        "- System-level feature flags or toggle mechanisms",
        "- Test framework and CI/CD pipeline access",
    ]
    if parsed["is_complex"]:
        lines.append(f"- Coordination across components: {', '.join(parsed['components'][1:])}")
    return "\n".join(lines)


def _generate_open_questions(parsed: dict) -> str:
    target = parsed["target"]
    return "\n".join([
        f"- What is the expected scope of {target} in production environments?",
        f"- Are there any existing {target} implementations to integrate with?",
        "- What are the performance requirements for this feature?",
        "- Should this be behind a feature flag for gradual rollout?",
    ])


def _generate_test_plan(parsed: dict, criteria: list[dict]) -> str:
    lines = [
        "- Unit tests for each acceptance criterion behavior",
        "- Integration tests for CLI wiring and end-to-end flows",
        "- Edge case tests for error handling and boundary conditions",
    ]
    for criterion in criteria[:3]:
        lines.append(f"- Test for {criterion['id']}: verify {criterion['text'].replace('The system SHALL ', '')}")
    return "\n".join(lines)
