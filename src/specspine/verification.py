from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
    feature_bundle_paths,
    validate_feature_slug,
)


@dataclass(frozen=True)
class VerificationMatrix:
    root: Path
    feature_id: str
    status: str
    ready: bool
    matrix: tuple[dict[str, Any], ...]
    evidence: dict[str, Any]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence": dict(self.evidence),
            "feature_id": self.feature_id,
            "matrix": [dict(row) for row in self.matrix],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "status": self.status,
            "summary": dict(self.summary),
        }


def _checklist_summary(items: tuple[Any, ...]) -> dict[str, int]:
    done = sum(1 for item in items if bool(item.done))
    total = len(items)
    return {
        "done": done,
        "open": total - done,
        "total": total,
    }


def _empty_evidence(root: Path, slug: str) -> dict[str, Any]:
    missing = [
        str(path.relative_to(root))
        for path in feature_bundle_paths(root, slug).values()
    ]
    return {
        "blocking_checks": [],
        "gaps": [
            {
                "id": "missing_file",
                "message": f"Missing native feature file: {relative_path}",
                "source_file": relative_path,
            }
            for relative_path in missing
        ],
        "has_native_files": False,
        "missing_files": missing,
        "quality_checks": [],
        "ready_summary": {"fail": 0, "pass": 0, "total": 0},
        "sources": {
            kind: {
                "exists": False,
                "path": str(path.relative_to(root)),
            }
            for kind, path in feature_bundle_paths(root, slug).items()
        },
        "task_summary": {"done": 0, "open": 0, "total": 0},
        "test_coverage_summary": {"done": 0, "open": 0, "total": 0},
        "test_plan": [],
    }


def _row_gap_reasons(
    *,
    criterion_done: bool,
    coverage_links: list[dict[str, Any]],
    coverage_complete: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not criterion_done:
        reasons.append("acceptance_criterion_open")
    if not coverage_links:
        reasons.append("missing_test_coverage")
    elif not coverage_complete:
        reasons.append("test_coverage_incomplete")
    return tuple(reasons)


def _matrix_rows(trace: Any, tests: Any) -> tuple[dict[str, Any], ...]:
    test_cases_by_ac: dict[str, list[dict[str, Any]]] = {}
    for test_case in tests.test_cases:
        test_cases_by_ac.setdefault(test_case.acceptance_criterion_id, []).append(
            test_case.as_dict()
        )

    coverage_by_ac: dict[str, list[dict[str, Any]]] = {}
    for link in tests.test_coverage:
        coverage_by_ac.setdefault(link.acceptance_criterion_id, []).append(
            link.as_dict()
        )

    rows: list[dict[str, Any]] = []
    for criterion in trace.acceptance_criteria:
        coverage_links = coverage_by_ac.get(criterion.id, [])
        coverage_complete = any(
            bool(link["done"]) and bool(link["target_exists"])
            for link in coverage_links
        )
        reasons = _row_gap_reasons(
            criterion_done=criterion.done,
            coverage_links=coverage_links,
            coverage_complete=coverage_complete,
        )
        rows.append(
            {
                "acceptance_criterion": criterion.as_dict(),
                "coverage_complete": coverage_complete,
                "gap_reasons": list(reasons),
                "test_cases": test_cases_by_ac.get(criterion.id, []),
                "test_coverage": coverage_links,
                "verification_status": (
                    "verified"
                    if criterion.done and coverage_complete
                    else "unverified"
                ),
            }
        )
    return tuple(rows)


def _evidence(trace: Any, tests: Any, ready: Any) -> dict[str, Any]:
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "gaps": [dict(gap) for gap in trace.gaps],
        "has_native_files": tests.has_native_files,
        "missing_files": list(tests.missing_files),
        "quality_checks": [check.as_dict() for check in trace.quality_checks],
        "ready_summary": dict(ready.summary),
        "sources": dict(trace.sources),
        "task_summary": _checklist_summary(trace.tasks),
        "test_coverage_summary": dict(tests.summary["test_coverage"]),
        "test_plan": [item.as_dict() for item in trace.test_plan],
    }


def _summary(matrix: tuple[dict[str, Any], ...], evidence: dict[str, Any]) -> dict[str, Any]:
    verified = sum(1 for row in matrix if row["verification_status"] == "verified")
    total = len(matrix)
    coverage_complete = sum(1 for row in matrix if row["coverage_complete"])
    return {
        "acceptance_criteria": total,
        "blocking_checks": len(evidence["blocking_checks"]),
        "coverage_complete": coverage_complete,
        "coverage_incomplete": total - coverage_complete,
        "gaps": len(evidence["gaps"]),
        "unverified": total - verified,
        "verified": verified,
    }


def _recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine verify matrix {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine provenance manifest . --feature {slug} --json",
        f"specspine review packet . --feature {slug} --json",
        "specspine validate . --fusion --features",
    )


def _safety_notes() -> tuple[str, ...]:
    return (
        "This verification matrix is advisory local evidence.",
        "Recommended commands are advisory and are not executed.",
        "A verified row means the local acceptance criterion is checked and has at least one checked existing coverage link; it does not prove tests were run.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )


def build_verification_matrix(root: Path, slug: str) -> VerificationMatrix:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    try:
        trace = build_feature_trace_report(resolved_root, feature_id)
        tests = build_feature_tests_report(resolved_root, feature_id)
        ready = build_feature_ready_report(
            resolved_root,
            feature_id,
            require_coverage=True,
        )
        rows = _matrix_rows(trace, tests)
        evidence = _evidence(trace, tests, ready)
        status = trace.status
        is_ready = ready.ready
    except FeatureBundleNotFoundError:
        rows = ()
        evidence = _empty_evidence(resolved_root, feature_id)
        status = "unknown"
        is_ready = False

    return VerificationMatrix(
        root=resolved_root,
        feature_id=feature_id,
        status=status,
        ready=is_ready,
        matrix=rows,
        evidence=evidence,
        summary=_summary(rows, evidence),
        recommended_commands=_recommended_commands(feature_id),
        safety_notes=_safety_notes(),
    )


def render_verification_matrix_json(matrix: VerificationMatrix) -> str:
    return json.dumps(matrix.as_dict(), indent=2, sort_keys=True) + "\n"


def render_verification_matrix_text(matrix: VerificationMatrix) -> str:
    summary = matrix.summary
    lines = [
        f"Verification matrix: {matrix.feature_id}",
        f"Status: {matrix.status}",
        f"Ready: {'yes' if matrix.ready else 'no'}",
        (
            "Summary: "
            f"acceptance_criteria={summary['acceptance_criteria']} "
            f"verified={summary['verified']} "
            f"unverified={summary['unverified']} "
            f"coverage_complete={summary['coverage_complete']} "
            f"blocking={summary['blocking_checks']}"
        ),
        "",
        "Rows:",
    ]
    if matrix.matrix:
        for row in matrix.matrix:
            criterion = row["acceptance_criterion"]
            reasons = ", ".join(row["gap_reasons"]) or "none"
            lines.append(
                "- "
                f"{criterion['id']} {row['verification_status']} "
                f"coverage={'yes' if row['coverage_complete'] else 'no'} "
                f"reasons={reasons} "
                f"{criterion['source_file']}:{criterion['line']} "
                f"{criterion['text']}"
            )
    else:
        lines.append("- None.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in matrix.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in matrix.safety_notes)
    return "\n".join(lines) + "\n"
