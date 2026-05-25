from __future__ import annotations

__all__ = [
    "_build_quality_check_lines",
    "_build_test_coverage_lines",
]


def _build_quality_check_lines(quality_checks: list[str]) -> str:
    return "\n".join(
        f"- [ ] QC{i+1:03d}: {check}" for i, check in enumerate(quality_checks)
    )


def _build_test_coverage_lines(resolved_slug: str, criteria: list[dict]) -> str:
    return "\n".join(
        f"- [ ] {c['id']} -> tests/test_{resolved_slug.replace('-', '_')}.py"
        for c in criteria
    )
