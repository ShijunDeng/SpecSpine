from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_trace_report,
    feature_bundle_paths,
    parse_test_coverage,
    validate_feature_slug,
)

SLUG_TO_CLASS_RE = re.compile(r"(?:^|-)([a-z])")
AC_KEYWORD_RE = re.compile(r"(?:can|should|must|will|shall|is|are)\s+(\S+)")


@dataclass(frozen=True)
class ScaffoldTestMethod:
    method_name: str
    docstring: str
    ac_id: str
    ac_text: str
    body: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "ac_text": self.ac_text,
            "body": self.body,
            "docstring": self.docstring,
            "method_name": self.method_name,
        }


@dataclass(frozen=True)
class ScaffoldCoverageLink:
    ac_id: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class ScaffoldSkippedCriterion:
    ac_id: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ScaffoldRemediationStep:
    ac_id: str
    action: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "action": self.action,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class ScaffoldReport:
    feature_id: str
    status: str
    scaffold_file: str
    test_methods: tuple[ScaffoldTestMethod, ...]
    coverage_links: tuple[ScaffoldCoverageLink, ...]
    skipped_criteria: tuple[ScaffoldSkippedCriterion, ...]
    remediation_plan: tuple[ScaffoldRemediationStep, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "coverage_links": [link.as_dict() for link in self.coverage_links],
            "feature_id": self.feature_id,
            "remediation_plan": [step.as_dict() for step in self.remediation_plan],
            "safety_notes": list(self.safety_notes),
            "scaffold_file": self.scaffold_file,
            "skipped_criteria": [item.as_dict() for item in self.skipped_criteria],
            "status": self.status,
            "test_methods": [method.as_dict() for method in self.test_methods],
        }


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


def _build_remediation_plan(
    slug: str,
    uncovered_acs: list[dict[str, str]],
    test_path: str,
    class_name: str,
) -> list[ScaffoldRemediationStep]:
    steps: list[ScaffoldRemediationStep] = []
    for ac in uncovered_acs:
        method_info = _generate_test_method(ac["ac_id"], ac["ac_text"], slug)
        steps.append(
            ScaffoldRemediationStep(
                ac_id=ac["ac_id"],
                action=f"Implement {method_info['method_name']} in {test_path}",
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
    return steps


def build_ac_test_scaffold(root: Path, slug: str) -> ScaffoldReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    trace_report = build_feature_trace_report(resolved_root, slug)
    acceptance_criteria = trace_report.acceptance_criteria
    status = trace_report.status
    covered_acs = _existing_coverage_links(resolved_root, slug)
    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    test_filename = f"test_{slug.replace('-', '_')}_scaffold.py"
    test_path = f"tests/{test_filename}"

    methods: list[dict[str, str]] = []
    coverage_links: list[ScaffoldCoverageLink] = []
    skipped_criteria: list[ScaffoldSkippedCriterion] = []
    uncovered_acs: list[dict[str, str]] = []

    for criterion in acceptance_criteria:
        if criterion.id in covered_acs:
            skipped_criteria.append(
                ScaffoldSkippedCriterion(
                    ac_id=criterion.id,
                    reason="Already has completed test coverage link",
                )
            )
            continue
        method_info = _generate_test_method(criterion.id, criterion.text, slug)
        methods.append(method_info)
        coverage_links.append(
            ScaffoldCoverageLink(
                ac_id=criterion.id,
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
        uncovered_acs.append({"ac_id": criterion.id, "ac_text": criterion.text})

    scaffold_source = _generate_test_class(slug, methods)
    remediation = _build_remediation_plan(slug, uncovered_acs, test_path, class_name)

    safety_notes: tuple[str, ...] = (
        "Scaffold generation is read-only; no subprocess or network calls made.",
        "Generated test methods contain self.fail() placeholders only.",
        "Review and implement each test method before running the scaffold file.",
    )

    return ScaffoldReport(
        feature_id=slug,
        status=status,
        scaffold_file=test_path,
        test_methods=tuple(
            ScaffoldTestMethod(
                method_name=m["method_name"],
                docstring=m["docstring"],
                ac_id=uncovered_acs[i]["ac_id"],
                ac_text=uncovered_acs[i]["ac_text"],
                body=m["body"],
            )
            for i, m in enumerate(methods)
        ),
        coverage_links=tuple(coverage_links),
        skipped_criteria=tuple(skipped_criteria),
        remediation_plan=tuple(remediation),
        safety_notes=safety_notes,
    )


def render_scaffold_json(result: ScaffoldReport) -> str:
    return json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"


def render_scaffold_text(result: ScaffoldReport) -> str:
    lines = [
        f"Scaffold: {result.feature_id}",
        f"Status: {result.status}",
        f"Target: {result.scaffold_file}",
        "",
        f"Test methods: {len(result.test_methods)}",
        f"Coverage links: {len(result.coverage_links)}",
        f"Skipped: {len(result.skipped_criteria)}",
        "",
    ]
    if result.test_methods:
        lines.append("Methods:")
        for method in result.test_methods:
            lines.append(f"  - {method.method_name}: {method.docstring}")
        lines.append("")
    if result.skipped_criteria:
        lines.append("Skipped (already covered):")
        for item in result.skipped_criteria:
            lines.append(f"  - {item.ac_id}: {item.reason}")
        lines.append("")
    if result.remediation_plan:
        lines.append("Remediation:")
        for step in result.remediation_plan:
            lines.append(f"  - {step.ac_id}: {step.action}")
        lines.append("")
    lines.extend(f"Note: {note}" for note in result.safety_notes)
    return "\n".join(lines) + "\n"
