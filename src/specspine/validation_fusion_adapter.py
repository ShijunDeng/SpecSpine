from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS
from .status import build_status, _read_yaml_section
from .validation_fusion_contract import _enabled_upstream_configs
from .validation_fusion_utils import _check
from .validation_models import ValidationCheck, AdapterProbe


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


__all__ = [
    "_adapter_availability_checks",
]
