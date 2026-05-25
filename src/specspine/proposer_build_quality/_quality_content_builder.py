from __future__ import annotations

from ..workspace import normalize_template
from ..proposer_build_sections import _generate_why, _generate_test_plan
from ._quality_builders_checks import _build_quality_check_lines, _build_test_coverage_lines
from ._quality_release_readiness import RELEASE_READINESS_TEMPLATE

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
    release_readiness = RELEASE_READINESS_TEMPLATE.format(slug=resolved_slug)

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

{release_readiness}
""")
