from __future__ import annotations

from pathlib import Path
from typing import Any

from ..drift_analysis import _correlate_cross_feature_drift, _parse_feature_drift
from ..drift_models import DriftAuditReport, FeatureDriftRecord, _now_iso
from ..evolution import _run_git  # noqa: F401
from ..features import (
    list_feature_bundles,
    validate_feature_slug,
)
from ..drift_history import _git_commit, GIT_LOG_DATE_RE
from .compliance import _build_compliance_section, _severity_distribution

__all__ = [
    "_recommended_commands",
    "build_drift_monitor_report",
]


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
