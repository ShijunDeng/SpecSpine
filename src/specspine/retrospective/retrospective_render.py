from __future__ import annotations

import json


def render_retrospective_json(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_retrospective_text(report: dict[str, object]) -> str:
    summary = report["summary"]  # type: ignore[index]
    lines = [
        f"Retrospective report: {report['root']}",
        f"Feature filter: {report['feature_filter'] or 'all'}",
        (
            "Summary: "
            f"features={summary['features_total']} "
            f"ready={summary['features_ready']} "
            f"not_ready={summary['features_not_ready']} "
            f"open_tasks={summary['open_tasks']} "
            f"blocking={summary['blocking_checks']} "
            f"gaps={summary['gap_count']}"
        ),
        "",
        "Recommendations:",
    ]
    recommendations = report["recommendations"]  # type: ignore[index]
    if recommendations:
        for row in recommendations:  # type: ignore[union-attr]
            lines.append(
                f"- {row['rank']}. {row['feature_id']} ({row['status']}): {row['reason']}"
            )
    else:
        lines.append("- None.")

    missing_feature = summary.get("missing_feature")
    if missing_feature:
        lines.extend(["", f"Missing feature bundle: {missing_feature}"])

    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report["safety_notes"])  # type: ignore[index]
    return "\n".join(lines) + "\n"


__all__ = [
    "render_retrospective_json",
    "render_retrospective_text",
]
