from __future__ import annotations

from .feature_bundle import (
    FeatureMetadata,
    _render_metadata_lines,
)

__all__ = [
    "_render_pr_header_lines",
]


def _render_pr_header_lines(
    *,
    feature_id: str,
    status: str,
    ready: bool,
    summary: dict[str, object],
    why: str,
    metadata: FeatureMetadata,
) -> list[str]:
    trace = summary["trace"]
    ready_summary = summary["ready"]
    task_summary = summary["tasks"]
    lines = [
        "## Summary",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        f"- Ready: {'yes' if ready else 'no'}",
        (
            "- Trace: "
            f"total={trace['total']} "
            f"done={trace['done']} "
            f"open={trace['open']}"
        ),
        (
            "- Tasks: "
            f"total={task_summary['total']} "
            f"done={task_summary['done']} "
            f"open={task_summary['open']}"
        ),
        (
            "- Readiness: "
            f"pass={ready_summary['pass']} "
            f"fail={ready_summary['fail']} "
            f"total={ready_summary['total']}"
        ),
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
        "## Feature",
        "",
        "- This is an offline Pull Request draft generated from local SpecSpine feature artifacts.",
        "- No remote PR is created by this command.",
        "",
        "## Why",
        "",
        why,
        "",
    ]
    return lines
