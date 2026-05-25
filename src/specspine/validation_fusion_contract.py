from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS
from .status import build_status, _read_yaml_section
from .validation_fusion_utils import _check, _read_top_level_scalars
from .validation_models import ValidationCheck


def _fusion_contract_checks(root: Path) -> list[ValidationCheck]:
    fusion_path = root / ".specspine" / "fusion.yaml"
    if not fusion_path.exists():
        return [
            _check(
                "fusion.integration_mode",
                "skip",
                "fusion.yaml is missing, so integration_mode cannot be checked.",
            ),
            _check(
                "fusion.vendored_upstream_code",
                "skip",
                "fusion.yaml is missing, so vendored_upstream_code cannot be checked.",
            ),
        ]

    values = _read_top_level_scalars(fusion_path)
    integration_mode = values.get("integration_mode")
    vendored_upstream_code = values.get("vendored_upstream_code")
    checks: list[ValidationCheck] = []

    checks.append(
        _check(
            "fusion.integration_mode",
            "pass" if integration_mode == "adapter" else "fail",
            "fusion.yaml declares integration_mode: adapter."
            if integration_mode == "adapter"
            else "fusion.yaml must declare integration_mode: adapter.",
        )
    )
    checks.append(
        _check(
            "fusion.vendored_upstream_code",
            "pass" if vendored_upstream_code is False else "fail",
            "fusion.yaml declares vendored_upstream_code: false."
            if vendored_upstream_code is False
            else "fusion.yaml must declare vendored_upstream_code: false.",
        )
    )

    return checks


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


__all__ = [
    "_enabled_upstream_configs",
    "_fusion_adapter_contract_checks",
    "_fusion_contract_checks",
]
