from __future__ import annotations

from typing import Any

__all__ = [
    "_complete_marker",
    "_marker",
    "render_status_text",
]


def _marker(value: bool) -> str:
    return "ok" if value else "missing"


def _complete_marker(value: bool) -> str:
    return "complete" if value else "incomplete"


def render_status_text(status: dict[str, Any]) -> str:
    lines = [
        f"SpecSpine status at {status['root']}",
        f"Workspace: {_complete_marker(status['workspace']['complete'])}",
        f"Fusion: {_complete_marker(status['fusion']['complete'])}",
        "Artifacts:",
    ]

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

    adapters = status.get("adapters")
    if adapters is not None:
        lines.append("External adapters:")
        for key, adapter in adapters.items():
            version = f" ({adapter['version']})" if adapter["version"] else ""
            lines.append(
                f"  [{_marker(adapter['available'])}] {key}: {adapter['display_name']}{version}"
            )
            lines.append(f"      {adapter['detail']}")

    validation = status.get("validation")
    if validation is not None:
        result = "ok" if validation["ok"] else "failed"
        summary = validation["summary"]
        lines.append("Validation:")
        lines.append(f"  Result: {result}")
        lines.append(
            "  Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"warn={summary['warn']} "
            f"skip={summary['skip']} "
            f"total={summary['total']}"
        )
        failed_checks = validation.get("failed_checks", [])
        if failed_checks:
            lines.append("  Failed checks:")
            for check in failed_checks:
                lines.append(f"    - {check['id']}")
        warning_checks = validation.get("warning_checks")
        if warning_checks is not None:
            lines.append("  Warning checks:")
            if warning_checks:
                for check in warning_checks:
                    lines.append(f"    - {check['id']}")
            else:
                lines.append("    none")

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

    lines.append("Recommended next actions:")
    for recommendation in status["recommendations"]:
        lines.append(f"  - {recommendation}")

    return "\n".join(lines) + "\n"
