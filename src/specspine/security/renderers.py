from __future__ import annotations

import json

from .models import SecurityCueReport

__all__ = [
    "render_security_cue_json",
    "render_security_cue_text",
]


def render_security_cue_json(report: SecurityCueReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_security_cue_text(report: SecurityCueReport) -> str:
    summary = report.summary
    lines = [
        f"Security cues report: {report.root}",
        f"Feature: {report.feature_id or 'workspace'}",
        (
            "Summary: "
            f"changed_files={summary['changed_files']} "
            f"files_existing={summary['files_existing']} "
            f"cues_total={summary['cues_total']} "
            f"high={summary['high']} "
            f"medium={summary['medium']} "
            f"low={summary['low']}"
        ),
        "Files:",
    ]
    if report.files:
        for file in report.files:
            marker = "exists" if file["exists"] else "missing"
            lines.append(f"- [{marker}] {file['category']}: {file['path']}")
    else:
        lines.append("- None.")

    lines.append("Cues:")
    if report.cues:
        for cue in report.cues:
            lines.append(
                "- "
                f"{cue['severity']} {cue['keyword']} "
                f"{cue['path']}:{cue['line']} - {cue['message']}"
            )
    else:
        lines.append("- None.")

    if report.feature_evidence:
        lines.append("Feature evidence:")
        for evidence in report.feature_evidence:
            lines.append(
                "- "
                f"{evidence['feature_id']}: "
                f"status={evidence['status']} "
                f"ready={'yes' if evidence['ready'] else 'no'} "
                f"has_native_files={'yes' if evidence['has_native_files'] else 'no'}"
            )

    lines.append("Recommended commands:")
    for command in report.recommended_commands:
        lines.append(f"- {command}")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"
