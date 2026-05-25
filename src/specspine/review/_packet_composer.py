from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ReviewPacket

__all__ = [
    "_compose_packet",
]


def _compose_packet(
    resolved_root: Path,
    feature_slug: str | None,
    review_data: dict[str, Any],
    impact: Any,
    gates: Any,
) -> ReviewPacket:
    safety_notes = (
        "This command composes local SpecSpine reports only.",
        "Recommended commands are advisory and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ReviewPacket(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=impact.changed_files,
        validation=review_data.get("validation", {}),
        quality_gates=gates.as_dict(),
        test_impact=impact.as_dict(),
        feature=review_data.get("feature_payload"),
        review_checks=review_data["review_checks"],
        summary=review_data["summary"],
        recommended_commands=review_data["recommended_commands"],
        safety_notes=safety_notes,
    )
