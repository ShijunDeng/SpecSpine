from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    build_feature_handoff_report,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
    validate_feature_slug,
)
from .gates import build_quality_gate_report
from .impact import build_test_impact_report
from .validation import build_validation_report, build_validation_summary


@dataclass(frozen=True)
class ReviewPacket:
    root: Path
    feature_id: str | None
    changed_files: tuple[str, ...]
    validation: dict[str, Any]
    quality_gates: dict[str, Any]
    test_impact: dict[str, Any]
    review_checks: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]
    feature: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "changed_files": list(self.changed_files),
            "feature_id": self.feature_id,
            "quality_gates": dict(self.quality_gates),
            "recommended_commands": list(self.recommended_commands),
            "review_checks": [dict(check) for check in self.review_checks],
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "test_impact": dict(self.test_impact),
            "validation": dict(self.validation),
        }
        if self.feature is not None:
            payload["feature"] = dict(self.feature)
        return payload


def _dedupe_commands(*command_groups: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = []
    seen: set[str] = set()
    for group in command_groups:
        for command in group:
            if command not in seen:
                commands.append(command)
                seen.add(command)
    return tuple(commands)


def _review_check(check_id: str, passed: bool, message: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "message": message,
        "status": "pass" if passed else "fail",
    }


def _feature_payload(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    tests = build_feature_tests_report(root, slug)
    trace = build_feature_trace_report(root, slug) if handoff.has_native_files else None
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "gaps": list(trace.gaps if trace is not None else handoff.gaps),
        "handoff": handoff.as_dict(),
        "has_native_files": handoff.has_native_files,
        "ready": ready.as_dict(),
        "source_files": list(tests.source_files),
        "status": handoff.status,
        "tests": tests.as_dict(),
        "trace": trace.as_dict() if trace is not None else None,
    }


def build_review_packet(
    root: Path,
    *,
    feature: str | None = None,
    changed_files: tuple[str, ...] = (),
) -> ReviewPacket:
    resolved_root = root.expanduser().resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None

    validation_report = build_validation_report(
        resolved_root,
        include_fusion=True,
        include_features=True,
    )
    validation = build_validation_summary(
        validation_report,
        included={
            "workspace": True,
            "fusion": True,
            "features": True,
            "adapters": False,
        },
    )
    gates = build_quality_gate_report(resolved_root)
    impact = build_test_impact_report(
        resolved_root,
        changed_files=changed_files,
        feature=feature_slug,
    )

    feature_payload = _feature_payload(resolved_root, feature_slug) if feature_slug else None
    checks = [
        _review_check(
            "review.validation",
            bool(validation["ok"]),
            "Workspace validation passes.",
        ),
        _review_check(
            "review.quality_gates_source",
            not gates.source_missing,
            "Quality gate source file exists.",
        ),
        _review_check(
            "review.test_impact",
            bool(impact.recommendations),
            "Test impact recommendations are available.",
        ),
    ]
    if feature_payload is not None:
        checks.extend(
            [
                _review_check(
                    "review.feature_exists",
                    bool(feature_payload["has_native_files"]),
                    "Native feature evidence exists.",
                ),
                _review_check(
                    "review.feature_ready",
                    bool(feature_payload["ready"]["ready"]),
                    "Feature readiness passes with coverage required.",
                ),
                _review_check(
                    "review.trace_gaps",
                    not bool(feature_payload["gaps"]),
                    "Feature trace has no gaps.",
                ),
                _review_check(
                    "review.blocking_checks",
                    not bool(feature_payload["blocking_checks"]),
                    "Feature has no blocking readiness checks.",
                ),
            ]
        )

    review_checks = tuple(checks)
    failed_checks = tuple(
        check["id"] for check in review_checks if check["status"] != "pass"
    )
    feature_commands: tuple[str, ...] = ()
    if feature_slug is not None:
        feature_commands = (
            f"specspine review packet . --feature {feature_slug} --json",
            f"specspine feature handoff {feature_slug} . --json",
            f"specspine feature ready {feature_slug} . --json --require-coverage",
            f"specspine feature trace {feature_slug} . --json",
            f"specspine feature tests {feature_slug} . --json",
        )

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
