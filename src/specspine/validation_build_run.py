from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS
from .fusion import FUSION_REQUIRED_FILES
from .validation_build_checks import (
    _file_checks,
    _workspace_placeholder_checks,
)
from .validation_models import ValidationCheck, AdapterProbe, WORKSPACE_PLACEHOLDER_PHRASES
from .workspace import BASE_WORKSPACE_FILES


def _run_checks(
    root: Path,
    include_fusion: bool = False,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = None,
) -> list[ValidationCheck]:
    from .validation_feature import _feature_bundle_checks
    from .validation_fusion import (
        _fusion_contract_checks,
        _fusion_adapter_contract_checks,
        _adapter_availability_checks,
    )
    from .adapters import probe_adapters

    if adapter_probe is None:
        adapter_probe = probe_adapters

    checks: list[ValidationCheck] = []

    checks.extend(
        _file_checks(
            root,
            required_files=BASE_WORKSPACE_FILES,
            prefix="workspace",
            label="Workspace",
        )
    )
    checks.extend(_workspace_placeholder_checks(root))

    if include_fusion:
        checks.extend(
            _file_checks(
                root,
                required_files=FUSION_REQUIRED_FILES,
                prefix="fusion",
                label="Fusion",
            )
        )
        checks.extend(_fusion_contract_checks(root))
        checks.extend(_fusion_adapter_contract_checks(root))

    if include_features:
        checks.extend(_feature_bundle_checks(root))

    if include_adapters:
        checks.extend(_adapter_availability_checks(root, adapter_probe=adapter_probe))

    return checks


__all__ = [
    "_run_checks",
]
