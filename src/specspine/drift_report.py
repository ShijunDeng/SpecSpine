from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .drift_analysis import _correlate_cross_feature_drift, _parse_feature_drift
from .drift_models import DriftAuditReport, FeatureDriftRecord, _now_iso
from .evolution import _run_git
from .features import (
    list_feature_bundles,
    validate_feature_slug,
)
from .drift_history import _git_commit, GIT_LOG_DATE_RE

__all__ = [
    "_build_compliance_section",
    "_now_iso",
    "_recommended_commands",
    "_severity_distribution",
    "build_drift_monitor_report",
]


def _build_compliance_section(report: DriftAuditReport) -> dict[str, Any]:
    evidence_parts: list[str] = [
        str(report.root),
        report.scan_metadata.get("timestamp", ""),
        report.scan_metadata.get("git_commit", ""),
    ]
    for f in report.features:
        evidence_parts.append(f.feature_id)
        evidence_parts.append(f.severity)
        for ev in f.drift_events:
            evidence_parts.append(ev.event_type)
            evidence_parts.append(ev.severity)
            evidence_parts.append(ev.description)

    evidence_str = "\n".join(sorted(evidence_parts))
    evidence_hash = hashlib.sha256(evidence_str.encode("utf-8")).hexdigest()

    pass_fail: dict[str, str] = {}
    dimensions = ["spec", "code", "test", "quality"]
    for dim in dimensions:
        has_drift = False
        for f in report.features:
            if dim == "spec" and f.spec_drift:
                has_drift = True
            elif dim == "code" and f.code_drift:
                has_drift = True
            elif dim == "test" and f.test_drift:
                has_drift = True
            elif dim == "quality" and f.quality_drift:
                has_drift = True
        pass_fail[dim] = "fail" if has_drift else "pass"

    return {
        "evidence_hash": evidence_hash,
        "pass_fail_per_dimension": pass_fail,
    }


def _severity_distribution(features: tuple[FeatureDriftRecord, ...]) -> dict[str, int]:
    dist: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0,
    }
    for f in features:
        dist[f.severity] = dist.get(f.severity, 0) + 1
    return dist


def _recommended_commands(feature_ids: tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = ["specspine drift monitor . --json"]
    for slug in feature_ids:
        commands.append(f"specspine drift monitor . --feature {slug} --json")
    commands.append("specspine consistency scan . --json")
    commands.append("specspine validate . --fusion --features")
    seen: set[str] = set()
    deduped: list[str] = []
    for c in commands:
        if c not in seen:
            seen.add(c)
            deduped.append(c)
    return tuple(deduped)


def build_drift_monitor_report(
    root: Path,
    *,
    feature_filter: str | None = None,
    baseline: str | None = None,
    since: str | None = None,
) -> DriftAuditReport:
    resolved_root = root.expanduser().resolve()

    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = {str(f["slug"]) for f in discovered}

    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = tuple(sorted(discovered_slugs))

    feature_records: list[FeatureDriftRecord] = []
    for slug in slugs:
        record = _parse_feature_drift(slug, resolved_root, baseline, since)
        feature_records.append(record)

    _correlate_cross_feature_drift(feature_records, resolved_root)

    feature_tuple = tuple(sorted(feature_records, key=lambda f: f.feature_id))

    severity_dist = _severity_distribution(feature_tuple)
    total_events = sum(len(f.drift_events) for f in feature_tuple)
    drift_free = sum(1 for f in feature_tuple if f.severity == "none")

    trends: tuple[dict[str, Any], ...] = ()
    if since is not None:
        trend_entries: list[dict[str, Any]] = []
        date_events: dict[str, int] = {}
        for f in feature_tuple:
            for ev in f.drift_events:
                date_match = GIT_LOG_DATE_RE.match(ev.timestamp)
                if date_match:
                    day = date_match.group(0)
                    date_events[day] = date_events.get(day, 0) + 1
        for day in sorted(date_events):
            trend_entries.append({"date": day, "drift_events": date_events[day]})
        trends = tuple(trend_entries)

    summary = {
        "drift_events_total": total_events,
        "drift_free_count": drift_free,
        "features_scanned": len(feature_tuple),
        "severity_distribution": severity_dist,
    }

    scan_metadata = {
        "baseline": baseline,
        "git_commit": _git_commit(resolved_root),
        "since": since,
        "timestamp": _now_iso(),
    }

    report = DriftAuditReport(
        root=resolved_root,
        scan_metadata=scan_metadata,
        features=feature_tuple,
        summary=summary,
        trends=trends,
        compliance={},
        recommended_commands=_recommended_commands(tuple(f.feature_id for f in feature_tuple)),
        safety_notes=(
            "This drift monitor report reads local workspace files only.",
            "Recommended commands are advisory only and are not executed.",
            "SpecSpine did not run tests, invoke subprocesses (except git show/log for baseline comparison), call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
        ),
    )

    compliance = _build_compliance_section(report)
    object.__setattr__(report, "compliance", compliance)

    return report
