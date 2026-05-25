from __future__ import annotations

import json

from .verification_models import VerificationMatrix

__all__ = [
    "render_verification_matrix_json",
    "render_verification_matrix_text",
]


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
