from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .consistency import _read_text
from .dependency import _list_feature_slugs
from .evolution import _run_git
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    feature_bundle_paths,
    list_feature_bundles,
    validate_feature_slug,
)

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")
SPEC_AC_LINE_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(AC\d{3}):")
EXEC_TASK_LINE_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(TASK\d{3}):")
QUALITY_COV_LINE_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")
QUALITY_QC_LINE_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(QC\d{3}):")
GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True)
class DriftEvent:
    event_type: str
    severity: str
    timestamp: str
    description: str
    affected_acs: tuple[str, ...] = ()
    affected_tasks: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "affected_acs": list(self.affected_acs),
            "affected_tasks": list(self.affected_tasks),
            "description": self.description,
            "event_type": self.event_type,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }
        return result


@dataclass(frozen=True)
class FeatureDriftRecord:
    feature_id: str
    severity: str
    spec_drift: tuple[DriftEvent, ...]
    code_drift: tuple[DriftEvent, ...]
    test_drift: tuple[DriftEvent, ...]
    quality_drift: tuple[DriftEvent, ...]
    drift_events: tuple[DriftEvent, ...]
    cascade_risk: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "cascade_risk": self.cascade_risk,
            "code_drift": [e.as_dict() for e in self.code_drift],
            "drift_events": [e.as_dict() for e in self.drift_events],
            "feature_id": self.feature_id,
            "quality_drift": [e.as_dict() for e in self.quality_drift],
            "severity": self.severity,
            "spec_drift": [e.as_dict() for e in self.spec_drift],
            "test_drift": [e.as_dict() for e in self.test_drift],
        }


@dataclass(frozen=True)
class DriftAuditReport:
    root: Path
    scan_metadata: dict[str, Any]
    features: tuple[FeatureDriftRecord, ...]
    summary: dict[str, Any]
    trends: tuple[dict[str, Any], ...]
    compliance: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "compliance": dict(self.compliance),
            "features": [f.as_dict() for f in self.features],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "scan_metadata": dict(self.scan_metadata),
            "summary": dict(self.summary),
            "trends": [dict(t) for t in self.trends],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_commit(root: Path) -> str:
    try:
        result = _run_git(["rev-parse", "HEAD"], root)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _extract_acs_from_spec(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_tasks_from_execution(content: str) -> list[str]:
    return TASK_ID_RE.findall(content)


def _extract_acs_from_quality(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_cov_links_from_quality(content: str) -> list[tuple[str, str]]:
    return COV_LINK_RE.findall(content)


def _extract_qc_ids_from_quality(content: str) -> list[str]:
    return QUALITY_CHECK_RE.findall(content)


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)


def _baseline_peer_content(root: Path, slug: str, kind: str, baseline: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    rel = rel_path.format(slug=slug)
    result = _run_git(["show", f"{baseline}:{rel}"], root)
    if result.returncode == 0:
        return result.stdout
    return None


def _detect_spec_drift(slug: str, root: Path, baseline: str | None) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    current = _feature_peer_content(root, slug, "spec")
    if current is None:
        return events

    current_acs = _extract_acs_from_spec(current)

    if baseline is not None:
        before = _baseline_peer_content(root, slug, "spec", baseline)
        if before is None:
            if current_acs:
                events.append(
                    DriftEvent(
                        event_type="spec",
                        severity="high",
                        timestamp=_now_iso(),
                        description=f"Spec file exists but missing at baseline '{baseline}'; all ACs are new",
                        affected_acs=tuple(sorted(set(current_acs))),
                    )
                )
            return events

        before_acs = _extract_acs_from_spec(before)
        before_set = set(before_acs)
        current_set = set(current_acs)

        removed = sorted(before_set - current_set)
        added = sorted(current_set - before_set)

        if removed:
            events.append(
                DriftEvent(
                    event_type="spec",
                    severity="critical",
                    timestamp=_now_iso(),
                    description=f"ACs removed from spec compared to baseline '{baseline}'",
                    affected_acs=tuple(removed),
                )
            )

        if added:
            events.append(
                DriftEvent(
                    event_type="spec",
                    severity="medium",
                    timestamp=_now_iso(),
                    description=f"ACs added to spec compared to baseline '{baseline}'",
                    affected_acs=tuple(added),
                )
            )

    return events


def _detect_code_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is None:
        return events

    from .consistency import _explicit_paths_from_feature_files, LOCAL_PATH_RE
    source_files: list[str] = []
    for kind in ("spec", "execution", "quality"):
        content = _feature_peer_content(root, slug, kind)
        if content is not None:
            source_files.append(content)

    referenced_paths: set[str] = set()
    for content in source_files:
        for match in LOCAL_PATH_RE.finditer(content):
            p = match.group("path").rstrip(".,);]`")
            referenced_paths.add(p)

    code_paths = [p for p in referenced_paths if p.startswith("src/")]
    orphaned: list[str] = []
    for path in sorted(code_paths):
        if not (root / path).exists():
            orphaned.append(path)

    if orphaned:
        events.append(
            DriftEvent(
                event_type="code",
                severity="medium",
                timestamp=_now_iso(),
                description=f"Source files referenced in spec do not exist on disk",
            )
        )

    exec_content = _feature_peer_content(root, slug, "execution")
    if exec_content is not None:
        tasks_in_exec = _extract_tasks_from_execution(exec_content)
        tasks_in_spec = _extract_acs_from_spec(spec_content)
        task_ac_refs: set[str] = set()
        for line in exec_content.splitlines():
            for ac_match in AC_ID_RE.finditer(line):
                task_ac_refs.add(ac_match.group(1))

        missing_ac_links = sorted(set(tasks_in_spec) - task_ac_refs)
        if missing_ac_links:
            events.append(
                DriftEvent(
                    event_type="code",
                    severity="medium",
                    timestamp=_now_iso(),
                    description="Tasks in execution file do not reference all spec ACs",
                    affected_acs=tuple(missing_ac_links),
                )
            )

    return events


def _detect_test_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    quality_content = _feature_peer_content(root, slug, "quality")
    if spec_content is None or quality_content is None:
        return events

    spec_acs = set(_extract_acs_from_spec(spec_content))
    cov_links = _extract_cov_links_from_quality(quality_content)
    covered_acs: set[str] = set()
    for ac_id, target_path in cov_links:
        covered_acs.add(ac_id)
        if not (root / target_path).exists():
            events.append(
                DriftEvent(
                    event_type="test",
                    severity="high",
                    timestamp=_now_iso(),
                    description=f"Test coverage link references stale test file",
                    affected_acs=(ac_id,),
                )
            )

    uncovered_acs = sorted(spec_acs - covered_acs)
    if uncovered_acs:
        events.append(
            DriftEvent(
                event_type="test",
                severity="high",
                timestamp=_now_iso(),
                description="Spec ACs have no test coverage link in quality file",
                affected_acs=tuple(uncovered_acs),
            )
        )

    return events


def _detect_quality_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    quality_content = _feature_peer_content(root, slug, "quality")
    spec_content = _feature_peer_content(root, slug, "spec")
    if quality_content is None:
        return events

    qc_ids_in_quality = set(_extract_qc_ids_from_quality(quality_content))
    cov_links = _extract_cov_links_from_quality(quality_content)
    covered_acs = {ac_id for ac_id, _ in cov_links}

    if spec_content is not None:
        spec_acs = set(_extract_acs_from_spec(spec_content))
        acs_without_qc = sorted(spec_acs - qc_ids_in_quality - covered_acs)
        if acs_without_qc:
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description="Spec ACs missing quality check or coverage link",
                    affected_acs=tuple(acs_without_qc),
                )
            )

    for ac_id, target_path in cov_links:
        if not target_path.startswith("tests/"):
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description=f"Coverage link for {ac_id} does not point to a tests/ path",
                    affected_acs=(ac_id,),
                )
            )

    return events


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

    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return events

    for line in result.stdout.strip().splitlines():
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


def _correlate_cross_feature_drift(
    features: list[FeatureDriftRecord],
    root: Path,
) -> None:
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
            c = _feature_peer_content(root, f.feature_id, kind)
            if c is not None:
                content_parts.append(c)
        all_content[f.feature_id] = "\n".join(content_parts)

    from .dependency import _extract_slugs_from_text
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
        validate_feature_slug(slug)

        spec_events = _detect_spec_drift(slug, resolved_root, baseline)
        code_events = _detect_code_drift(slug, resolved_root)
        test_events = _detect_test_drift(slug, resolved_root)
        quality_events = _detect_quality_drift(slug, resolved_root)

        severity = _classify_severity(spec_events, code_events, test_events, quality_events)

        all_drift = spec_events + code_events + test_events + quality_events
        history = _build_drift_history(slug, resolved_root, since)
        combined_events = tuple(all_drift + history)

        record = FeatureDriftRecord(
            feature_id=slug,
            severity=severity,
            spec_drift=tuple(spec_events),
            code_drift=tuple(code_events),
            test_drift=tuple(test_events),
            quality_drift=tuple(quality_events),
            drift_events=combined_events,
            cascade_risk=False,
        )
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


def render_drift_json(report: DriftAuditReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_drift_text(report: DriftAuditReport) -> str:
    summary = report.summary
    lines = [
        f"Drift monitor report: {report.root}",
        (
            "Summary: "
            f"features={summary['features_scanned']} "
            f"drift_events={summary['drift_events_total']} "
            f"drift_free={summary['drift_free_count']}"
        ),
    ]

    sev_dist = summary.get("severity_distribution", {})
    if sev_dist:
        parts = []
        for sev in ("critical", "high", "medium", "low", "none"):
            count = sev_dist.get(sev, 0)
            if count:
                parts.append(f"{sev}={count}")
        if parts:
            lines.append(f"Severity: {' '.join(parts)}")

    lines.append("")
    lines.append("Features:")
    if not report.features:
        lines.append("- none")
    for f in report.features:
        marker = "OK" if f.severity == "none" else f.severity.upper()
        cascade = " [CASCADE_RISK]" if f.cascade_risk else ""
        lines.append(
            f"- {f.feature_id}: severity={marker}{cascade} "
            f"spec={len(f.spec_drift)} code={len(f.code_drift)} "
            f"test={len(f.test_drift)} quality={len(f.quality_drift)} "
            f"total_events={len(f.drift_events)}"
        )
        for ev in f.drift_events:
            lines.append(f"  - [{ev.severity}] {ev.event_type}: {ev.description}")
            if ev.affected_acs:
                lines.append(f"    affected ACs: {', '.join(ev.affected_acs)}")
            if ev.affected_tasks:
                lines.append(f"    affected tasks: {', '.join(ev.affected_tasks)}")

    if report.trends:
        lines.extend(["", "Trends:"])
        for t in report.trends:
            lines.append(f"- {t['date']}: {t['drift_events']} events")

    if report.compliance:
        lines.extend(["", "Compliance:"])
        lines.append(f"- evidence_hash: {report.compliance.get('evidence_hash', 'N/A')}")
        pf = report.compliance.get("pass_fail_per_dimension", {})
        for dim in ("spec", "code", "test", "quality"):
            status = pf.get(dim, "N/A")
            lines.append(f"- {dim}: {status}")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {cmd}" for cmd in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
