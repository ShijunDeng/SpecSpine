from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
    validate_feature_slug,
)
from .verification_matrix import (
    _empty_evidence,
    _evidence,
    _matrix_rows,
    _summary,
)
from .verification_models import VerificationMatrix


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


__all__ = [
    "build_verification_matrix",
    "render_verification_matrix_json",
    "render_verification_matrix_text",
]
