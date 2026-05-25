from __future__ import annotations

from ..workspace import normalize_template
from ..proposer_build_sections import _generate_why, _generate_test_plan
from ._quality_builders_checks import _build_quality_check_lines, _build_test_coverage_lines

__all__ = [
    "build_quality_content",
]


def build_quality_content(
    resolved_slug: str,
    title: str,
    parsed: dict,
    criteria: list[dict],
    quality_checks: list[str],
    intent: str,
) -> str:
    why_text = _generate_why(parsed, intent)

    quality_check_lines = _build_quality_check_lines(quality_checks)
    test_coverage_lines = _build_test_coverage_lines(resolved_slug, criteria)
    test_plan_lines = _generate_test_plan(parsed, criteria)

    return normalize_template(f"""
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
