from __future__ import annotations

from ..feature_bundle import FeatureTestsReport

__all__ = [
    "render_test_cases_lines",
    "render_test_coverage_lines",
]


def render_test_cases_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Test Cases:"]
    if report.test_cases:
        for test_case in report.test_cases:
            linked_targets = (
                ", ".join(link.target for link in test_case.coverage if link.target)
                or "None linked"
            )
            lines.append(
                f"- [ ] {test_case.id} -> "
                f"{test_case.acceptance_criterion_id} "
                f"[{test_case.status}; links={linked_targets}] "
                f"{test_case.source_file}:{test_case.line} "
                f"{test_case.behavior}"
            )
    else:
        lines.append(
            "- [ ] Add acceptance criteria checklist items before testing behavior."
        )
    return lines


def render_test_coverage_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Test Coverage:"]
    if report.test_coverage:
        for link in report.test_coverage:
            marker = "x" if link.done else " "
            exists = "exists" if link.target_exists else "missing"
            target = link.target or "None linked"
            lines.append(
                f"- [{marker}] {link.id} -> "
                f"{link.acceptance_criterion_id} {target} "
                f"({exists}) {link.source_file}:{link.line}"
            )
    else:
        lines.append("- None linked.")
    return lines
