from __future__ import annotations

import json

from .models import QualityGateReport

__all__ = [
    "render_quality_gate_json",
    "render_quality_gate_text",
]


def render_quality_gate_json(report: QualityGateReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_quality_gate_text(report: QualityGateReport) -> str:
    summary = report.summary
    lines = [
        f"Quality gates: {report.root}",
        f"Source: {report.source_file}",
    ]
    if report.source_missing:
        lines.append("Source missing: yes")
    else:
        lines.append("Source missing: no")

    lines.extend(
        [
            (
                "Summary: "
                f"required={summary['required_total']} "
                f"done={summary['required_done']} "
                f"open={summary['required_open']} "
                f"definition={summary['definition_total']}"
            ),
            "",
            "Required Checks:",
        ]
    )

    if report.required_checks:
        for gate in report.required_checks:
            marker = "x" if gate.done else " "
            metadata = f"severity={gate.severity} owner={gate.owner}"
            if gate.ci_check is not None:
                metadata = f"{metadata} ci={gate.ci_check}"
            if gate.metadata_warnings:
                metadata = f"{metadata} warnings={len(gate.metadata_warnings)}"
            lines.append(
                f"- [{marker}] {gate.id} {gate.source_file}:{gate.line} "
                f"{gate.text} ({metadata})"
            )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Required Checks.")

    lines.extend(["", "Definition Of Done:"])
    if report.definition_of_done:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.definition_of_done
        )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Definition Of Done.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
