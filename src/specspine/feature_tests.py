from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FeatureAcceptanceTestCase,
    FeatureHandoffReport,
    FeatureReadyCheck,
    FeatureTestCoverageLink,
    FeatureTestsReport,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
    _relative_feature_paths,
    feature_bundle_paths,
    parse_test_coverage,
    validate_feature_slug,
)
from .feature_handoff import build_feature_handoff_report
from .feature_trace import _render_trace_checklist_item

__all__ = [
    "FeatureTestsReport",
    "build_feature_tests_report",
    "render_feature_tests_text",
    "render_feature_tests_json",
]


def _recommended_test_packet_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature tests {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _acceptance_test_cases(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    test_coverage: tuple[FeatureTestCoverageLink, ...],
) -> tuple[FeatureAcceptanceTestCase, ...]:
    test_cases: list[FeatureAcceptanceTestCase] = []
    for index, criterion in enumerate(acceptance_criteria, start=1):
        coverage = tuple(
            link
            for link in test_coverage
            if link.acceptance_criterion_id == criterion.id
        )
        if any(link.done for link in coverage):
            status = "covered"
        elif coverage:
            status = "planned"
        else:
            status = "pending"
        test_cases.append(
            FeatureAcceptanceTestCase(
                id=f"TC{index:03d}",
                acceptance_criterion_id=criterion.id,
                acceptance_criterion_text=criterion.text,
                source_file=criterion.source_file,
                line=criterion.line,
                behavior=f"Pending behavior to test: {criterion.text}",
                coverage=coverage,
                status=status,
            )
        )
    return tuple(test_cases)


def build_feature_tests_report(root: Path, slug: str) -> FeatureTestsReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    handoff = build_feature_handoff_report(resolved_root, slug)
    source_files = tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    if quality_path.exists():
        test_coverage = parse_test_coverage(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
            root=resolved_root,
        )

    return FeatureTestsReport(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        acceptance_criteria=handoff.acceptance_criteria,
        test_plan=handoff.test_plan,
        test_coverage=test_coverage,
        test_cases=_acceptance_test_cases(
            handoff.acceptance_criteria,
            test_coverage,
        ),
        quality_checks=handoff.quality_checks,
        ready_summary=handoff.ready_summary,
        recommended_commands=_recommended_test_packet_commands(slug),
        has_native_files=handoff.has_native_files,
        metadata=handoff.metadata,
    )


def render_feature_tests_json(report: FeatureTestsReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


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
