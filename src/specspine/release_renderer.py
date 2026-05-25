from __future__ import annotations

import json
from pathlib import Path

from .release_breaking import _compute_summary, _detect_breaking_changes
from .release_features import _collect_release_features, _group_features
from .release_models import ReleaseNotesReport

__all__ = [
    "_safety_notes",
    "build_release_notes_report",
    "render_release_notes_json",
    "render_release_notes_json_lines",
    "render_release_notes_text",
]


def _safety_notes() -> tuple[str, ...]:
    return (
        "This release notes report is advisory only.",
        "Breaking change detection uses heuristic pattern matching on spec content.",
        "SpecSpine did not run commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )


def build_release_notes_report(
    root: Path,
    since: str | None = None,
    until: str | None = None,
    group_by: str = "priority",
) -> ReleaseNotesReport:
    resolved_root = root.expanduser().resolve()

    features = _collect_release_features(resolved_root, since=since, until=until)
    grouped = _group_features(features, group_by)
    breaking_changes = _detect_breaking_changes(features, resolved_root)
    summary = _compute_summary(features, breaking_changes)

    date_range = ""
    if since and until:
        date_range = f"{since}..{until}"
    elif since:
        date_range = f"{since}..latest"
    elif until:
        date_range = f"initial..{until}"
    else:
        date_range = "all"

    return ReleaseNotesReport(
        version="1",
        date_range=date_range,
        grouped_features=grouped,
        breaking_changes=breaking_changes,
        summary=summary,
        safety_notes=_safety_notes(),
    )


def render_release_notes_json(report: ReleaseNotesReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_release_notes_text(report: ReleaseNotesReport) -> str:
    summary = report.summary
    lines = [
        "# Release Notes",
        "",
        f"Version: {report.version}",
        f"Date Range: {report.date_range}",
        "",
        "## Summary",
        "",
        f"- Features Total: {summary['features_total']}",
        f"- Validated: {summary['features_validated']}",
        f"- Archived: {summary['features_archived']}",
        f"- Breaking Changes: {summary['breaking_changes_total']}",
        f"- Validation Evidence Items: {summary['total_validation_evidence']}",
        "",
    ]

    if summary["priority_counts"]:
        lines.append("## Features by Priority")
        lines.append("")
        for priority, count in sorted(summary["priority_counts"].items()):
            lines.append(f"- {priority}: {count}")
        lines.append("")

    if report.grouped_features:
        lines.append("## Features")
        lines.append("")
        for group_name, entries in report.grouped_features.items():
            lines.append(f"### {group_name}")
            lines.append("")
            for entry in entries:
                marker = "validated" if entry.status_transition == "newly validated" else "archived"
                lines.append(f"- **{entry.title}** (`{entry.slug}`) [{marker}]")
                lines.append(f"  - Priority: {entry.priority}")
                lines.append(f"  - Project: {entry.project}")
                lines.append(f"  - Effort: {entry.effort}")
                lines.append(f"  - {entry.ac_summary}")
                lines.append(f"  - Validation evidence: {entry.validation_evidence_count} items")
            lines.append("")

    if report.breaking_changes:
        lines.append("## Breaking Changes")
        lines.append("")
        for bc in report.breaking_changes:
            sev_marker = bc.severity.upper()
            lines.append(f"- [{sev_marker}] `{bc.feature_id}`: {bc.description}")
            if bc.affected_commands:
                for cmd in bc.affected_commands:
                    lines.append(f"  - Affects: `{cmd}`")
        lines.append("")

    lines.append("## Safety Notes")
    lines.append("")
    for note in report.safety_notes:
        lines.append(f"- {note}")
    lines.append("")

    return "\n".join(lines)


def render_release_notes_json_lines(report: ReleaseNotesReport) -> str:
    json_lines: list[str] = []
    json_lines.append(json.dumps({"type": "release_notes", **report.as_dict()}, sort_keys=True))

    for group_name, entries in report.grouped_features.items():
        for entry in entries:
            json_lines.append(
                json.dumps(
                    {"type": "feature", "group": group_name, **entry.as_dict()},
                    sort_keys=True,
                )
            )

    for bc in report.breaking_changes:
        json_lines.append(
            json.dumps({"type": "breaking_change", **bc.as_dict()}, sort_keys=True)
        )

    return "\n".join(json_lines) + "\n"
