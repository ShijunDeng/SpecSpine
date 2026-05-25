from __future__ import annotations

import json

from .scaffold_models import (
    ScaffoldReport,
)

__all__ = [
    "render_scaffold_json",
    "render_scaffold_text",
]


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
