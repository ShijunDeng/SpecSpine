from __future__ import annotations

import re
from pathlib import Path

from .features import (
    feature_bundle_paths,
    parse_test_coverage,
)
from .scaffold_models import ScaffoldCoverageLink

__all__ = [
    "_existing_coverage_links",
    "_update_quality_file",
]


def _existing_coverage_links(root: Path, slug: str) -> set[str]:
    quality_path = feature_bundle_paths(root, slug)["quality"]
    covered: set[str] = set()
    if not quality_path.exists():
        return covered
    coverage = parse_test_coverage(
        quality_path.read_text(encoding="utf-8"),
        source_file=str(quality_path),
        root=root,
    )
    for link in coverage:
        if link.done and link.target_exists:
            covered.add(link.acceptance_criterion_id)
    return covered


def _update_quality_file(root: Path, slug: str, new_links: list[dict[str, str]]) -> bool:
    if not new_links:
        return False
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return False
    content = quality_path.read_text(encoding="utf-8")
    section_marker = "## Test Coverage"
    if section_marker not in content:
        return False
    lines_to_add = []
    for link in new_links:
        ac_id = link["ac_id"]
        target_path = link["target_path"]
        lines_to_add.append(f"- [ ] {ac_id} -> {target_path}")
    section_lines = "\n".join(lines_to_add)
    updated = content.replace(
        section_marker,
        f"{section_marker}\n\n{section_lines}",
        1,
    )
    if updated == content:
        existing_section = content.split(section_marker, 1)[1]
        next_heading_match = re.search(r"\n## ", existing_section)
        if next_heading_match:
            insert_point = content.index(section_marker) + len(section_marker) + next_heading_match.start()
            updated = content[:insert_point] + "\n\n" + section_lines + content[insert_point:]
        else:
            updated = content + "\n\n" + section_lines + "\n"
    quality_path.write_text(updated, encoding="utf-8")
    return True
