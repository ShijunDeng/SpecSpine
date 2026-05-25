from __future__ import annotations

from typing import Any

from .text_markers import _marker

__all__ = [
    "_render_text_adapters",
    "_render_text_validation",
]


def _render_text_adapters(status: dict[str, Any], lines: list[str]) -> None:
    adapters = status.get("adapters")
    if adapters is not None:
        lines.append("External adapters:")
        for key, adapter in adapters.items():
            version = f" ({adapter['version']})" if adapter["version"] else ""
            lines.append(
                f"  [{_marker(adapter['available'])}] {key}: {adapter['display_name']}{version}"
            )
            lines.append(f"      {adapter['detail']}")


def _render_text_validation(status: dict[str, Any], lines: list[str]) -> None:
    validation = status.get("validation")
    if validation is not None:
        result = "ok" if validation["ok"] else "failed"
        summary = validation["summary"]
        lines.append("Validation:")
        lines.append(f"  Result: {result}")
        lines.append(
            "  Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"warn={summary['warn']} "
            f"skip={summary['skip']} "
            f"total={summary['total']}"
        )
        failed_checks = validation.get("failed_checks", [])
        if failed_checks:
            lines.append("  Failed checks:")
            for check in failed_checks:
                lines.append(f"    - {check['id']}")
        warning_checks = validation.get("warning_checks")
        if warning_checks is not None:
            lines.append("  Warning checks:")
            if warning_checks:
                for check in warning_checks:
                    lines.append(f"    - {check['id']}")
            else:
                lines.append("    none")
