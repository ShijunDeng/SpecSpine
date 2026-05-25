from __future__ import annotations

import json

from .hygiene_models import HygieneReport

__all__ = [
    "render_hygiene_scan_json",
    "render_hygiene_scan_text",
]


def render_hygiene_scan_json(report: HygieneReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_hygiene_scan_text(report: HygieneReport) -> str:
    summary = report.summary
    severity = summary["by_severity"]
    lines = [
        f"Repository hygiene scan: {report.root}",
        (
            "Summary: "
            f"changed_files={summary['changed_files']} "
            f"findings_total={summary['findings_total']} "
            f"critical={severity['critical']} "
            f"high={severity['high']} "
            f"medium={severity['medium']} "
            f"low={severity['low']} "
            f"files_scanned={summary['files_scanned']} "
            f"files_skipped={summary['files_skipped']}"
        ),
        "Findings:",
    ]
    if report.findings:
        for finding in report.findings:
            location = finding.path
            if finding.line is not None:
                location = f"{location}:{finding.line}"
            lines.append(
                "- "
                f"{finding.severity} {finding.category} "
                f"{location} [{finding.source}] - {finding.message}"
            )
    else:
        lines.append("- None.")

    lines.append("Recommended commands:")
    for command in report.recommended_commands:
        lines.append(f"- {command}")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"
