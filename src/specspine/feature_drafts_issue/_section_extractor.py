from __future__ import annotations

from ..feature_bundle import (
    _first_line_h1,
    _first_scalar,
    _section_or_placeholder,
    _why_or_placeholder,
    feature_title,
)


def extract_draft_sections(
    contents: dict[str, str],
    relative_paths: dict[str, str],
    slug: str,
) -> tuple[str, str, str, str, str, str]:
    spec_content = contents.get("spec", "")
    title = _first_line_h1(spec_content) or feature_title(slug)
    status = _first_scalar(contents, "Status") or "TODO: Confirm feature status."
    why = _why_or_placeholder(contents, relative_path=relative_paths["spec"])
    acceptance_criteria = _section_or_placeholder(
        contents,
        kind="spec",
        heading="Acceptance Criteria",
        relative_path=relative_paths["spec"],
    )
    tasks = _section_or_placeholder(
        contents,
        kind="execution",
        heading="Tasks",
        relative_path=relative_paths["execution"],
    )
    test_plan = _section_or_placeholder(
        contents,
        kind="quality",
        heading="Test Plan",
        relative_path=relative_paths["quality"],
    )
    return title, status, why, acceptance_criteria, tasks, test_plan


__all__ = [
    "extract_draft_sections",
]
