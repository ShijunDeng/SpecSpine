from __future__ import annotations

from pathlib import Path

from .validation_models import AdapterProbe

__all__ = [
    "_run_feature_adapter_checks",
]


def _run_feature_adapter_checks(
    root: Path,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = None,
) -> list:
    from .validation_feature import _feature_bundle_checks
    from .validation_fusion import _adapter_availability_checks
    from .adapters import probe_adapters
    from .validation_models import ValidationCheck

    if adapter_probe is None:
        adapter_probe = probe_adapters

    checks: list[ValidationCheck] = []

    if include_features:
        checks.extend(_feature_bundle_checks(root))

    if include_adapters:
        checks.extend(_adapter_availability_checks(root, adapter_probe=adapter_probe))

    return checks
