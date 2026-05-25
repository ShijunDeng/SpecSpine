from __future__ import annotations

__all__ = [
    "render_consistency_text",
]


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
