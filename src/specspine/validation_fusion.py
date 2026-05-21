from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS, probe_adapters
from .features import list_feature_bundles
from .status import build_status, _read_yaml_section
from .validation_models import ValidationCheck, AdapterProbe

__all__ = [
    "_fusion_adapter_contract_checks",
    "_fusion_contract_checks",
    "_adapter_availability_checks",
]


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
    from .validation_models import VALIDATION_STATUSES
    if status not in VALIDATION_STATUSES:
        raise ValueError(f"Unsupported validation status: {status}")

    if severity is None:
        severity = {
            "fail": "error",
            "warn": "warning",
            "pass": "info",
            "skip": "info",
        }[status]

    return ValidationCheck(
        id=check_id,
        status=status,
        message=message,
        severity=severity,
    )


def _read_top_level_scalars(path: Path) -> dict[str, Any]:
    from .status import _clean_scalar
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    values: dict[str, Any] = {}
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent != 0 or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        value = value.strip()
        if value:
            values[key.strip()] = _clean_scalar(value)

    return values


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


def _adapter_availability_checks(
    root: Path,
    *,
    adapter_probe: AdapterProbe,
) -> list[ValidationCheck]:
    upstreams = _enabled_upstream_configs(root)
    enabled_keys = [key for key in sorted(upstreams) if upstreams[key]["enabled"]]
    statuses = {status.key: status for status in adapter_probe(enabled_keys)} if enabled_keys else {}

    checks: list[ValidationCheck] = []
    for key in sorted(upstreams):
        upstream = upstreams[key]
        if not upstream["enabled"]:
            checks.append(
                _check(
                    f"adapter.available:{key}",
                    "skip",
                    f"{upstream['display_name']} is disabled; external adapter probe was skipped.",
                )
            )
            continue

        status = statuses.get(key)
        if status is None:
            checks.append(
                _check(
                    f"adapter.available:{key}",
                    "fail",
                    f"{upstream['display_name']} adapter probe did not return a result.",
                )
            )
            continue

        checks.append(
            _check(
                f"adapter.available:{key}",
                "pass" if status.available else "fail",
                f"{status.display_name} external adapter is available: {status.detail}"
                if status.available
                else f"{status.display_name} external adapter is unavailable: {status.detail}",
            )
        )

    return checks
