from __future__ import annotations

from pathlib import Path

from .validation_fusion_utils import _check, _read_top_level_scalars
from .validation_models import ValidationCheck

__all__ = [
    "_fusion_contract_checks",
]


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
