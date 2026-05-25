from __future__ import annotations

import re
import textwrap
from pathlib import Path

from .features import (
    feature_bundle_paths,
    parse_test_coverage,
)
from .scaffold_models import ScaffoldCoverageLink

SLUG_TO_CLASS_RE = re.compile(r"(?:^|-)([a-z])")
AC_KEYWORD_RE = re.compile(r"(?:can|should|must|will|shall|is|are)\s+(\S+)")

__all__ = [
    "_ac_id_snake",
    "_existing_coverage_links",
    "_extract_ac_keyword",
    "_generate_test_class",
    "_generate_test_method",
    "_slug_to_camel",
    "_update_quality_file",
]


def _slug_to_camel(slug: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        return match.group(1).upper()
    result = SLUG_TO_CLASS_RE.sub(_repl, slug)
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result


def _ac_id_snake(ac_id: str) -> str:
    return ac_id.lower()


def _extract_ac_keyword(ac_text: str) -> str:
    match = AC_KEYWORD_RE.search(ac_text)
    if match:
        return match.group(1).lower()
    words = ac_text.strip().split()
    if words:
        return words[0].lower()
    return "behavior"


def _generate_test_method(ac_id: str, ac_text: str, slug: str) -> dict[str, str]:
    camel = _slug_to_camel(slug)
    snake = _ac_id_snake(ac_id)
    keyword = _extract_ac_keyword(ac_text)
    method_name = f"test_{snake}_{keyword}"
    docstring = ac_text.strip()
    body = 'self.fail("TODO: implement")'
    return {
        "method_name": method_name,
        "docstring": docstring,
        "body": body,
    }


def _generate_test_class(slug: str, methods: list[dict[str, str]]) -> str:
    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    lines = [
        '"""Auto-generated test scaffold for feature: {slug}."""',
        "import unittest",
        "",
        "",
        f"class {class_name}(unittest.TestCase):",
    ]
    if not methods:
        lines.append('    """No acceptance criteria found to scaffold."""')
        lines.append("")
        lines.append("    def test_no_criteria(self) -> None:")
        lines.append('        self.fail("TODO: add acceptance criteria to the feature spec")')
    else:
        for i, method in enumerate(methods):
            if i > 0:
                lines.append("")
            method_name = method["method_name"]
            docstring = method["docstring"]
            body = method["body"]
            lines.append(f'    def {method_name}(self) -> None:')
            lines.append(f'        """{docstring}."""')
            lines.append(f"        {body}")
    lines.append("")
    return "\n".join(lines)


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
