from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapter_models import (
    ADAPTER_LIFECYCLE_MAPPINGS,
    ADAPTER_SPECS,
    AdapterLifecycleAdapter,
    AdapterLifecycleReport,
)
from .features import FEATURE_STATUSES

__all__ = [
    "build_adapter_lifecycle_report",
    "render_adapter_lifecycle_json",
    "render_adapter_lifecycle_text",
]


def _clean_config_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_fusion_upstreams(content: str) -> dict[str, dict[str, Any]]:
    upstreams: dict[str, dict[str, Any]] = {}
    in_upstreams = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_upstreams = stripped == "upstreams:"
            current_key = None
            continue

        if not in_upstreams:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            upstreams.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            upstreams[current_key][key.strip()] = _clean_config_scalar(value)

    return upstreams


def _read_fusion_upstreams(root: Path) -> dict[str, dict[str, Any]]:
    fusion_path = root / ".specspine" / "fusion.yaml"
    if not fusion_path.exists():
        return {}

    try:
        return _parse_fusion_upstreams(fusion_path.read_text(encoding="utf-8"))
    except OSError:
        return {}


def _adapter_lifecycle_recommended_commands() -> tuple[str, ...]:
    return (
        "specspine status . --json --validate",
        "specspine adapters doctor",
        "specspine validate . --fusion --features",
    )


def build_adapter_lifecycle_report(root: Path) -> AdapterLifecycleReport:
    resolved_root = root.expanduser().resolve()
    fusion_upstreams = _read_fusion_upstreams(resolved_root)
    adapters: dict[str, AdapterLifecycleAdapter] = {}

    for key, spec in ADAPTER_SPECS.items():
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = fusion_config.get("adapter")
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", False)
        if not isinstance(enabled, bool):
            enabled = False

        adapters[key] = AdapterLifecycleAdapter(
            key=key,
            display_name=spec.display_name,
            enabled=enabled,
            config=adapter_path,
            config_exists=(resolved_root / adapter_path).exists(),
            upstream_url=spec.upstream_url,
            mappings=ADAPTER_LIFECYCLE_MAPPINGS[key],
        )

    return AdapterLifecycleReport(
        root=resolved_root,
        native_statuses=FEATURE_STATUSES,
        adapters=adapters,
        recommended_commands=_adapter_lifecycle_recommended_commands(),
    )


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
