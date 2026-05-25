from __future__ import annotations

__all__ = [
    "_archive_safety_notes",
    "_archive_recommended_commands",
]


def _archive_safety_notes(coverage_required: bool) -> tuple[str, ...]:
    notes = [
        (
            "This command only reads local SpecSpine feature artifacts unless "
            "--output-dir is provided."
        ),
        (
            "When --output-dir is provided, this command writes only the "
            "explicit output directory and does not mark the feature archived."
        ),
        (
            "The archive package preserves local evidence for review; use the "
            "recommended lifecycle command separately after reviewing readiness."
        ),
        (
            "SpecSpine did not run tests, invoke subprocesses, call network "
            "services, invoke upstream CLIs, call GitHub APIs, or read tokens."
        ),
    ]
    if coverage_required:
        notes.append(
            "A local Test Coverage section was present, so archive readiness "
            "uses the same coverage gate as feature ready --require-coverage."
        )
    return tuple(notes)


def _archive_recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature ready {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature status {slug} . --set archived --enforce-transition --json",
        "specspine validate . --fusion --features --json",
    )
