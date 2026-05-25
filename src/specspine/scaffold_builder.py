from __future__ import annotations

import json
from pathlib import Path

from .features import (
    build_feature_trace_report,
    validate_feature_slug,
)
from .scaffold_generator import (
    _existing_coverage_links,
    _generate_test_class,
    _generate_test_method,
    _slug_to_camel,
)
from .scaffold_models import (
    ScaffoldCoverageLink,
    ScaffoldRemediationStep,
    ScaffoldReport,
    ScaffoldSkippedCriterion,
    ScaffoldTestMethod,
)

__all__ = [
    "_build_remediation_plan",
    "build_ac_test_scaffold",
    "render_scaffold_json",
    "render_scaffold_text",
]


def _build_remediation_plan(
    slug: str,
    uncovered_acs: list[dict[str, str]],
    test_path: str,
    class_name: str,
) -> list[ScaffoldRemediationStep]:
    steps: list[ScaffoldRemediationStep] = []
    for ac in uncovered_acs:
        method_info = _generate_test_method(ac["ac_id"], ac["ac_text"], slug)
        steps.append(
            ScaffoldRemediationStep(
                ac_id=ac["ac_id"],
                action=f"Implement {method_info['method_name']} in {test_path}",
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
    return steps


def build_ac_test_scaffold(root: Path, slug: str) -> ScaffoldReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    trace_report = build_feature_trace_report(resolved_root, slug)
    acceptance_criteria = trace_report.acceptance_criteria
    status = trace_report.status
    covered_acs = _existing_coverage_links(resolved_root, slug)
    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    test_filename = f"test_{slug.replace('-', '_')}_scaffold.py"
    test_path = f"tests/{test_filename}"

    methods: list[dict[str, str]] = []
    coverage_links: list[ScaffoldCoverageLink] = []
    skipped_criteria: list[ScaffoldSkippedCriterion] = []
    uncovered_acs: list[dict[str, str]] = []

    for criterion in acceptance_criteria:
        if criterion.id in covered_acs:
            skipped_criteria.append(
                ScaffoldSkippedCriterion(
                    ac_id=criterion.id,
                    reason="Already has completed test coverage link",
                )
            )
            continue
        method_info = _generate_test_method(criterion.id, criterion.text, slug)
        methods.append(method_info)
        coverage_links.append(
            ScaffoldCoverageLink(
                ac_id=criterion.id,
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
        uncovered_acs.append({"ac_id": criterion.id, "ac_text": criterion.text})

    scaffold_source = _generate_test_class(slug, methods)
    remediation = _build_remediation_plan(slug, uncovered_acs, test_path, class_name)

    safety_notes: tuple[str, ...] = (
        "Scaffold generation is read-only; no subprocess or network calls made.",
        "Generated test methods contain self.fail() placeholders only.",
        "Review and implement each test method before running the scaffold file.",
    )

    return ScaffoldReport(
        feature_id=slug,
        status=status,
        scaffold_file=test_path,
        test_methods=tuple(
            ScaffoldTestMethod(
                method_name=m["method_name"],
                docstring=m["docstring"],
                ac_id=uncovered_acs[i]["ac_id"],
                ac_text=uncovered_acs[i]["ac_text"],
                body=m["body"],
            )
            for i, m in enumerate(methods)
        ),
        coverage_links=tuple(coverage_links),
        skipped_criteria=tuple(skipped_criteria),
        remediation_plan=tuple(remediation),
        safety_notes=safety_notes,
    )


def render_scaffold_json(result: ScaffoldReport) -> str:
    return json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"


def render_scaffold_text(result: ScaffoldReport) -> str:
    lines = [
        f"Scaffold: {result.feature_id}",
        f"Status: {result.status}",
        f"Target: {result.scaffold_file}",
        "",
        f"Test methods: {len(result.test_methods)}",
        f"Coverage links: {len(result.coverage_links)}",
        f"Skipped: {len(result.skipped_criteria)}",
        "",
    ]
    if result.test_methods:
        lines.append("Methods:")
        for method in result.test_methods:
            lines.append(f"  - {method.method_name}: {method.docstring}")
        lines.append("")
    if result.skipped_criteria:
        lines.append("Skipped (already covered):")
        for item in result.skipped_criteria:
            lines.append(f"  - {item.ac_id}: {item.reason}")
        lines.append("")
    if result.remediation_plan:
        lines.append("Remediation:")
        for step in result.remediation_plan:
            lines.append(f"  - {step.ac_id}: {step.action}")
        lines.append("")
    lines.extend(f"Note: {note}" for note in result.safety_notes)
    return "\n".join(lines) + "\n"
