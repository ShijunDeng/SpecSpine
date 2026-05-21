from __future__ import annotations

import json


def render_impact_json(analysis) -> str:
    return json.dumps(analysis.as_dict(), indent=2, sort_keys=True) + "\n"


def render_impact_text(analysis) -> str:
    lines: list[str] = []
    lines.append(f"Feature impact analysis: {analysis.feature_id}")
    lines.append(f"Risk score: {analysis.risk_score}/100")
    lines.append(f"Total affected items: {analysis.total_affected}")
    lines.append("")

    lines.append(f"Impacted features ({len(analysis.impacted_features)}):")
    if analysis.impacted_features:
        for item in analysis.impacted_features:
            lines.append(f"  - [{item.severity}] {item.id}: {item.reason}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Impacted tests ({len(analysis.impacted_tests)}):")
    if analysis.impacted_tests:
        for item in analysis.impacted_tests:
            ac_info = ""
            if item.affected_acs:
                ac_info = f" (ACs: {', '.join(item.affected_acs)})"
            lines.append(f"  - [{item.severity}] {item.path}: {item.reason}{ac_info}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Impacted code ({len(analysis.impacted_code)}):")
    if analysis.impacted_code:
        for item in analysis.impacted_code:
            lines.append(f"  - [{item.severity}] {item.path}: {item.reason}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append("Mitigation steps:")
    for step in analysis.mitigation_steps:
        lines.append(f"  - {step}")
    lines.append("")

    lines.append("Recommended commands:")
    for cmd in analysis.recommended_commands:
        lines.append(f"  - {cmd}")
    lines.append("")

    lines.append("Safety notes:")
    for note in analysis.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"


__all__ = [
    "render_impact_json",
    "render_impact_text",
]
