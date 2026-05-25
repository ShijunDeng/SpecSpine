from __future__ import annotations

from pathlib import Path
from typing import Any

from .validation_fusion_upstream_config import _enabled_upstream_configs
from .validation_fusion_utils import _check
from .validation_models import ValidationCheck

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
