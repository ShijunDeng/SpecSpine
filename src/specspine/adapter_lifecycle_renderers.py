from __future__ import annotations

import json

from .adapter_models import (
    ADAPTER_SPECS,
    AdapterLifecycleReport,
)

__all__ = [
    "render_adapter_lifecycle_json",
    "render_adapter_lifecycle_text",
]


def render_adapter_lifecycle_json(report: AdapterLifecycleReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_adapter_lifecycle_text(report: AdapterLifecycleReport) -> str:
    summary = report.summary
    lines = [
        f"Adapter lifecycle mappings: {report.root}",
        (
            "Summary: "
            f"adapters={summary['adapters_total']} "
            f"enabled={summary['enabled_adapters']} "
            f"statuses={summary['statuses_total']} "
            f"mappings={summary['mappings_total']}"
        ),
    ]

    for key in ADAPTER_SPECS:
        adapter = report.adapters[key]
        enabled = "yes" if adapter.enabled else "no"
        config_exists = "yes" if adapter.config_exists else "no"
        lines.extend(
            [
                "",
                f"{adapter.display_name} ({key})",
                f"Enabled: {enabled}",
                f"Config: {adapter.config} (exists: {config_exists})",
                f"Upstream: {adapter.upstream_url}",
                "Mappings:",
            ]
        )
        for mapping in adapter.mappings:
            lines.append(
                f"- {mapping.id} {mapping.status} -> {mapping.upstream_phase}"
            )
            lines.append(f"  focus: {mapping.agent_focus}")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
