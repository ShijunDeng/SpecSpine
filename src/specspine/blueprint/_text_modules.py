from __future__ import annotations

__all__ = [
    "_render_modules_section",
]


def _render_modules_section(modules) -> list[str]:
    lines = ["Modules:"]
    if modules:
        for module in modules:
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
    return lines
