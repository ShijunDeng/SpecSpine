from __future__ import annotations

from typing import Any

from .text_markers import _complete_marker, _marker

__all__ = [
    "_render_text_header",
]


def _render_text_header(status: dict[str, Any], lines: list[str]) -> None:
    lines.append(f"SpecSpine status at {status['root']}")
    lines.append(f"Workspace: {_complete_marker(status['workspace']['complete'])}")
    lines.append(f"Fusion: {_complete_marker(status['fusion']['complete'])}")
    lines.append("Artifacts:")

    for relative_path, artifact in status["artifacts"].items():
        lines.append(f"  [{_marker(artifact['exists'])}] {relative_path}")

    lines.append("Features:")
    if status["features"]:
        for feature in status["features"]:
            marker = "complete" if feature["complete"] else "incomplete"
            lifecycle = feature.get("status") or "unknown"
            consistency = "consistent" if feature.get("status_consistent") else "mixed"
            lines.append(
                f"  [{marker}] {feature['slug']} - {lifecycle} ({consistency})"
            )
    else:
        lines.append("  none")

    lines.append("Enabled upstreams:")
    enabled = [
        (key, upstream)
        for key, upstream in status["upstreams"].items()
        if upstream["enabled"]
    ]
    if enabled:
        for key, upstream in enabled:
            marker = _marker(upstream["config_exists"])
            lines.append(f"  [{marker}] {key}: {upstream['config']}")
    else:
        lines.append("  none")
