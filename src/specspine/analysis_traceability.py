from __future__ import annotations

import re
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
)
from .analysis_models import (
    AC_REFERENCE_RE,
    QUALITY_REFERENCE_RE,
    TEST_TARGET_RE,
    VAGUE_TERMS,
    _PendingIssue,
)

__all__ = [
    "_readiness_issues",
    "_ac_traceability_issues",
    "_task_traceability_issues",
    "_criterion_quality_issues",
    "_normalize_ac_id",
    "_referenced_ac_ids",
    "_source_files",
    "_missing_files",
    "_read_test_coverage",
    "_coverage_ac_id",
    "_ready_check_severity",
    "_ready_check_category",
    "_trace_gap_issues",
    "_normalized_criterion_text",
    "_feature_trace_command",
    "_feature_ready_command",
    "_feature_tests_command",
]


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
    from .features import feature_bundle_paths, parse_test_coverage
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
