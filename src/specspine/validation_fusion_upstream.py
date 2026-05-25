from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS
from .status import build_status, _read_yaml_section
from .validation_fusion_utils import _check
from .validation_models import ValidationCheck

__all__ = [
    "_enabled_upstream_configs",
    "_fusion_adapter_contract_checks",
]


def _enabled_upstream_configs(root: Path) -> dict[str, dict[str, Any]]:
    status = build_status(root)
    fusion_upstreams = _read_yaml_section(root / ".specspine" / "fusion.yaml", "upstreams")

    upstreams: dict[str, dict[str, Any]] = {}
    for key in ADAPTER_SPECS:
        status_config = status["upstreams"][key]
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = fusion_config.get("adapter", status_config["config"])
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", status_config["enabled"])
        if not isinstance(enabled, bool):
            enabled = False

        upstreams[key] = {
            "display_name": status_config["display_name"],
            "enabled": enabled,
            "config": adapter_path,
        }

    return upstreams


def _fusion_adapter_contract_checks(root: Path) -> list[ValidationCheck]:
    upstreams = _enabled_upstream_configs(root)
    checks: list[ValidationCheck] = []

    for key in sorted(upstreams):
        upstream = upstreams[key]
        adapter_path = upstream["config"]
        if not upstream["enabled"]:
            checks.append(
                _check(
                    f"fusion.adapter_config:{key}",
                    "skip",
                    f"{upstream['display_name']} is disabled; adapter config is not required.",
                )
            )
            checks.append(
                _check(
                    f"fusion.adapter_boundary:{key}",
                    "skip",
                    f"{upstream['display_name']} is disabled; adapter boundary docs are not required.",
                )
            )
            continue

        target = root / adapter_path
        if target.exists():
            checks.append(
                _check(
                    f"fusion.adapter_config:{key}",
                    "pass",
                    f"{upstream['display_name']} adapter config exists: {adapter_path}",
                )
            )
        else:
            checks.append(
                _check(
                    f"fusion.adapter_config:{key}",
                    "fail",
                    f"{upstream['display_name']} adapter config is missing: {adapter_path}",
                )
            )
            checks.append(
                _check(
                    f"fusion.adapter_boundary:{key}",
                    "skip",
                    f"{upstream['display_name']} adapter config is missing, so boundary docs cannot be checked.",
                )
            )
            continue

        try:
            content = target.read_text(encoding="utf-8").lower()
        except OSError:
            checks.append(
                _check(
                    f"fusion.adapter_boundary:{key}",
                    "fail",
                    f"{upstream['display_name']} adapter config could not be read: {adapter_path}",
                )
            )
            continue

        has_boundary = "no vendored source code" in content or "no vendored" in content
        checks.append(
            _check(
                f"fusion.adapter_boundary:{key}",
                "pass" if has_boundary else "fail",
                f"{upstream['display_name']} adapter docs state the no-vendored-code boundary."
                if has_boundary
                else f"{upstream['display_name']} adapter docs must state a no-vendored-code boundary.",
            )
        )

    return checks
