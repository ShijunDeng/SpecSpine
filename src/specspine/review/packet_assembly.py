from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ReviewPacket
from .helpers import _dedupe_commands
from .feature_evidence import _feature_payload
from .review_checks import _build_review_checks, _build_feature_commands

__all__ = [
    "assemble_review_packet",
]


def assemble_review_packet(
    resolved_root: Path,
    feature_slug: str | None,
    validation: dict[str, Any],
    gates: Any,
    impact: Any,
    feature_payload: dict[str, Any] | None,
) -> ReviewPacket:
    review_checks = _build_review_checks(
        validation_ok=validation["ok"],
        gates_source_missing=gates.source_missing,
        has_impact_recommendations=bool(impact.recommendations),
        feature_payload=feature_payload,
    )
    failed_checks = tuple(
        check["id"] for check in review_checks if check["status"] != "pass"
    )
    feature_commands = _build_feature_commands(feature_slug)

    recommended_commands = _dedupe_commands(
        impact.recommended_commands,
        gates.recommended_commands,
        (
            "specspine review packet . --json",
            "specspine validate . --fusion --features",
        ),
        feature_commands,
    )
    summary = {
        "changed_files": len(impact.changed_files),
        "failed_review_checks": len(failed_checks),
        "feature_included": feature_slug is not None,
        "passed_review_checks": len(review_checks) - len(failed_checks),
        "recommended_commands": len(recommended_commands),
        "review_checks": len(review_checks),
        "test_impact_recommendations": len(impact.recommendations),
        "validation_ok": bool(validation["ok"]),
    }
    safety_notes = (
        "This command composes local SpecSpine reports only.",
        "Recommended commands are advisory and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ReviewPacket(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=impact.changed_files,
        validation=validation,
        quality_gates=gates.as_dict(),
        test_impact=impact.as_dict(),
        feature=feature_payload,
        review_checks=review_checks,
        summary=summary,
        recommended_commands=recommended_commands,
        safety_notes=safety_notes,
    )
