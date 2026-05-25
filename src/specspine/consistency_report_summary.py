from __future__ import annotations

from typing import Any

from .consistency_models import (
    FeatureConsistency,
)

__all__ = [
    "_summary",
    "render_consistency_text",
]


def _summary(features: tuple[FeatureConsistency, ...], discovered_features: int) -> dict[str, Any]:
    checks = [check for feature in features for check in feature.consistency_checks]
    return {
        "changed_references": sum(len(feature.changed_references) for feature in features),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_total": len(checks),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "discovered_features": discovered_features,
        "documentation_references": sum(
            len(feature.documentation_references) for feature in features
        ),
        "features_scanned": len(features),
        "features_with_missing_files": sum(1 for feature in features if feature.missing_files),
        "implementation_references": sum(
            len(feature.implementation_references) for feature in features
        ),
        "test_references": sum(len(feature.test_references) for feature in features),
    }


def render_consistency_text(report) -> str:
    summary = report.summary
    lines = [
        f"Spec-code consistency report: {report.root}",
        f"Feature filter: {report.feature_filter or 'all'}",
        (
            "Summary: "
            f"features={summary['features_scanned']} "
            f"impl_refs={summary['implementation_references']} "
            f"test_refs={summary['test_references']} "
            f"documentation_refs={summary['documentation_references']} "
            f"changed_refs={summary['changed_references']} "
            f"fail={summary['checks_fail']} "
            f"warn={summary['checks_warn']}"
        ),
        "",
        "Features:",
    ]
    if not report.features:
        lines.append("- none")
    for feature in report.features:
        lines.append(
            f"- {feature.feature_id}: status={feature.status or 'missing'} "
            f"sources={len(feature.source_files)} "
            f"impl={len(feature.implementation_references)} "
            f"tests={len(feature.test_references)} "
            f"docs={len(feature.documentation_references)} "
            f"changed={len(feature.changed_references)}"
        )
        for check in feature.consistency_checks:
            if check.status == "pass":
                continue
            lines.append(f"  - [{check.status}] {check.id}: {check.message}")

    lines.extend(["", "Changed files:"])
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- None provided.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
