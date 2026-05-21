from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from .drift_models import DriftEvent, FeatureDriftRecord, DriftAuditReport, _now_iso
from .evolution import _run_git
from .features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
    list_feature_bundles,
    validate_feature_slug,
)

from .drift_detection import (
    _detect_code_drift,
    _detect_spec_drift,
    _detect_test_drift,
    _detect_quality_drift,
)

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

__all__ = [
    "build_drift_monitor_report",
    "_build_drift_history",
    "_run_git_log",
    "_parse_feature_drift",
    "_classify_severity",
    "_correlate_cross_feature_drift",
    "_build_compliance_section",
    "_severity_distribution",
    "_git_commit",
    "_now_iso",
]


def _git_commit(root: Path) -> str:
    import subprocess
    try:
        result = _run_git(["rev-parse", "HEAD"], root)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _run_git_log(root: Path, rel_paths: list[str]) -> list[str]:
    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return []
    return result.stdout.strip().splitlines()


def _build_drift_history(slug: str, root: Path, since: str | None) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    lines = _run_git_log(root, rel_paths)
    for line in lines:
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash, date_str = parts[0], parts[1]
        message = parts[2] if len(parts) > 2 else ""

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = "spec"
        for kind in ("spec", "execution", "quality"):
            rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
            if rel in " ".join(rel_paths):
                event_type = kind
                break

        severity = "medium"
        if any(kw in message.lower() for kw in ("remove", "delete", "drop")):
            severity = "high"
        elif any(kw in message.lower() for kw in ("add", "new", "create")):
            severity = "low"

        events.append(
            DriftEvent(
                event_type=event_type,
                severity=severity,
                timestamp=date_str.strip(),
                description=f"Commit {commit_hash[:8]}: {message}",
            )
        )

    return events


def _parse_feature_drift(slug: str, root: Path, baseline: str | None, since: str | None) -> FeatureDriftRecord:
    validate_feature_slug(slug)

    spec_events = _detect_spec_drift(slug, root, baseline)
    code_events = _detect_code_drift(slug, root)
    test_events = _detect_test_drift(slug, root)
    quality_events = _detect_quality_drift(slug, root)

    severity = _classify_severity(spec_events, code_events, test_events, quality_events)

    all_drift = spec_events + code_events + test_events + quality_events
    history = _build_drift_history(slug, root, since)
    combined_events = tuple(all_drift + history)

    return FeatureDriftRecord(
        feature_id=slug,
        severity=severity,
        spec_drift=tuple(spec_events),
        code_drift=tuple(code_events),
        test_drift=tuple(test_events),
        quality_drift=tuple(quality_events),
        drift_events=combined_events,
        cascade_risk=False,
    )


def _classify_severity(
    spec_events: list[DriftEvent],
    code_events: list[DriftEvent],
    test_events: list[DriftEvent],
    quality_events: list[DriftEvent],
) -> str:
    all_events = spec_events + code_events + test_events + quality_events
    if not all_events:
        return "none"

    severity_order = ["critical", "high", "medium", "low"]
    for sev in severity_order:
        for ev in all_events:
            if ev.severity == sev:
                return sev
    return "none"


def _correlate_cross_feature_drift(
    features: list[FeatureDriftRecord],
    root: Path,
) -> None:
    from .consistency import _read_text
    from .features import FEATURE_FILE_PATHS
    from .dependency import _extract_slugs_from_text

    critical_features: dict[str, FeatureDriftRecord] = {}
    for f in features:
        if f.severity == "critical":
            critical_features[f.feature_id] = f

    if not critical_features:
        return

    all_content: dict[str, str] = {}
    for f in features:
        content_parts: list[str] = []
        for kind in ("spec", "execution", "quality"):
            rel_path = FEATURE_FILE_PATHS.get(kind)
            if rel_path is None:
                continue
            path = root / rel_path.format(slug=f.feature_id)
            if path.exists():
                content_parts.append(_read_text(path))
        all_content[f.feature_id] = "\n".join(content_parts)

    all_slugs = {f.feature_id for f in features}
    for f in features:
        if f.cascade_risk:
            continue
        content = all_content.get(f.feature_id, "")
        deps = _extract_slugs_from_text(content, f.feature_id, all_slugs)
        for dep_slug in deps:
            if dep_slug in critical_features:
                object.__setattr__(f, "cascade_risk", True)
                break


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
