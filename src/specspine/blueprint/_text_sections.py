from __future__ import annotations

__all__ = [
    "_render_entities_section",
    "_render_error_paths_section",
    "_render_safety_notes_section",
]


def _render_entities_section(data_entities) -> list[str]:
    lines = ["Data Entities:"]
    if data_entities:
        for entity in data_entities:
            attrs = ", ".join(entity.attributes) if entity.attributes else "none"
            ac_str = ", ".join(entity.ac_ids) if entity.ac_ids else "none"
            lines.append(f"  {entity.name}")
            lines.append(f"    Attributes: {attrs}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No data entities identified.")
    return lines


def _render_error_paths_section(error_paths) -> list[str]:
    lines = ["Error Paths:"]
    if error_paths:
        for ep in error_paths:
            ac_str = ", ".join(ep.ac_ids) if ep.ac_ids else "none"
            lines.append(f"  Condition: {ep.condition}")
            lines.append(f"    Exception: {ep.exception_type}")
            lines.append(f"    Handling: {ep.handling}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No error paths detected.")
    return lines


def _render_safety_notes_section(safety_notes) -> list[str]:
    lines = ["Safety Notes:"]
    if safety_notes:
        for note in safety_notes:
            lines.append(f"  - {note}")
    else:
        lines.append("  None.")
    return lines
