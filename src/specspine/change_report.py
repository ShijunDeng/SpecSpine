from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .change_classifiers import (
    _classify_changed_file,
    _dedupe,
    _feature_slug_from_path,
    _normalise_changed_file,
)
from .change_models import RISK_BY_CATEGORY, ChangeRiskReport
from .features import (
    build_feature_handoff_report,
    build_feature_ready_report,
    validate_feature_slug,
)


def _feature_evidence(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "feature_id": slug,
        "gaps": [dict(gap) for gap in ready.gaps],
        "has_native_files": handoff.has_native_files,
        "missing_files": list(ready.missing_files),
        "ready": ready.ready,
        "source_files": [
            str(source["path"])
            for source in handoff.sources.values()
            if source.get("exists")
        ],
        "status": ready.status,
    }


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


def build_change_risk_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> ChangeRiskReport:
    resolved_root = root.resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None
    normalised_changed_files = _dedupe(
        [_normalise_changed_file(resolved_root, path) for path in changed_files]
    )

    files: list[dict[str, Any]] = []
    inferred_features: list[str] = []
    risk_counts = {"high": 0, "low": 0, "medium": 0}
    categories: dict[str, int] = {}
    for path in normalised_changed_files:
        category = _classify_changed_file(path)
        risk = RISK_BY_CATEGORY[category]
        files.append({"category": category, "path": path, "risk": risk})
        risk_counts[risk] += 1
        categories[category] = categories.get(category, 0) + 1
        inferred = _feature_slug_from_path(path)
        if inferred is not None:
            inferred_features.append(inferred)

    feature_ids = _dedupe(
        tuple([slug for slug in inferred_features] + ([feature_slug] if feature_slug else []))
    )
    evidence = tuple(_feature_evidence(resolved_root, slug) for slug in feature_ids)
    summary = {
        "categories": dict(sorted(categories.items())),
        "changed_files": len(normalised_changed_files),
        "feature_ids": list(feature_ids),
        "high": risk_counts["high"],
        "low": risk_counts["low"],
        "medium": risk_counts["medium"],
    }
    safety_notes = (
        "This report is advisory only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ChangeRiskReport(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=normalised_changed_files,
        files=tuple(files),
        feature_evidence=evidence,
        summary=summary,
        recommended_commands=_recommended_commands(normalised_changed_files, feature_ids),
        safety_notes=safety_notes,
    )


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


__all__ = [
    "build_change_risk_report",
    "render_change_risk_json",
    "render_change_risk_text",
]
