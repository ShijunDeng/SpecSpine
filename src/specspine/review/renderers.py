from __future__ import annotations

import json

from .models import ReviewPacket

__all__ = [
    "render_review_packet_json",
    "render_review_packet_text",
]


def render_review_packet_json(packet: ReviewPacket) -> str:
    return json.dumps(packet.as_dict(), indent=2, sort_keys=True) + "\n"


def render_review_packet_text(packet: ReviewPacket) -> str:
    summary = packet.summary
    lines = [
        f"Review packet: {packet.root}",
        f"Feature: {packet.feature_id or 'workspace'}",
        (
            "Summary: "
            f"checks={summary['review_checks']} "
            f"passed={summary['passed_review_checks']} "
            f"failed={summary['failed_review_checks']} "
            f"changed_files={summary['changed_files']} "
            f"impact_recommendations={summary['test_impact_recommendations']}"
        ),
        "",
        "Review checks:",
    ]
    lines.extend(
        f"- [{check['status']}] {check['id']}: {check['message']}"
        for check in packet.review_checks
    )
    lines.extend(["", "Changed files:"])
    if packet.changed_files:
        lines.extend(f"- {path}" for path in packet.changed_files)
    else:
        lines.append("- None provided.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in packet.recommended_commands)

    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in packet.safety_notes)
    return "\n".join(lines) + "\n"
