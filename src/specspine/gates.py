from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


QUALITY_GATE_SOURCE_FILE = "quality/checklist.md"
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(.+?)\s*$")


@dataclass(frozen=True)
class RequiredGate:
    id: str
    text: str
    done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class DefinitionOfDoneItem:
    id: str
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class QualityGateReport:
    root: Path
    source_file: str
    source_missing: bool
    required_checks: tuple[RequiredGate, ...]
    definition_of_done: tuple[DefinitionOfDoneItem, ...]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        required_done = sum(1 for gate in self.required_checks if gate.done)
        required_total = len(self.required_checks)
        return {
            "definition_total": len(self.definition_of_done),
            "required_done": required_done,
            "required_open": required_total - required_done,
            "required_total": required_total,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "definition_of_done": [
                item.as_dict() for item in self.definition_of_done
            ],
            "recommended_commands": list(self.recommended_commands),
            "required_checks": [gate.as_dict() for gate in self.required_checks],
            "root": str(self.root),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "summary": self.summary,
        }


def _markdown_heading(raw_line: str) -> tuple[int, str] | None:
    stripped = raw_line.strip()
    if not stripped.startswith("#"):
        return None

    marks = len(stripped) - len(stripped.lstrip("#"))
    if marks == 0 or marks > 6:
        return None

    if len(stripped) == marks or stripped[marks] != " ":
        return None

    return marks, stripped[marks:].strip()


def _extract_markdown_section_lines(content: str, heading: str) -> list[tuple[int, str]]:
    lines = content.splitlines()
    section_start: int | None = None
    section_level: int | None = None

    for index, raw_line in enumerate(lines):
        parsed = _markdown_heading(raw_line)
        if parsed is None:
            continue

        level, text = parsed
        if section_start is None:
            if level == 2 and text.lower() == heading.lower():
                section_start = index + 1
                section_level = level
            continue

        if section_level is not None and level <= section_level:
            return [
                (line_number, line)
                for line_number, line in enumerate(
                    lines[section_start:index],
                    start=section_start + 1,
                )
            ]

    if section_start is None:
        return []

    return [
        (line_number, line)
        for line_number, line in enumerate(
            lines[section_start:],
            start=section_start + 1,
        )
    ]


def parse_required_checks(
    content: str,
    *,
    source_file: str = QUALITY_GATE_SOURCE_FILE,
) -> tuple[RequiredGate, ...]:
    checks: list[RequiredGate] = []

    for line_number, raw_line in _extract_markdown_section_lines(
        content,
        "Required Checks",
    ):
        match = CHECKBOX_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        checks.append(
            RequiredGate(
                id=f"GATE{len(checks) + 1:03d}",
                text=text.strip(),
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(checks)


def parse_definition_of_done(
    content: str,
    *,
    source_file: str = QUALITY_GATE_SOURCE_FILE,
) -> tuple[DefinitionOfDoneItem, ...]:
    items: list[DefinitionOfDoneItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(
        content,
        "Definition Of Done",
    ):
        match = BULLET_RE.match(raw_line)
        if match is None:
            continue

        text = match.group(1).strip()
        if not text:
            continue

        items.append(
            DefinitionOfDoneItem(
                id=f"DOD{len(items) + 1:03d}",
                text=text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)


def _recommended_commands() -> tuple[str, ...]:
    return (
        "specspine gates . --json",
        "specspine validate . --fusion --features",
        "specspine status . --json --validate",
        "python3 -m unittest discover -s tests",
    )


def build_quality_gate_report(root: Path) -> QualityGateReport:
    resolved_root = root.expanduser().resolve()
    source_path = resolved_root / QUALITY_GATE_SOURCE_FILE

    if not source_path.exists():
        return QualityGateReport(
            root=resolved_root,
            source_file=QUALITY_GATE_SOURCE_FILE,
            source_missing=True,
            required_checks=(),
            definition_of_done=(),
            recommended_commands=_recommended_commands(),
        )

    content = source_path.read_text(encoding="utf-8")
    return QualityGateReport(
        root=resolved_root,
        source_file=QUALITY_GATE_SOURCE_FILE,
        source_missing=False,
        required_checks=parse_required_checks(content),
        definition_of_done=parse_definition_of_done(content),
        recommended_commands=_recommended_commands(),
    )


def render_quality_gate_json(report: QualityGateReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_quality_gate_text(report: QualityGateReport) -> str:
    summary = report.summary
    lines = [
        f"Quality gates: {report.root}",
        f"Source: {report.source_file}",
    ]
    if report.source_missing:
        lines.append("Source missing: yes")
    else:
        lines.append("Source missing: no")

    lines.extend(
        [
            (
                "Summary: "
                f"required={summary['required_total']} "
                f"done={summary['required_done']} "
                f"open={summary['required_open']} "
                f"definition={summary['definition_total']}"
            ),
            "",
            "Required Checks:",
        ]
    )

    if report.required_checks:
        for gate in report.required_checks:
            marker = "x" if gate.done else " "
            lines.append(
                f"- [{marker}] {gate.id} {gate.source_file}:{gate.line} {gate.text}"
            )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Required Checks.")

    lines.extend(["", "Definition Of Done:"])
    if report.definition_of_done:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.definition_of_done
        )
    elif report.source_missing:
        lines.append("- None found because quality/checklist.md is missing.")
    else:
        lines.append("- None found under ## Definition Of Done.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
