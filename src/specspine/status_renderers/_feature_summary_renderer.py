from __future__ import annotations

from typing import Any

__all__ = [
    "_render_text_feature_summaries",
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
