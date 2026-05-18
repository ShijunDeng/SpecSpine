from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
    build_feature_ready_report,
    build_feature_trace_report,
    feature_bundle_paths,
    list_feature_bundles,
    parse_test_coverage,
    validate_feature_slug,
)


SEVERITIES = ("critical", "high", "medium", "low")
AC_REFERENCE_RE = re.compile(r"\bAC[-\s]?0*(\d{1,})\b", re.IGNORECASE)
TEST_TARGET_RE = re.compile(r"\b(?:tests?/|test_|_test\b|pytest|unittest)\b", re.IGNORECASE)
QUALITY_REFERENCE_RE = re.compile(r"\b(?:Q|COV|TC)[-\s]?0*(\d{1,})\b", re.IGNORECASE)
VAGUE_TERMS = (
    "appropriate",
    "easy",
    "efficient",
    "fast",
    "flexible",
    "intuitive",
    "performant",
    "reliable",
    "robust",
    "scalable",
    "seamless",
    "simple",
    "user-friendly",
)
TEXT_MAX_ISSUES_PER_FEATURE = 8
TEXT_MAX_RECOMMENDATIONS = 12


@dataclass(frozen=True)
class AnalysisIssue:
    id: str
    feature_id: str
    severity: str
    category: str
    code: str
    message: str
    source_file: str
    line: int | None = None
    evidence: dict[str, object] | None = None
    recommended_command: str | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "category": self.category,
            "code": self.code,
            "feature_id": self.feature_id,
            "id": self.id,
            "message": self.message,
            "severity": self.severity,
            "source_file": self.source_file,
        }
        if self.line is not None:
            payload["line"] = self.line
        if self.evidence:
            payload["evidence"] = dict(self.evidence)
        if self.recommended_command:
            payload["recommended_command"] = self.recommended_command
        return payload


@dataclass(frozen=True)
class FeatureAnalysis:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    metrics: dict[str, int | bool]
    issues: tuple[AnalysisIssue, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "issues": [issue.as_dict() for issue in self.issues],
            "metrics": dict(self.metrics),
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
        }


@dataclass(frozen=True)
class AnalysisReport:
    root: Path
    feature_filter: str | None
    summary: dict[str, object]
    features: tuple[FeatureAnalysis, ...]
    issues: tuple[AnalysisIssue, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_filter": self.feature_filter,
            "features": [feature.as_dict() for feature in self.features],
            "issues": [issue.as_dict() for issue in self.issues],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "summary": dict(self.summary),
        }


@dataclass(frozen=True)
class _PendingIssue:
    feature_id: str
    severity: str
    category: str
    code: str
    message: str
    source_file: str
    line: int | None = None
    evidence: dict[str, object] | None = None
    recommended_command: str | None = None


def _feature_trace_command(slug: str) -> str:
    return f"specspine feature trace {slug} . --json"


def _feature_ready_command(slug: str) -> str:
    return f"specspine feature ready {slug} . --json --require-coverage"


def _feature_tests_command(slug: str) -> str:
    return f"specspine feature tests {slug} . --json"


def _normalize_ac_id(value: str) -> str:
    match = AC_REFERENCE_RE.search(value)
    if match is None:
        return "unknown"
    return f"AC{int(match.group(1)):03d}"


def _referenced_ac_ids(text: str) -> set[str]:
    return {f"AC{int(match.group(1)):03d}" for match in AC_REFERENCE_RE.finditer(text)}


def _source_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    files = feature.get("files")
    if isinstance(files, dict):
        return tuple(sorted(str(path) for path in files.values()))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )


def _missing_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    missing = feature.get("missing_files")
    if isinstance(missing, list):
        return tuple(sorted(str(path) for path in missing))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )


def _read_test_coverage(
    root: Path,
    slug: str,
) -> tuple[FeatureTestCoverageLink, ...]:
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return ()
    quality_file = FEATURE_FILE_PATHS["quality"].format(slug=slug)
    quality_content = quality_path.read_text(encoding="utf-8")
    return parse_test_coverage(
        quality_content,
        source_file=quality_file,
        root=root,
    )


def _coverage_ac_id(link: FeatureTestCoverageLink) -> str:
    if link.acceptance_criterion_id != "unknown":
        return _normalize_ac_id(link.acceptance_criterion_id)
    return _normalize_ac_id(link.text)


def _ready_check_severity(check: FeatureReadyCheck) -> str:
    if check.id in {"feature.bundle_files", "feature.status_consistency"}:
        return "high"
    if check.id in {
        "feature.trace_gaps",
        "feature.acceptance_criteria",
        "feature.required_checks",
        "feature.test_plan",
        "feature.test_coverage",
    }:
        return "medium"
    return "low"


def _ready_check_category(check: FeatureReadyCheck) -> str:
    if check.id == "feature.test_coverage":
        return "coverage"
    if check.id in {"feature.bundle_files", "feature.status_consistency"}:
        return "artifact"
    return "readiness"


def _readiness_issues(
    slug: str,
    checks: tuple[FeatureReadyCheck, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for check in checks:
        if check.status != "fail":
            continue
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity=_ready_check_severity(check),
                category=_ready_check_category(check),
                code=check.id,
                message=check.message,
                source_file=FEATURE_FILE_PATHS["quality"].format(slug=slug),
                evidence={"check_id": check.id},
                recommended_command=_feature_ready_command(slug),
            )
        )
    return issues


def _trace_gap_issues(slug: str, trace_report: FeatureTraceReport) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for gap in trace_report.gaps:
        gap_id = gap["id"]
        severity = "high" if gap_id == "missing_file" else "medium"
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity=severity,
                category="artifact" if gap_id == "missing_file" else "traceability",
                code=f"trace.{gap_id}",
                message=gap["message"],
                source_file=gap["source_file"],
                recommended_command=_feature_trace_command(slug),
            )
        )
    return issues


def _ac_traceability_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    task_refs = set().union(*(_referenced_ac_ids(task.text) for task in tasks)) if tasks else set()
    coverage_refs = {_coverage_ac_id(link) for link in coverage_links}
    covered_refs = {
        _coverage_ac_id(link)
        for link in coverage_links
        if link.done and link.target_exists
    }
    known_ids = {criterion.id for criterion in acceptance_criteria}

    for criterion in acceptance_criteria:
        if criterion.id not in task_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="traceability",
                    code="acceptance.no_task_reference",
                    message=(
                        f"{criterion.id} has no execution task reference by AC id."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_trace_command(slug),
                )
            )
        if criterion.id not in coverage_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_coverage_link",
                    message=f"{criterion.id} has no Test Coverage link.",
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_tests_command(slug),
                )
            )
        elif criterion.id not in covered_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_completed_coverage",
                    message=(
                        f"{criterion.id} lacks a checked Test Coverage link to an "
                        "existing local target."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_ready_command(slug),
                )
            )

    for link in coverage_links:
        link_ac_id = _coverage_ac_id(link)
        if link_ac_id not in known_ids:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="coverage.unknown_acceptance_criterion",
                    message=(
                        f"{link.id} points to unknown acceptance criterion "
                        f"{link_ac_id}."
                    ),
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "acceptance_criterion_id": link_ac_id,
                        "coverage_link_id": link.id,
                    },
                    recommended_command=_feature_tests_command(slug),
                )
            )
        if link.target_path and not link.target_exists:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="high",
                    category="coverage",
                    code="coverage.missing_target",
                    message=f"{link.id} target does not exist: {link.target_path}",
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "coverage_link_id": link.id,
                        "target_path": link.target_path,
                    },
                    recommended_command=_feature_tests_command(slug),
                )
            )
        if not link.done and link_ac_id in known_ids:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="coverage",
                    code="coverage.open_link",
                    message=f"{link.id} is not checked for {link_ac_id}.",
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "acceptance_criterion_id": link_ac_id,
                        "coverage_link_id": link.id,
                    },
                    recommended_command=_feature_ready_command(slug),
                )
            )

    return issues


def _task_traceability_issues(
    slug: str,
    tasks: tuple[FeatureTask, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for task in tasks:
        has_ac_ref = bool(_referenced_ac_ids(task.text))
        has_test_or_quality_ref = bool(
            TEST_TARGET_RE.search(task.text) or QUALITY_REFERENCE_RE.search(task.text)
        )
        if has_ac_ref or has_test_or_quality_ref:
            continue
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity="low",
                category="traceability",
                code="task.no_reference",
                message=(
                    f"{task.id} has no AC, test, or quality reference in its task text."
                ),
                source_file=task.source_file,
                line=task.line,
                evidence={"task_id": task.id},
                recommended_command=_feature_trace_command(slug),
            )
        )
    return issues


def _normalized_criterion_text(text: str) -> str:
    normalized = re.sub(r"`([^`]*)`", r"\1", text.lower())
    normalized = re.sub(r"\b(ac[-\s]?0*\d+|must|should|shall)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _criterion_quality_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    by_text: dict[str, list[FeatureTraceChecklistItem]] = {}
    for criterion in acceptance_criteria:
        normalized = _normalized_criterion_text(criterion.text)
        if normalized:
            by_text.setdefault(normalized, []).append(criterion)
        lowered = criterion.text.lower()
        vague_terms = [
            term
            for term in VAGUE_TERMS
            if re.search(rf"\b{re.escape(term)}\b", lowered)
        ]
        if vague_terms:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="quality",
                    code="acceptance.vague_text",
                    message=(
                        f"{criterion.id} contains vague term(s): "
                        + ", ".join(vague_terms)
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={
                        "acceptance_criterion_id": criterion.id,
                        "terms": vague_terms,
                    },
                    recommended_command=_feature_trace_command(slug),
                )
            )

    for duplicates in by_text.values():
        if len(duplicates) < 2:
            continue
        duplicate_ids = [criterion.id for criterion in duplicates]
        for criterion in duplicates:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="quality",
                    code="acceptance.duplicate_text",
                    message=(
                        f"{criterion.id} duplicates acceptance criterion text: "
                        + ", ".join(duplicate_ids)
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={
                        "acceptance_criterion_id": criterion.id,
                        "duplicate_acceptance_criterion_ids": duplicate_ids,
                    },
                    recommended_command=_feature_trace_command(slug),
                )
            )
    return issues


def _dedupe_commands(commands: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return tuple(deduped)


def _build_missing_feature_analysis(root: Path, slug: str) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    missing_files = tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )
    issue = _PendingIssue(
        feature_id=slug,
        severity="critical",
        category="artifact",
        code="feature.missing_bundle",
        message=f"No native feature files found for '{slug}'.",
        source_file=missing_files[0],
        evidence={"missing_files": list(missing_files)},
        recommended_command=f"specspine feature new {slug} .",
    )
    metrics: dict[str, int | bool] = {
        "acceptance_criteria_total": 0,
        "coverage_links_total": 0,
        "covered_acceptance_criteria": 0,
        "quality_checks_total": 0,
        "ready": False,
        "readiness_blocking_checks": 1,
        "tasks_total": 0,
        "test_plan_total": 0,
    }
    analysis = FeatureAnalysis(
        feature_id=slug,
        status="unknown",
        ready=False,
        source_files=missing_files,
        missing_files=missing_files,
        metrics=metrics,
        issues=(),
        recommended_commands=(f"specspine feature new {slug} .",),
    )
    return analysis, [issue]


def _build_feature_analysis(
    root: Path,
    feature: dict[str, object],
) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    slug = str(feature["slug"])
    try:
        trace_report = build_feature_trace_report(root, slug)
    except FeatureBundleNotFoundError:
        return _build_missing_feature_analysis(root, slug)

    ready_report = build_feature_ready_report(root, slug, require_coverage=True)
    coverage_links = _read_test_coverage(root, slug)
    known_ids = {criterion.id for criterion in trace_report.acceptance_criteria}
    covered_ids = {
        _coverage_ac_id(link)
        for link in coverage_links
        if _coverage_ac_id(link) in known_ids and link.done and link.target_exists
    }

    pending_issues: list[_PendingIssue] = []
    pending_issues.extend(_trace_gap_issues(slug, trace_report))
    pending_issues.extend(_readiness_issues(slug, ready_report.blocking_checks))
    pending_issues.extend(
        _ac_traceability_issues(
            slug,
            trace_report.acceptance_criteria,
            trace_report.tasks,
            coverage_links,
        )
    )
    pending_issues.extend(_task_traceability_issues(slug, trace_report.tasks))
    pending_issues.extend(_criterion_quality_issues(slug, trace_report.acceptance_criteria))

    metrics: dict[str, int | bool] = {
        "acceptance_criteria_total": len(trace_report.acceptance_criteria),
        "coverage_links_total": len(coverage_links),
        "covered_acceptance_criteria": len(covered_ids),
        "quality_checks_total": len(trace_report.quality_checks),
        "ready": ready_report.ready,
        "readiness_blocking_checks": len(ready_report.blocking_checks),
        "tasks_total": len(trace_report.tasks),
        "test_plan_total": len(trace_report.test_plan),
    }
    recommended_commands = _dedupe_commands(
        [
            command
            for issue in pending_issues
            for command in ([issue.recommended_command] if issue.recommended_command else [])
        ]
        or ["specspine validate . --fusion --features --json"]
    )
    return (
        FeatureAnalysis(
            feature_id=slug,
            status=trace_report.status,
            ready=ready_report.ready,
            source_files=_source_files(feature, slug),
            missing_files=_missing_files(feature, slug),
            metrics=metrics,
            issues=(),
            recommended_commands=recommended_commands,
        ),
        pending_issues,
    )


def _assign_issue_ids(
    pending_by_feature: dict[str, list[_PendingIssue]],
) -> dict[str, tuple[AnalysisIssue, ...]]:
    sequence = 1
    assigned: dict[str, tuple[AnalysisIssue, ...]] = {}
    for slug in sorted(pending_by_feature):
        feature_issues: list[AnalysisIssue] = []
        pending_issues = sorted(
            pending_by_feature[slug],
            key=lambda issue: (
                SEVERITIES.index(issue.severity),
                issue.category,
                issue.code,
                issue.source_file,
                issue.line or 0,
                issue.message,
            ),
        )
        for pending in pending_issues:
            feature_issues.append(
                AnalysisIssue(
                    id=f"AN{sequence:03d}",
                    feature_id=pending.feature_id,
                    severity=pending.severity,
                    category=pending.category,
                    code=pending.code,
                    message=pending.message,
                    source_file=pending.source_file,
                    line=pending.line,
                    evidence=pending.evidence,
                    recommended_command=pending.recommended_command,
                )
            )
            sequence += 1
        assigned[slug] = tuple(feature_issues)
    return assigned


def _summary(
    features: tuple[FeatureAnalysis, ...],
    issues: tuple[AnalysisIssue, ...],
    *,
    discovered_features: int,
) -> dict[str, object]:
    severity_counts = {severity: 0 for severity in SEVERITIES}
    category_counts: dict[str, int] = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

    return {
        "category_counts": dict(sorted(category_counts.items())),
        "discovered_features": discovered_features,
        "features_analyzed": len(features),
        "features_ready": sum(1 for feature in features if feature.ready),
        "features_total": len(features),
        "features_with_issues": sum(1 for feature in features if feature.issues),
        "issue_counts_by_category": dict(sorted(category_counts.items())),
        "issue_counts_by_severity": severity_counts,
        "issues_total": len(issues),
        "severity_counts": severity_counts,
    }


def build_analysis_report(
    root: Path,
    *,
    feature_filter: str | None = None,
) -> AnalysisReport:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    selected = [
        feature
        for feature in discovered
        if feature_filter is None or str(feature["slug"]) == feature_filter
    ]
    if feature_filter is not None and not selected:
        selected = [
            {
                "slug": feature_filter,
                "complete": False,
                "files": {},
                "status": None,
                "status_consistent": False,
                "missing_files": [
                    relative_path.format(slug=feature_filter)
                    for relative_path in FEATURE_FILE_PATHS.values()
                ],
            }
        ]

    base_features: list[FeatureAnalysis] = []
    pending_by_feature: dict[str, list[_PendingIssue]] = {}
    for feature in selected:
        analysis, pending_issues = _build_feature_analysis(resolved_root, feature)
        base_features.append(analysis)
        pending_by_feature[analysis.feature_id] = pending_issues

    assigned = _assign_issue_ids(pending_by_feature)
    features: list[FeatureAnalysis] = []
    all_issues: list[AnalysisIssue] = []
    for feature in sorted(base_features, key=lambda item: item.feature_id):
        issues = assigned.get(feature.feature_id, ())
        all_issues.extend(issues)
        features.append(
            FeatureAnalysis(
                feature_id=feature.feature_id,
                status=feature.status,
                ready=feature.ready,
                source_files=feature.source_files,
                missing_files=feature.missing_files,
                metrics=feature.metrics,
                issues=issues,
                recommended_commands=feature.recommended_commands,
            )
        )

    recommended_commands = _dedupe_commands(
        [
            command
            for issue in all_issues
            for command in ([issue.recommended_command] if issue.recommended_command else [])
        ]
        or ["specspine validate . --fusion --features --json"]
    )

    feature_tuple = tuple(features)
    issue_tuple = tuple(all_issues)
    return AnalysisReport(
        root=resolved_root,
        feature_filter=feature_filter,
        summary=_summary(
            feature_tuple,
            issue_tuple,
            discovered_features=len(discovered),
        ),
        features=feature_tuple,
        issues=issue_tuple,
        recommended_commands=recommended_commands,
    )


def render_analysis_json(report: AnalysisReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_analysis_text(report: AnalysisReport) -> str:
    summary = report.summary
    severity_counts = summary["issue_counts_by_severity"]
    assert isinstance(severity_counts, dict)
    lines = [
        "SpecSpine analysis",
        f"Root: {report.root}",
        f"Feature filter: {report.feature_filter or 'all'}",
        (
            "Summary: "
            f"features={summary['features_analyzed']} "
            f"ready={summary['features_ready']} "
            f"issues={summary['issues_total']} "
            f"critical={severity_counts.get('critical', 0)} "
            f"high={severity_counts.get('high', 0)} "
            f"medium={severity_counts.get('medium', 0)} "
            f"low={severity_counts.get('low', 0)}"
        ),
        "",
        "Issues:",
    ]

    if not report.issues:
        lines.append("- None. No consistency or coverage issues found.")
    else:
        for feature in report.features:
            if not feature.issues:
                continue
            lines.append(f"- {feature.feature_id} ({feature.status}, ready={'yes' if feature.ready else 'no'})")
            for issue in feature.issues[:TEXT_MAX_ISSUES_PER_FEATURE]:
                location = issue.source_file
                if issue.line is not None:
                    location = f"{location}:{issue.line}"
                lines.append(
                    f"  - [{issue.severity}] {issue.category}/{issue.code} "
                    f"{location} - {issue.message}"
                )
            hidden = len(feature.issues) - TEXT_MAX_ISSUES_PER_FEATURE
            if hidden > 0:
                lines.append(f"  - ... {hidden} more issue(s); use --json for the full list.")

    lines.extend(["", "Recommendations:"])
    for command in report.recommended_commands[:TEXT_MAX_RECOMMENDATIONS]:
        lines.append(f"- {command}")
    hidden_commands = len(report.recommended_commands) - TEXT_MAX_RECOMMENDATIONS
    if hidden_commands > 0:
        lines.append(
            f"- ... {hidden_commands} more recommended command(s); use --json for the full list."
        )
    if not report.issues:
        lines.append("- Analysis is clean; continue with validation or implementation handoff.")

    return "\n".join(lines) + "\n"
