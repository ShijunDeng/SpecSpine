from __future__ import annotations

from pathlib import Path

from .validation_models import AdapterProbe

__all__ = [
    "_run_checks",
]


def _run_checks(
    root: Path,
    include_fusion: bool = False,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = None,
) -> list:
    from .fusion import FUSION_REQUIRED_FILES
    from .validation_build_checks import _file_checks
    from .validation_fusion import (
        _fusion_contract_checks,
        _fusion_adapter_contract_checks,
    )
    from .validation_models import ValidationCheck
    from ._validation_run_workspace import _run_workspace_checks
    from ._validation_run_feature_adapter import _run_feature_adapter_checks

    checks: list[ValidationCheck] = []

    checks.extend(_run_workspace_checks(root))

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

    checks.extend(
        _run_feature_adapter_checks(
            root,
            include_features=include_features,
            include_adapters=include_adapters,
            adapter_probe=adapter_probe,
        )
    )

    return checks
