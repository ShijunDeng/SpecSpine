from __future__ import annotations

from typing import Any

__all__ = [
    "_render_text_feature_summaries",
    "_render_text_readiness_summary",
    "_render_text_recommendations",
]


def _render_text_feature_summaries(status: dict[str, Any], lines: list[str]) -> None:
    feature_summaries = status.get("feature_summaries")
    if feature_summaries is not None:
        lines.append("Feature summaries:")
        if feature_summaries:
            for summary in feature_summaries:
                tasks = summary["tasks_summary"]
                next_actions = summary.get("next_actions", [])
                first_action = next_actions[0] if next_actions else "None."
                coverage_marker = (
                    "coverage=yes "
                    if summary.get("coverage_required")
                    else ""
                )
                lines.append(
                    "  "
                    f"{summary['slug']} - "
                    f"status={summary['status']} "
                    f"priority={summary['priority']} "
                    f"owner={summary['owner']} "
                    f"milestone={summary['milestone']} "
                    f"target_release={summary['target_release']} "
                    f"ready={'yes' if summary['ready'] else 'no'} "
                    f"{coverage_marker}"
                    f"tasks={tasks['done']}/{tasks['open']} "
                    f"gaps={summary['gaps']} "
                    f"blocking={summary['blocking_checks']}"
                )
                lines.append(f"    next: {first_action}")
        else:
            lines.append("  none")


def _render_text_readiness_summary(status: dict[str, Any], lines: list[str]) -> None:
    readiness_summary = status.get("readiness_summary")
    if readiness_summary is not None:
        lines.append("Readiness summary:")
        lines.append(
            "  "
            f"features={readiness_summary['features_total']} "
            f"ready={readiness_summary['ready']} "
            f"not_ready={readiness_summary['not_ready']} "
            f"blocking={readiness_summary['blocking_checks_total']} "
            f"gaps={readiness_summary['gaps_total']} "
            f"coverage_required={readiness_summary['coverage_required_total']}"
        )
        not_ready = [
            feature
            for feature in readiness_summary["features"]
            if not feature["ready"]
        ]
        if not_ready:
            lines.append("  Not-ready features:")
            for feature in not_ready:
                commands = feature.get("recommended_commands", [])
                command = commands[0] if commands else f"specspine feature ready {feature['feature_id']} . --json"
                lines.append(
                    "    "
                    f"- {feature['feature_id']} "
                    f"status={feature['status']} "
                    f"blocking={feature['blocking_checks']} "
                    f"gaps={feature['gaps']} "
                    f"missing={len(feature['missing_files'])}"
                )
                lines.append(f"      command: {command}")


def _render_text_recommendations(status: dict[str, Any], lines: list[str]) -> None:
    lines.append("Recommended next actions:")
    for recommendation in status["recommendations"]:
        lines.append(f"  - {recommendation}")
