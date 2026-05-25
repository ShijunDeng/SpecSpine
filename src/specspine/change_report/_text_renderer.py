from __future__ import annotations

from ..change_models import ChangeRiskReport

__all__ = [
    "render_change_risk_text",
]


def render_change_risk_text(report: ChangeRiskReport) -> str:
    summary = report.summary
    lines = [
        f"Change risk report: {report.root}",
        f"Feature: {report.feature_id or 'workspace'}",
        (
            "Summary: "
            f"changed_files={summary['changed_files']} "
            f"high={summary['high']} "
            f"medium={summary['medium']} "
            f"low={summary['low']}"
        ),
        "",
        "Changed files:",
    ]
    lines.extend(
        f"- [{file['risk']}] {file['category']}: {file['path']}"
        for file in report.files
    )
    lines.extend(["", "Feature evidence:"])
    if report.feature_evidence:
        lines.extend(
            (
                f"- {evidence['feature_id']}: "
                f"status={evidence['status']} "
                f"ready={evidence['ready']} "
                f"has_native_files={evidence['has_native_files']}"
            )
            for evidence in report.feature_evidence
        )
    else:
        lines.append("- none")
    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
