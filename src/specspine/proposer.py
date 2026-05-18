from __future__ import annotations

import re
from textwrap import dedent

from .workspace import normalize_template


class InvalidProposalIntent(ValueError):
    """Raised when natural-language proposal text is empty or not meaningful."""


MAX_INTENT_CHARS = 5000

ACTION_VERBS = (
    "add",
    "create",
    "implement",
    "build",
    "support",
    "enable",
    "integrate",
    "introduce",
    "develop",
    "design",
    "extend",
    "provide",
    "generate",
    "configure",
    "display",
    "show",
    "hide",
    "remove",
    "delete",
    "update",
    "modify",
    "change",
    "allow",
    "permit",
    "restrict",
    "block",
    "track",
    "monitor",
    "validate",
    "verify",
    "test",
    "document",
    "migrate",
    "convert",
    "import",
    "export",
    "publish",
    "deploy",
    "render",
    "animate",
    "sync",
)

TARGET_NOUNS = (
    "feature",
    "toggle",
    "mode",
    "button",
    "page",
    "panel",
    "dialog",
    "modal",
    "menu",
    "sidebar",
    "header",
    "footer",
    "toolbar",
    "form",
    "input",
    "field",
    "dropdown",
    "select",
    "checkbox",
    "radio",
    "tab",
    "card",
    "list",
    "table",
    "chart",
    "graph",
    "widget",
    "component",
    "module",
    "service",
    "api",
    "endpoint",
    "handler",
    "middleware",
    "plugin",
    "extension",
    "adapter",
    "connector",
    "integration",
    "pipeline",
    "workflow",
    "report",
    "dashboard",
    "notification",
    "alert",
    "toast",
    "banner",
    "badge",
    "tooltip",
    "popover",
    "accordion",
    "carousel",
    "slider",
    "progress",
    "spinner",
    "loader",
    "skeleton",
    "theme",
    "layout",
    "template",
    "style",
    "animation",
    "transition",
    "routing",
    "navigation",
    "search",
    "filter",
    "sort",
    "pagination",
    "validation",
    "authentication",
    "authorization",
    "permission",
    "role",
    "setting",
    "config",
    "preference",
    "profile",
    "account",
    "session",
    "cache",
    "store",
    "database",
    "model",
    "schema",
    "migration",
    "seed",
    "fixture",
    "mock",
    "stub",
    "test",
    "spec",
    "doc",
    "documentation",
    "readme",
    "changelog",
    "version",
    "release",
    "build",
    "deploy",
    "ci",
    "cd",
    "pipeline",
    "hook",
    "trigger",
    "event",
    "listener",
    "subscriber",
    "publisher",
    "broker",
    "queue",
    "stream",
    "log",
    "metric",
    "monitor",
    "health",
    "status",
    "check",
    "gate",
    "policy",
    "rule",
    "constraint",
    "limit",
    "quota",
    "rate",
    "throttle",
    "retry",
    "timeout",
    "circuit",
    "breaker",
    "fallback",
    "default",
)

MODIFIER_PREPOSITIONS = (
    "with",
    "when",
    "if",
    "for",
    "to",
    "where",
    "while",
    "unless",
    "after",
    "before",
    "during",
    "without",
    "by",
    "via",
    "through",
    "on",
    "in",
    "at",
    "from",
    "between",
    "among",
)

COMPONENT_SPLITTERS = re.compile(r"\band\b|\bwith\b|\bplus\b|;")

EARS_PATTERNS = (
    "event-driven",
    "conditional",
    "simple",
    "ubiquitous",
)

BEHAVIOR_PATTERNS = {
    "event-driven": "The system SHALL {behavior} WHEN {condition}",
    "conditional": "The system SHALL {behavior} IF {precondition}",
    "simple": "The system SHALL {behavior}",
    "ubiquitous": "The system SHALL {behavior} WHERE {context}",
}

SLUG_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def _truncation_warning(original_length: int) -> str:
    return (
        f"Proposal intent exceeded {MAX_INTENT_CHARS} characters and was "
        f"truncated from {original_length} characters."
    )


def normalize_intent(intent: str) -> tuple[str, list[str]]:
    normalized = intent.strip()
    if not normalized:
        raise InvalidProposalIntent("Proposal intent must not be empty.")
    if not any(char.isalnum() for char in normalized):
        raise InvalidProposalIntent(
            "Proposal intent must include meaningful words or numbers."
        )
    if len(normalized) > MAX_INTENT_CHARS:
        return normalized[:MAX_INTENT_CHARS], [_truncation_warning(len(normalized))]
    return normalized, []


def validate_intent(intent: str) -> str:
    normalized, _warnings = normalize_intent(intent)
    return normalized


def generate_slug_from_intent(intent: str) -> str:
    normalized = validate_intent(intent)
    tokens = re.findall(r"[a-z0-9]+", normalized.lower())
    filtered = [token for token in tokens if token not in SLUG_STOP_WORDS]
    selected = filtered[:5] or tokens[:5] or ["proposal"]
    slug = "-".join(selected)

    if not slug[0].isalnum():
        slug = f"proposal-{slug}"
    if not slug[-1].isalnum():
        slug = f"{slug}-proposal"

    from .features import validate_feature_slug

    return validate_feature_slug(slug)


def parse_intent(intent: str) -> dict:
    text = validate_intent(intent).lower()

    raw_components = COMPONENT_SPLITTERS.split(text)
    components = [c.strip() for c in raw_components if c.strip()]
    is_complex = len(components) > 1

    if is_complex:
        primary = components[0]
    else:
        primary = text

    action = _extract_action(primary)
    target = _extract_target(primary)
    modifiers = _extract_modifiers(primary)

    return {
        "action": action,
        "target": target,
        "modifiers": modifiers,
        "components": components,
        "is_complex": is_complex,
    }


def _extract_action(text: str) -> str:
    words = text.split()
    for word in words:
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in ACTION_VERBS:
            return cleaned
    return "implement"


def _extract_target(text: str) -> str:
    words = text.split()
    found_nouns = []
    for i, word in enumerate(words):
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in TARGET_NOUNS:
            if i > 0:
                prev = words[i - 1].strip(".,;:!?()[]{}'\"")
                if prev in MODIFIER_PREPOSITIONS:
                    if found_nouns:
                        pass
                    found_nouns.append(cleaned)
                else:
                    found_nouns.append(cleaned)
            else:
                found_nouns.append(cleaned)
    if found_nouns:
        return found_nouns[-1]
    return "feature"


def _extract_modifiers(text: str) -> list:
    modifiers = []
    words = text.split()
    for i, word in enumerate(words):
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in MODIFIER_PREPOSITIONS:
            rest = " ".join(words[i:])
            for end_prep in MODIFIER_PREPOSITIONS:
                idx = rest.find(f" {end_prep} ")
                if idx > len(cleaned):
                    rest = rest[:idx]
                    break
            modifier = rest.strip().rstrip(".")
            if modifier and modifier not in modifiers:
                modifiers.append(modifier)
    return modifiers


def _normalize_modifier(modifier: str) -> str:
    result = modifier
    for prep in MODIFIER_PREPOSITIONS:
        if result.startswith(prep + " "):
            result = result[len(prep):].strip()
            break
    if not result:
        return "the necessary conditions are met"
    return result


def generate_ears_criteria(parsed_intent: dict) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    modifiers = parsed_intent["modifiers"]
    components = parsed_intent["components"]
    is_complex = parsed_intent["is_complex"]

    criteria: list[dict] = []
    counter = 1

    if modifiers:
        first_mod = modifiers[0]
        criteria.append(
            {
                "id": f"AC{counter:03d}",
                "text": BEHAVIOR_PATTERNS["conditional"].format(
                    behavior=f"allow users to {action} the {target}",
                    precondition=_normalize_modifier(first_mod),
                ),
                "pattern": "conditional",
            }
        )
        counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["event-driven"].format(
                behavior=f"{action} the {target} successfully",
                condition=f"the user initiates a request to {action} the {target}",
            ),
            "pattern": "event-driven",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["simple"].format(
                behavior=f"provide the {target} with {action} capability",
            ),
            "pattern": "simple",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["ubiquitous"].format(
                behavior=f"ensure the {target} behaves consistently during {action} operations",
                context=f"the {target} is in active use",
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
                        behavior=f"handle edge cases related to {action}ing the {target}",
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


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def build_proposal_content(
    slug: str,
    intent: str,
    *,
    priority: str = "medium",
    owner: str = "unassigned",
    milestone: str = "unassigned",
    target_release: str = "unassigned",
    project: str = "unassigned",
    effort: str = "unknown",
) -> dict[str, str]:
    from .features import FEATURE_FILE_PATHS

    intent = validate_intent(intent)
    resolved_slug = slug
    title = _slug_to_title(resolved_slug)
    parsed = parse_intent(intent)
    criteria = generate_ears_criteria(parsed)
    tasks = generate_tasks(parsed, criteria)
    quality_checks = generate_quality_checks(criteria)

    ac_lines = "\n".join(f"- [ ] {c['id']} {c['text']}" for c in criteria)
    edge_case_lines = _generate_edge_cases(parsed)
    constraint_lines = _generate_constraints(parsed)
    traceability_lines = _generate_traceability_notes(resolved_slug, criteria)

    task_lines = "\n".join(
        f"- [ ] {t['id']}: {t['text']}\n  _Boundary: {t['boundary']}\n  _Depends: {t['depends']}"
        for t in tasks
    )
    dependency_lines = _generate_dependencies(parsed)
    open_questions_lines = _generate_open_questions(parsed)

    quality_check_lines = "\n".join(
        f"- [ ] QC{i+1:03d}: {check}" for i, check in enumerate(quality_checks)
    )
    test_coverage_lines = "\n".join(
        f"- [ ] {c['id']} -> tests/test_{resolved_slug.replace('-', '_')}.py"
        for c in criteria
    )
    test_plan_lines = _generate_test_plan(parsed, criteria)

    why_text = _generate_why(parsed, intent)

    spec_content = normalize_template(f"""
# {title}

Feature ID: {resolved_slug}
Status: proposed
Priority: {priority}
Owner: {owner}
Milestone: {milestone}
Target Release: {target_release}
Project: {project}
Effort: {effort}

## Why

{why_text}

## Users

- End users who need to {parsed['action']} the {parsed['target']}
- Developers maintaining the {parsed['target']} functionality
- Operators configuring the {parsed['target']} in production

## Scope

- {_generate_scope(parsed)}
- Support for {parsed['action']}ing the {parsed['target']} in all relevant contexts
- Integration with existing system components

## Non-Goals

- This feature will not modify unrelated system behavior
- Migration of existing data is out of scope unless explicitly required
- Third-party integrations beyond core functionality

## Acceptance Criteria

{ac_lines}

## Edge Cases

{edge_case_lines}

## Constraints

{constraint_lines}

## Traceability Notes

{traceability_lines}
""")

    execution_content = normalize_template(f"""
# {title} Execution

Feature ID: {resolved_slug}
Status: proposed
Why: {why_text}

## Milestones

- M1: Module scaffolding and file structure in place
- M2: Core {parsed['action']} logic implemented for all acceptance criteria
- M3: CLI integration and validation complete
- M4: Tests written and passing, documentation updated

## Tasks

{task_lines}

## Dependencies

{dependency_lines}

## Open Questions

{open_questions_lines}

## Agent Handoff

- Run `specspine feature handoff {resolved_slug} . --json` before implementation or review handoff.
- Run `specspine adapters handoff {resolved_slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks {resolved_slug} . --json` for the focused implementation checklist.
- Run `specspine feature task-issues {resolved_slug} . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace {resolved_slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests {resolved_slug} . --json` to build the acceptance-test packet.
- Run `specspine feature ready {resolved_slug} . --json` after implementation evidence is complete.
- Run `specspine feature pr {resolved_slug} . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan {resolved_slug} . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan {resolved_slug} . --output-dir .specspine/sync-plan/{resolved_slug}` to materialize local sync review artifacts.
- Run `specspine validate . --fusion --features` before handoff or release.
""")

    quality_content = normalize_template(f"""
# {title} Quality

Feature ID: {resolved_slug}
Status: proposed
Why: {why_text}

## Required Checks

{quality_check_lines}

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

{test_coverage_lines}

## Test Plan

{test_plan_lines}

## Review Notes

- Review each acceptance criterion against implementation evidence.
- Verify edge case handling matches the spec.
- Confirm test coverage links are valid and targets exist.

## Release Readiness

- [ ] RR001: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [ ] RR002: Docs, release notes, or `specspine feature pr {resolved_slug} . --json` output are ready for reviewers.
- [ ] RR003: `specspine feature sync-plan {resolved_slug} . --json` or `--output-dir .specspine/sync-plan/{resolved_slug}` has been reviewed before any remote GitHub sync.
- [ ] RR004: `specspine feature ready {resolved_slug} . --json` and `specspine validate . --fusion --features` have been run.
- [ ] RR005: No known blockers remain, or blockers are documented in review notes.
""")

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=resolved_slug): spec_content,
        FEATURE_FILE_PATHS["execution"].format(slug=resolved_slug): execution_content,
        FEATURE_FILE_PATHS["quality"].format(slug=resolved_slug): quality_content,
    }


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
