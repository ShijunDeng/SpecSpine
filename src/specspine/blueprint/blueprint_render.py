from __future__ import annotations

import json


def render_blueprint_json(report) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_blueprint_text(report) -> str:
    lines = [
        f"Implementation Blueprint: {report.feature_id}",
        "",
        f"Coverage: {report.coverage_summary['modules_total']} modules, "
        f"{report.coverage_summary['functions_total']} functions, "
        f"{report.coverage_summary['data_entities_total']} entities, "
        f"{report.coverage_summary['error_paths_total']} error paths, "
        f"{report.coverage_summary['unique_ac_covered']} ACs covered",
        "",
        "Modules:",
    ]

    if report.modules:
        for module in report.modules:
            lines.append(f"  {module.module_path}")
            lines.append(f"    Responsibility: {module.responsibility}")
            if module.functions:
                lines.append("    Functions:")
                for func in module.functions:
                    params = ", ".join(func.parameters)
                    lines.append(
                        f"      {func.name}({params}) -> {func.return_type}"
                    )
            ac_str = ", ".join(module.ac_ids) if module.ac_ids else "none"
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No modules derived from acceptance criteria.")

    lines.append("Data Entities:")
    if report.data_entities:
        for entity in report.data_entities:
            attrs = ", ".join(entity.attributes) if entity.attributes else "none"
            ac_str = ", ".join(entity.ac_ids) if entity.ac_ids else "none"
            lines.append(f"  {entity.name}")
            lines.append(f"    Attributes: {attrs}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No data entities identified.")

    lines.append("Error Paths:")
    if report.error_paths:
        for ep in report.error_paths:
            ac_str = ", ".join(ep.ac_ids) if ep.ac_ids else "none"
            lines.append(f"  Condition: {ep.condition}")
            lines.append(f"    Exception: {ep.exception_type}")
            lines.append(f"    Handling: {ep.handling}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No error paths detected.")

    lines.append("Safety Notes:")
    if report.safety_notes:
        for note in report.safety_notes:
            lines.append(f"  - {note}")
    else:
        lines.append("  None.")

    return "\n".join(lines) + "\n"


__all__ = [
    "render_blueprint_json",
    "render_blueprint_text",
]
