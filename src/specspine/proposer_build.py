from __future__ import annotations

from .workspace import normalize_template
from .proposer_intent import validate_intent, parse_intent
from .proposer_slug import _slug_to_title
from .proposer_criteria import generate_ears_criteria, generate_tasks, generate_quality_checks

__all__ = [
    "build_proposal_content",
    "_generate_why",
    "_generate_scope",
    "_generate_edge_cases",
    "_generate_constraints",
    "_generate_traceability_notes",
    "_generate_dependencies",
    "_generate_open_questions",
    "_generate_test_plan",
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
    open_questions_line = _generate_open_questions(parsed)

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

{open_questions_line}

## Agent Handoff

- Run `specspine feature handoff {resolved_slug} . --json` before implementation or review handoff.
- Run `specspine adapters handoff {resolved_slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks {resolved_slug} . --json` for the focused implementation checklist.
- Run `specspine feature task-issues {resolved_slug} . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace {resolved_slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests {resolved_slug} . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature {resolved_slug} --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature {resolved_slug} --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature {resolved_slug} --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix {resolved_slug} . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature {resolved_slug} --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature {resolved_slug} --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature {resolved_slug} --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature {resolved_slug} --json` to compose local pre-merge review evidence.
- Run `specspine feature ready {resolved_slug} . --json` after implementation evidence is complete.
- Run `specspine feature pr {resolved_slug} . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan {resolved_slug} . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan {resolved_slug} . --output-dir .specspine/sync-plan/{resolved_slug}` to materialize local sync review artifacts.
- Run `specspine feature archive {resolved_slug} . --json` to package local archive evidence before lifecycle closure.
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
- [ ] RR003: `specspine tests impact . --feature {resolved_slug} --json` has been reviewed for focused local test commands.
- [ ] RR004: `specspine consistency scan . --feature {resolved_slug} --json` has been reviewed for local spec-code-test-doc drift.
- [ ] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [ ] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [ ] RR007: `specspine coverage plan . --feature {resolved_slug} --json` has been reviewed if missing AC coverage remains.
- [ ] RR008: `specspine verify matrix {resolved_slug} . --json` has been reviewed for AC-level verification evidence.
- [ ] RR009: `specspine change risk . --feature {resolved_slug} --json` has been reviewed for changed-path risk evidence.
- [ ] RR010: `specspine security cues . --feature {resolved_slug} --json` has been reviewed for security-sensitive cues.
- [ ] RR011: `specspine provenance manifest . --feature {resolved_slug} --json` has been reviewed for local evidence hashes.
- [ ] RR012: `specspine review packet . --feature {resolved_slug} --json` has been reviewed for local pre-merge evidence.
- [ ] RR013: `specspine feature sync-plan {resolved_slug} . --json` or `--output-dir .specspine/sync-plan/{resolved_slug}` has been reviewed before any remote GitHub sync.
- [ ] RR014: `specspine feature archive {resolved_slug} . --json` has been reviewed before marking status archived.
- [ ] RR015: `specspine feature ready {resolved_slug} . --json` and `specspine validate . --fusion --features` have been run.
- [ ] RR016: No known blockers remain, or blockers are documented in review notes.
""")

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=resolved_slug): spec_content,
        FEATURE_FILE_PATHS["execution"].format(slug=resolved_slug): execution_content,
        FEATURE_FILE_PATHS["quality"].format(slug=resolved_slug): quality_content,
    }
