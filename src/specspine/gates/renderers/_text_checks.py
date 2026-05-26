from __future__ import annotations

from ..models import QualityGateReport

__all__ = [
    "render_required_checks_lines",
    "render_definition_lines",
    "render_commands_lines",
]


def _format_gate_metadata(gate) -> str:
    metadata = f"severity={gate.severity} owner={gate.owner}"
    if gate.ci_check is not None:
        metadata = f"{metadata} ci={gate.ci_check}"
    if gate.metadata_warnings:
        metadata = f"{metadata} warnings={len(gate.metadata_warnings)}"
    return metadata


def render_required_checks_lines(report: QualityGateReport) -> list[str]:
    lines: list[str] = ["", "Required Checks:"]

    if report.required_checks:
        for gate in report.required_checks:
            marker = "x" if gate.done else " "
            metadata = _format_gate_metadata(gate)
            lines.append(
                f"- [{marker}] {gate.id} {gate.source_file}:{gate.line} "
                f"{gate.text} ({metadata})"
            )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Required Checks.")

    return lines


def render_definition_lines(report: QualityGateReport) -> list[str]:
    lines: list[str] = ["", "Definition Of Done:"]

    if report.definition_of_done:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.definition_of_done
        )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Definition Of Done.")

    return lines


def render_commands_lines(report: QualityGateReport) -> list[str]:
    lines: list[str] = ["", "Recommended commands:"]
    lines.extend(f"- {command}" for command in report.recommended_commands)
    return lines
