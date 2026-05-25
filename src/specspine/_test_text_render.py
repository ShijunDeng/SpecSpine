from __future__ import annotations

from .feature_bundle import FeatureTestsReport
from .feature_trace import _render_trace_checklist_item

__all__ = [
    "render_feature_tests_text",
]


def render_feature_tests_text(report: FeatureTestsReport) -> str:
    summary = report.summary
    lines = [
        f"Feature test packet: {report.feature_id}",
        f"Feature: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Metadata: "
            f"priority={report.metadata.priority} "
            f"owner={report.metadata.owner} "
            f"milestone={report.metadata.milestone} "
            f"target_release={report.metadata.target_release}"
        ),
        "Sources:",
    ]
    if report.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in report.source_files)
    if report.missing_files:
        lines.extend(
            f"- [missing] {relative_path}"
            for relative_path in report.missing_files
        )
    if not report.source_files and not report.missing_files:
        lines.append("- None.")

    lines.extend(
        [
            (
                "Summary: "
                f"acceptance_criteria={summary['acceptance_criteria']['total']} "
                f"test_cases={summary['test_cases']['total']} "
                f"test_coverage={summary['test_coverage']['total']} "
                f"test_plan={summary['test_plan']['total']} "
                f"quality_checks={summary['quality_checks']['total']} "
                f"gaps={summary['gaps']['total']} "
                f"blocking={summary['blocking_checks']['total']}"
            ),
            "",
            "Test Cases:",
        ]
    )
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

    lines.extend(["", "Test Coverage:"])
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

    lines.extend(["", "Existing Test Plan:"])
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Quality Checks:"])
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Gaps:"])
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking Checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key Commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
