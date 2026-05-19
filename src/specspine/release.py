from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    FEATURE_FILE_PATHS,
    FEATURE_PRIORITIES,
    FEATURE_STATUSES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    _extract_markdown_section,
    _extract_scalar,
    list_feature_bundles,
    read_feature_metadata,
)


@dataclass(frozen=True)
class ReleaseEntry:
    slug: str
    title: str
    priority: str
    status_transition: str
    ac_summary: str
    validation_evidence_count: int
    project: str
    effort: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_summary": self.ac_summary,
            "effort": self.effort,
            "priority": self.priority,
            "project": self.project,
            "slug": self.slug,
            "status_transition": self.status_transition,
            "title": self.title,
            "validation_evidence_count": self.validation_evidence_count,
        }


@dataclass(frozen=True)
class BreakingChange:
    feature_id: str
    description: str
    severity: str
    affected_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "affected_commands": list(self.affected_commands),
            "description": self.description,
            "feature_id": self.feature_id,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ReleaseNotesReport:
    version: str
    date_range: str
    grouped_features: dict[str, list[ReleaseEntry]]
    breaking_changes: list[BreakingChange]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for group_name, entries in self.grouped_features.items():
            grouped[group_name] = [entry.as_dict() for entry in entries]

        return {
            "breaking_changes": [bc.as_dict() for bc in self.breaking_changes],
            "date_range": self.date_range,
            "grouped_features": grouped,
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "version": self.version,
        }


_BREAKING_CHANGE_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"removed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "high",
        "CLI argument removed",
    ),
    (
        re.compile(r"removed\s+(?:the\s+)?required\s+field", re.IGNORECASE),
        "high",
        "Required field removed",
    ),
    (
        re.compile(r"changed\s+(?:the\s+)?(?:default|behavior|validation|output)", re.IGNORECASE),
        "medium",
        "Default behavior changed",
    ),
    (
        re.compile(r"deprecated\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "low",
        "Deprecation introduced",
    ),
    (
        re.compile(r"renamed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "medium",
        "Name change",
    ),
]


def _extract_title(spec_content: str) -> str:
    first_line = spec_content.splitlines()[0].strip() if spec_content.splitlines() else ""
    if first_line.startswith("# "):
        return first_line[2:].strip().strip("#").strip()
    title = _extract_scalar(spec_content, "Feature ID")
    if title:
        return title
    return ""


def _extract_ac_summary(spec_content: str, execution_content: str) -> str:
    ac_section = _extract_markdown_section(spec_content, "Acceptance Criteria")
    if ac_section:
        lines = ac_section.splitlines()
        ac_count = sum(1 for line in lines if line.strip().startswith("- ["))
        if ac_count > 0:
            return f"{ac_count} acceptance criterion/criteria defined"
    return "No acceptance criteria section found"


def _count_validation_evidence(quality_content: str) -> int:
    count = 0
    check_patterns = [
        r"- \[x\]",
        r"- \[X\]",
    ]
    for pattern in check_patterns:
        count += len(re.findall(pattern, quality_content))
    return count


def _determine_status_transition(status: str | None) -> str:
    if status is None:
        return "unknown"
    if status == "validated":
        return "newly validated"
    if status == "archived":
        return "released (archived)"
    if status == "implemented":
        return "implemented (pending validation)"
    return f"status: {status}"


def _collect_release_features(
    root: Path,
    since: str | None = None,
    until: str | None = None,
) -> list[ReleaseEntry]:
    resolved_root = root.expanduser().resolve()
    feature_bundles = list_feature_bundles(resolved_root)

    entries: list[ReleaseEntry] = []
    for feature in feature_bundles:
        slug = str(feature["slug"])
        status = feature.get("status")
        if status not in ("validated", "archived"):
            continue

        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug:
            continue

        bundle_paths = {
            kind: resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
            for kind in FEATURE_FILE_PATHS
        }

        spec_path = bundle_paths["spec"]
        execution_path = bundle_paths["execution"]
        quality_path = bundle_paths["quality"]

        spec_content = ""
        if spec_path.exists():
            try:
                spec_content = spec_path.read_text(encoding="utf-8")
            except OSError:
                pass

        execution_content = ""
        if execution_path.exists():
            try:
                execution_content = execution_path.read_text(encoding="utf-8")
            except OSError:
                pass

        quality_content = ""
        if quality_path.exists():
            try:
                quality_content = quality_path.read_text(encoding="utf-8")
            except OSError:
                pass

        title = _extract_title(spec_content)
        if not title:
            title = slug.replace("-", " ").title()

        ac_summary = _extract_ac_summary(spec_content, execution_content)
        validation_evidence_count = _count_validation_evidence(quality_content)
        status_transition = _determine_status_transition(status)

        entries.append(
            ReleaseEntry(
                slug=slug,
                title=title,
                priority=metadata.priority,
                status_transition=status_transition,
                ac_summary=ac_summary,
                validation_evidence_count=validation_evidence_count,
                project=metadata.project,
                effort=metadata.effort,
            )
        )

    entries.sort(key=lambda e: e.slug)
    return entries


def _group_features(
    features: list[ReleaseEntry],
    group_by: str,
) -> dict[str, list[ReleaseEntry]]:
    groups: dict[str, list[ReleaseEntry]] = {}
    for feature in features:
        if group_by == "priority":
            key = feature.priority
        elif group_by == "project":
            key = feature.project
        elif group_by == "status":
            key = feature.status_transition
        elif group_by == "effort":
            key = feature.effort
        else:
            key = "all"

        groups.setdefault(key, []).append(feature)

    sorted_groups: dict[str, list[ReleaseEntry]] = {}
    for key in sorted(groups):
        sorted_groups[key] = sorted(groups[key], key=lambda e: e.slug)
    return sorted_groups


def _detect_breaking_changes(
    features: list[ReleaseEntry],
    root: Path,
) -> list[BreakingChange]:
    resolved_root = root.expanduser().resolve()
    breaking: list[BreakingChange] = []

    for feature in features:
        slug = feature.slug
        spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
        execution_path = resolved_root / FEATURE_FILE_PATHS["execution"].format(slug=slug)

        contents: list[str] = []
        for path in (spec_path, execution_path):
            if path.exists():
                try:
                    contents.append(path.read_text(encoding="utf-8"))
                except OSError:
                    pass

        full_content = "\n".join(contents)

        seen_types: set[str] = set()
        for pattern, severity, description in _BREAKING_CHANGE_PATTERNS:
            matches = pattern.findall(full_content)
            if matches:
                if description in seen_types:
                    continue
                seen_types.add(description)
                affected: list[str] = []
                for match in matches:
                    if isinstance(match, str):
                        affected.append(match)
                    elif isinstance(match, tuple):
                        affected.extend(m for m in match if m)

                breaking.append(
                    BreakingChange(
                        feature_id=slug,
                        description=f"[{description}] {feature.title}",
                        severity=severity,
                        affected_commands=tuple(sorted(set(affected))),
                    )
                )

    breaking.sort(key=lambda bc: (bc.severity, bc.feature_id))
    return breaking


def _compute_summary(
    features: list[ReleaseEntry],
    breaking_changes: list[BreakingChange],
) -> dict[str, Any]:
    total = len(features)
    validated = sum(1 for f in features if f.status_transition == "newly validated")
    archived = sum(1 for f in features if f.status_transition == "released (archived)")

    high_breaking = sum(1 for bc in breaking_changes if bc.severity == "high")
    medium_breaking = sum(1 for bc in breaking_changes if bc.severity == "medium")
    low_breaking = sum(1 for bc in breaking_changes if bc.severity == "low")

    priority_counts: dict[str, int] = {}
    for f in features:
        priority_counts[f.priority] = priority_counts.get(f.priority, 0) + 1

    total_validation_evidence = sum(f.validation_evidence_count for f in features)

    summary: dict[str, Any] = {
        "features_total": total,
        "features_validated": validated,
        "features_archived": archived,
        "breaking_changes_total": len(breaking_changes),
        "breaking_changes_high": high_breaking,
        "breaking_changes_medium": medium_breaking,
        "breaking_changes_low": low_breaking,
        "priority_counts": dict(sorted(priority_counts.items())),
        "total_validation_evidence": total_validation_evidence,
    }

    return summary


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
