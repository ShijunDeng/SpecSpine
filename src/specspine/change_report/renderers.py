from __future__ import annotations

import json
from typing import Any

from ..change_models import ChangeRiskReport
from ..change_classifiers import _dedupe

__all__ = [
    "_recommended_commands",
    "render_change_risk_json",
    "render_change_risk_text",
]


def _recommended_commands(
    changed_files: tuple[str, ...],
    feature_ids: tuple[str, ...],
) -> tuple[str, ...]:
    commands: list[str] = []
    for path in changed_files:
        commands.append(f"specspine tests impact . --changed {path} --json")
        commands.append(f"specspine review packet . --changed {path} --json")
    for slug in feature_ids:
        commands.append(f"specspine tests impact . --feature {slug} --json")
        commands.append(f"specspine review packet . --feature {slug} --json")
        commands.append(
            f"specspine feature ready {slug} . --json --require-coverage"
        )
    if not commands:
        commands.extend(
            [
                "specspine change risk . --json",
                "specspine review packet . --json",
                "specspine validate . --fusion --features",
            ]
        )
    return _dedupe(commands)


def render_change_risk_json(report: ChangeRiskReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


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
