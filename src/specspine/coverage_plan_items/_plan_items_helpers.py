from __future__ import annotations

from typing import Any

__all__ = [
    "_coverage_plan_safety_notes",
    "_candidate_test_files",
    "_suggested_quality_links",
    "_risk_note",
]


def _coverage_plan_safety_notes() -> list[str]:
    return [
        "Coverage plan is read-only and advisory.",
        "Coverage gaps are signals for reviewer follow-up, not proof of test quality.",
        "The command does not write quality files or run tests.",
        "The command does not invoke subprocesses, network services, upstream tools, GitHub APIs, or token providers.",
    ]


def _candidate_test_files(slug: str, record: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for link in record.get("test_coverage_links", []):
        if not isinstance(link, dict):
            continue
        target_path = str(link.get("target_path") or "")
        if target_path and target_path not in candidates:
            candidates.append(target_path)
    suggested = f"tests/test_{slug.replace('-', '_')}.py"
    if suggested not in candidates:
        candidates.append(suggested)
    return candidates


def _suggested_quality_links(missing_criteria: list[dict[str, Any]]) -> list[str]:
    links: list[str] = []
    for criterion in missing_criteria:
        links.append(f"- [ ] {criterion['id']} -> tests/...")
    return links


def _risk_note(record: dict[str, Any]) -> str:
    notes: list[str] = []
    if record.get("missing_target_link_ids"):
        notes.append("checked coverage links point at missing local targets")
    if record.get("open_coverage_link_ids"):
        notes.append("open coverage links are not counted as coverage")
    if record.get("unknown_acceptance_criterion_link_ids"):
        notes.append("some coverage links reference unknown acceptance criteria")
    if record.get("missing_files"):
        notes.append("the feature bundle is partial")
    if not notes:
        notes.append("acceptance criteria lack checked local Test Coverage links")
    return "; ".join(notes) + "."
