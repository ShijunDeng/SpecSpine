from __future__ import annotations

from pathlib import Path
from typing import Any

from .validation_fusion_upstream_config import _enabled_upstream_configs
from .validation_fusion_utils import _check
from .validation_models import ValidationCheck
from ._upstream_enabled_checks import _handle_disabled_upstream
from ._upstream_file_checks import _check_adapter_config_exists
from ._upstream_boundary_checks import _check_adapter_boundary

__all__ = [
    "_fusion_adapter_contract_checks",
]


def _fusion_adapter_contract_checks(root: Path) -> list[ValidationCheck]:
    upstreams = _enabled_upstream_configs(root)
    checks: list[ValidationCheck] = []

    for key in sorted(upstreams):
        upstream = upstreams[key]
        adapter_path = upstream["config"]
        if not upstream["enabled"]:
            checks.extend(_handle_disabled_upstream(key, upstream))
            continue

        config_result = _check_adapter_config_exists(key, upstream, root)
        checks.append(config_result.check)

        if not config_result.passed:
            checks.extend(_handle_missing_config(key, upstream))
            continue

        try:
            content = config_result.target.read_text(encoding="utf-8").lower()
        except OSError:
            checks.append(
                _check(
                    f"fusion.adapter_boundary:{key}",
                    "fail",
                    f"{upstream['display_name']} adapter config could not be read: {adapter_path}",
                )
            )
            continue

        boundary_result = _check_adapter_boundary(key, upstream, content)
        checks.append(boundary_result)

    return checks
